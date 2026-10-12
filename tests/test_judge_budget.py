"""Offline regressions for paid-request limits, cache provenance and partial-batch reuse."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.experiment_support import judge_binary, judge_json, judge_session
from src.phase_b_judge import _validate_pairwise

pytestmark = pytest.mark.support


@pytest.fixture
def client():
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(
            {"winner": "A", "reasoning": "Supported by reference", "scores": {"A": .9, "B": .2}})))],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))
    return client


def test_cached_response_does_not_consume_request_budget(tmp_path, client):
    with judge_session(client, tmp_path, max_requests=1) as session:
        first = judge_json("Judge prompt", {"answer": "A"}, validator=_validate_pairwise)
        assert judge_json("Judge prompt", {"answer": "A"}, validator=_validate_pairwise) == first
        with pytest.raises(ValueError, match="budget exhausted"):
            judge_json("Judge prompt", {"answer": "B"}, validator=_validate_pairwise)
    client.chat.completions.create.assert_called_once()
    assert session.api_requests == 1 and session.cache_hits == 1
    assert session.prompt_tokens == 10 and session.completion_tokens == 5


def test_new_session_reuses_completed_call_without_api_replay(tmp_path, client):
    with judge_session(client, tmp_path):
        first = judge_json("Judge prompt", {"answer": "A"}, validator=_validate_pairwise)
    with judge_session(client, tmp_path) as resumed:
        assert judge_json("Judge prompt", {"answer": "A"}, validator=_validate_pairwise) == first
    client.chat.completions.create.assert_called_once()
    assert resumed.api_requests == 0 and resumed.cache_hits == 1


def test_swapped_candidates_and_changed_prompt_use_distinct_cache_keys(tmp_path, client):
    with judge_session(client, tmp_path, max_requests=3) as session:
        judge_json("Prompt", {"answer_a": "A", "answer_b": "B"}, validator=_validate_pairwise)
        judge_json("Prompt", {"answer_a": "B", "answer_b": "A"}, validator=_validate_pairwise)
        judge_json("Changed prompt", {"answer_a": "A", "answer_b": "B"}, validator=_validate_pairwise)
    assert client.chat.completions.create.call_count == 3
    assert session.cache_hits == 0 and len(list(tmp_path.glob("*.json"))) == 3


def test_invalid_output_is_not_cached_or_retried(tmp_path, client):
    client.chat.completions.create.return_value.choices[0].message.content = '{"winner":"C"}'
    with judge_session(client, tmp_path):
        with pytest.raises(ValueError):
            judge_json("Prompt", {"answer": "A"}, validator=_validate_pairwise)
    client.chat.completions.create.assert_called_once()
    assert not list(tmp_path.glob("*.json"))


def test_sdk_failure_is_propagated_without_retries(tmp_path, client):
    client.chat.completions.create.side_effect = RuntimeError("API unavailable")
    with judge_session(client, tmp_path):
        with pytest.raises(RuntimeError, match="API unavailable"):
            judge_json("Prompt", {"answer": "A"}, validator=_validate_pairwise)
    client.chat.completions.create.assert_called_once()
    assert not list(tmp_path.glob("*.json"))


def test_cached_response_is_revalidated_before_use(tmp_path, client):
    with judge_session(client, tmp_path):
        judge_json("Prompt", {"answer": "A"}, validator=_validate_pairwise)
    path = next(tmp_path.glob("*.json"))
    cached = json.loads(path.read_text(encoding="utf-8"))
    cached["result"]["winner"] = "C"
    path.write_text(json.dumps(cached), encoding="utf-8")
    with judge_session(client, tmp_path):
        with pytest.raises(ValueError):
            judge_json("Prompt", {"answer": "A"}, validator=_validate_pairwise)
    client.chat.completions.create.assert_called_once()


def test_binary_call_in_session_has_only_question_answer_reference(tmp_path, client):
    client.chat.completions.create.return_value.choices[0].message.content = '{"label":1,"reasoning":"Supported"}'
    with judge_session(client, tmp_path):
        assert judge_binary("Question", "Supplied answer", "Reference", client=client)["label"] == 1
    request = client.chat.completions.create.call_args.kwargs
    assert json.loads(request["messages"][1]["content"]) == {
        "question": "Question", "answer": "Supplied answer", "reference": "Reference"}
    assert "human_label" not in str(request) and "human_note" not in str(request)
