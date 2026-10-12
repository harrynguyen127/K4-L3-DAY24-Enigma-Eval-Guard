"""Student guards use injected fake engines/rails; no spaCy download or live API."""
import asyncio
import re
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock,Mock

import pytest

from config import ADVERSARIAL_SET_PATH,CLEAN_SET_PATH
from src import phase_c_guard as phase
from src.experiment_support import read_json
from src.report_contracts import validate_input_results,validate_latency

pytestmark = pytest.mark.student


@pytest.fixture
def pii_engines():
    def analyze(*,text,language):
        rows=[]
        for kind,pattern in [("VN_CCCD",r"\b(?:\d{12}|\d{9})\b"),
                             ("VN_PHONE",r"\b0[3-9]\d{8}\b"),
                             ("EMAIL_ADDRESS",r"[\w.]+@[\w.]+")]:
            for match in re.finditer(pattern,text):
                rows.append(SimpleNamespace(entity_type=kind,start=match.start(),
                                            end=match.end(),score=.9))
        return rows
    def anonymize(*,text,analyzer_results):
        for row in sorted(analyzer_results,key=lambda r:r.start,reverse=True):
            text=text[:row.start]+"<"+row.entity_type+">"+text[row.end:]
        return SimpleNamespace(text=text)
    return SimpleNamespace(analyze=Mock(side_effect=analyze)),SimpleNamespace(anonymize=Mock(side_effect=anonymize))


@pytest.mark.parametrize("text,kind", [
    ("CCCD 034095001234.","VN_CCCD"),("CMND 012345678.","VN_CCCD"),
    ("Call 0987654321.","VN_PHONE"),("Email test@company.com","EMAIL_ADDRESS")])
def test_pii_detect_and_redact(pii_engines,text,kind):
    result=phase.pii_scan(text,*pii_engines)
    assert result["has_pii"] is True
    assert kind in [r["type"] for r in result["entities"]]
    assert result["anonymized"] != text
    pii_engines[0].analyze.assert_called_once()


def test_pii_clean(pii_engines):
    text="Policy 2024."
    result=phase.pii_scan(text,*pii_engines)
    assert result=={"has_pii":False,"entities":[],"anonymized":text}
    pii_engines[0].analyze.assert_called_once()


def test_pii_scope_ignores_english_ner_guesses():
    person = SimpleNamespace(entity_type="PERSON", start=0, end=6, score=.9)
    identifier = SimpleNamespace(entity_type="VN_CCCD", start=7, end=19, score=.9)
    analyzer = SimpleNamespace(analyze=Mock(return_value=[person, identifier]))
    anonymizer = SimpleNamespace(anonymize=Mock(return_value=SimpleNamespace(text="Policy <VN_CCCD>")))
    result = phase.pii_scan("Policy 034095001234", analyzer, anonymizer)
    assert [row["type"] for row in result["entities"]] == ["VN_CCCD"]
    assert anonymizer.anonymize.call_args.kwargs["analyzer_results"] == [identifier]
    analyzer.analyze.return_value = [person]
    assert phase.pii_scan("Policy", analyzer, anonymizer)["has_pii"] is False


def test_presidio_factory_registers_both_vietnamese_recognizers(monkeypatch):
    registry = Mock()
    analyzer_factory, anonymizer_factory = Mock(), Mock()
    monkeypatch.setitem(sys.modules, "presidio_analyzer", SimpleNamespace(
        AnalyzerEngine=analyzer_factory, RecognizerRegistry=Mock(return_value=registry),
        Pattern=Mock(), PatternRecognizer=lambda **kwargs: SimpleNamespace(**kwargs)))
    monkeypatch.setitem(sys.modules, "presidio_anonymizer", SimpleNamespace(
        AnonymizerEngine=anonymizer_factory))
    phase.setup_presidio()
    registry.load_predefined_recognizers.assert_called_once()
    assert {call.args[0].supported_entity for call in registry.add_recognizer.call_args_list} == {
        "VN_CCCD", "VN_PHONE"}
    analyzer_factory.assert_called_once_with(registry=registry)


def test_guard_execution_records_counters_without_prompts():
    counters = dict(checks=0, llm_calls=0, prompt_tokens=0, completion_tokens=0)
    rails = SimpleNamespace(_guard_execution=counters)
    result = SimpleNamespace(log=SimpleNamespace(stats=SimpleNamespace(
        llm_calls_count=1, llm_calls_total_prompt_tokens=120,
        llm_calls_total_completion_tokens=1)))
    phase._record_guard_execution(rails, result)
    assert counters == dict(checks=1, llm_calls=1, prompt_tokens=120, completion_tokens=1)


def test_nemo_provider_override_preserves_actual_model_and_no_retries(monkeypatch):
    config = SimpleNamespace(models=[SimpleNamespace(type="main", model="gpt-4o-mini")])
    rails = SimpleNamespace(config=config)
    llm_factory, rails_factory = Mock(), Mock(return_value=rails)
    monkeypatch.setitem(sys.modules, "nemoguardrails", SimpleNamespace(
        RailsConfig=SimpleNamespace(from_path=lambda path:config), LLMRails=rails_factory))
    monkeypatch.setitem(sys.modules, "langchain_openai", SimpleNamespace(ChatOpenAI=llm_factory))
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")
    result = phase.setup_nemo_rails()
    assert result.config.models[0].model == "deepseek-chat"
    params = llm_factory.call_args.kwargs
    assert params["model"] == "deepseek-chat"
    assert params["max_retries"] == 0 and params["cache"] is False
    rails_factory.assert_called_once_with(config, llm=llm_factory.return_value)


@pytest.mark.parametrize("blocked",[True,False])
def test_input_uses_rail_decision(blocked):
    result=SimpleNamespace(response=[{"role":"assistant","content":"policy response"}],
                           log=SimpleNamespace(activated_rails=[SimpleNamespace(stop=blocked)]))
    rails=SimpleNamespace(generate_async=AsyncMock(return_value=result))
    actual=asyncio.run(phase.check_input_rail("Xin lỗi, tôi không thể đi làm; nghỉ phép thế nào?",rails))
    assert actual["allowed"] is (not blocked)
    assert actual["response"] == "policy response"
    rails.generate_async.assert_awaited_once()
    assert rails.generate_async.call_args.kwargs["options"]["rails"] == ["input"]


@pytest.mark.parametrize("blocked",[True,False])
def test_output_checks_supplied_answer(blocked):
    response="refusal" if blocked else "answer"
    returned=SimpleNamespace(response=[{"content":response}],
                             log=SimpleNamespace(activated_rails=[SimpleNamespace(stop=blocked)]))
    rails=SimpleNamespace(generate_async=AsyncMock(return_value=returned))
    result=asyncio.run(phase.check_output_rail("question","answer",rails))
    assert result["safe"] is (not blocked)
    assert result["final_answer"]==response
    assert rails.generate_async.call_args.kwargs["messages"][-1]["content"]=="answer"
    assert rails.generate_async.call_args.kwargs["options"]["rails"]==["output"]


@pytest.fixture(scope="module")
def guard_batch():
    patch=pytest.MonkeyPatch()
    attacks,clean=read_json(ADVERSARIAL_SET_PATH),read_json(CLEAN_SET_PATH)
    clean_texts={row["input"] for row in clean}
    patch.setattr(phase,"pii_scan",Mock(side_effect=lambda text,*args: {
        "has_pii":bool(re.search(r"\b\d{9,12}\b|@",text)),"entities":[],"anonymized":text}))
    rail=AsyncMock(side_effect=lambda text,*args:{
        "allowed":text in clean_texts,"blocked_reason":None if text in clean_texts else "nemo_input",
        "response":"response"})
    patch.setattr(phase,"check_input_rail",rail)
    try:
        yield phase.run_adversarial_suite(attacks+clean,rails=object(),analyzer=object(),anonymizer=object()),attacks+clean,rail
    finally:
        patch.undo()


def test_input_suite_exact_rows(guard_batch):
    rows,source,_=guard_batch
    validate_input_results(rows,source)
    assert len(rows)==28


def test_attack_and_clean_control(guard_batch):
    rows,source,rail=guard_batch
    assert len(rows)==28 and all(row["passed"] for row in rows)
    assert sum(row["actual"]=="allowed" for row in rows)==8
    assert rail.await_count==24  # four attacks stopped at PII; 8 clean + 16 other attacks


def test_latency_real_warmup_and_sample_count(monkeypatch):
    pii=Mock(return_value={"has_pii":False,"entities":[],"anonymized":"clean"})
    nemo=AsyncMock(return_value={"allowed":True,"blocked_reason":None,"response":"clean"})
    monkeypatch.setattr(phase,"pii_scan",pii)
    monkeypatch.setattr(phase,"check_input_rail",nemo)
    monkeypatch.setattr(phase.time,"perf_counter",Mock(side_effect=[i*.002 for i in range(100)]))
    result=phase.measure_p95_latency(["clean"],n_runs=20,rails=object(),analyzer=object(),anonymizer=object())
    validate_latency(result)
    assert pii.call_count==22 and nemo.await_count==22
    assert result["input_guard_ms"]["p95"]==pytest.approx(4)
