"""Offline evaluator regressions: preserve evidence and avoid automatic paid retries."""
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src import m4_eval
from src.m4_eval import evaluate_ragas

pytestmark = pytest.mark.student


@pytest.fixture
def fake_ragas(monkeypatch, tmp_path):
    monkeypatch.setattr(m4_eval, "EVALUATOR_CACHE_DIR", str(tmp_path / "cache"))
    row = {"question": "Question", "answer": "Saved answer", "contexts": ["Context"],
           "ground_truth": "Reference", "faithfulness": .8, "answer_relevancy": .7,
           "context_precision": .6, "context_recall": .5}

    class Frame:
        rows = [row]

        def __len__(self):
            return len(self.rows)

        def iterrows(self):
            return enumerate(self.rows)

    class Evaluation(dict):
        def to_pandas(self):
            return frame

    frame = Frame()
    evaluation = Evaluation({name: row[name] for name in
                             ("faithfulness", "answer_relevancy", "context_precision", "context_recall")})
    evaluate = Mock(return_value=evaluation)
    llm = Mock(side_effect=lambda **kwargs: SimpleNamespace(model_name=kwargs["model"]))
    embedding = Mock(side_effect=lambda **kwargs: SimpleNamespace(model=kwargs["model"]))
    modules = {
        "datasets": SimpleNamespace(Dataset=SimpleNamespace(from_dict=Mock(return_value="dataset"))),
        "langchain.embeddings": SimpleNamespace(CacheBackedEmbeddings=SimpleNamespace(
            from_bytes_store=Mock(side_effect=lambda model, store, **kwargs: model))),
        "langchain.storage": SimpleNamespace(LocalFileStore=Mock()),
        "langchain_community.cache": SimpleNamespace(SQLiteCache=Mock()),
        "langchain_openai": SimpleNamespace(ChatOpenAI=llm, OpenAIEmbeddings=embedding),
        "ragas": SimpleNamespace(evaluate=evaluate),
        "ragas.llms.base": SimpleNamespace(LangchainLLMWrapper=lambda model, **kwargs:
                                          SimpleNamespace(langchain_llm=model)),
        "ragas.embeddings.base": SimpleNamespace(LangchainEmbeddingsWrapper=lambda model, **kwargs:
                                                SimpleNamespace(embeddings=model)),
        "ragas.metrics": SimpleNamespace(**{name: Mock(return_value=SimpleNamespace(name=name))
                                            for name in ("Faithfulness", "AnswerRelevancy",
                                                         "ContextPrecision", "ContextRecall")}),
        "ragas.run_config": SimpleNamespace(RunConfig=lambda **kwargs: SimpleNamespace(**kwargs)),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    return SimpleNamespace(row=row, frame=frame, evaluate=evaluate, llm=llm, embedding=embedding)


def test_evaluator_uses_one_batch_and_inexpensive_models_without_transport_retries(fake_ragas):
    result = evaluate_ragas(["Question"], ["Saved answer"], [["Context"]], ["Reference"])
    fake_ragas.evaluate.assert_called_once()
    options = fake_ragas.evaluate.call_args.kwargs
    assert len(options["metrics"]) == 4
    assert options["raise_exceptions"] is True
    assert options["run_config"].max_retries == 1
    assert options["run_config"].max_workers == 2
    assert fake_ragas.llm.call_args.kwargs["model"] == "gpt-4o-mini"
    assert fake_ragas.embedding.call_args.kwargs["model"] == "text-embedding-3-small"
    assert fake_ragas.llm.call_args.kwargs["max_retries"] == 0
    assert "response_format" not in fake_ragas.llm.call_args.kwargs.get("model_kwargs", {})
    assert fake_ragas.embedding.call_args.kwargs["max_retries"] == 0
    assert result["metadata"]["evaluator_models"] == ["gpt-4o-mini", "text-embedding-3-small"]
    assert result["per_question"][0].answer == "Saved answer"
    assert result["per_question"][0].ground_truth == "Reference"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), 1.1])
def test_evaluator_rejects_invalid_scores_instead_of_manufacturing_zero(fake_ragas, value):
    fake_ragas.row["faithfulness"] = value
    with pytest.raises(ValueError, match="invalid metric scores"):
        evaluate_ragas(["Question"], ["Saved answer"], [["Context"]], ["Reference"])


def test_evaluator_propagates_api_failure_without_replaying_batch(fake_ragas):
    fake_ragas.evaluate.side_effect = RuntimeError("API unavailable")
    with pytest.raises(RuntimeError, match="API unavailable"):
        evaluate_ragas(["Question"], ["Saved answer"], [["Context"]], ["Reference"])
    fake_ragas.evaluate.assert_called_once()


def test_evaluator_rejects_incomplete_result_rows(fake_ragas):
    fake_ragas.frame.rows = []
    with pytest.raises(ValueError, match="incomplete"):
        evaluate_ragas(["Question"], ["Saved answer"], [["Context"]], ["Reference"])


@pytest.mark.parametrize("answers", [[], ["A", "B"]])
def test_evaluator_checks_input_lengths_before_any_api_call(fake_ragas, answers):
    with pytest.raises(ValueError, match="equal lengths"):
        evaluate_ragas(["Question"], answers, [["Context"]], ["Reference"])
    fake_ragas.evaluate.assert_not_called()


def test_evaluator_rejects_empty_input_before_any_api_call(fake_ragas):
    with pytest.raises(ValueError, match="at least one question"):
        evaluate_ragas([], [], [], [])
    fake_ragas.evaluate.assert_not_called()
