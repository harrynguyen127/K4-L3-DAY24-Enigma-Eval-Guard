"""Student contracts; no RAGAS API calls."""
from types import SimpleNamespace
import sys
from unittest.mock import Mock

import pytest

from src.phase_a_ragas import (load_test_set_50q, group_by_distribution, run_ragas_50q,
                               bottom_10, cluster_analysis, RagasResult)

pytestmark = pytest.mark.student


@pytest.fixture
def dummy_results():
    return [RagasResult(i+1, dist, f"Q{i}", "A", ["C"], "GT", *scores)
            for i, (dist, scores) in enumerate([
                ("factual", (.9,.8,.7,.6)), ("multi_hop", (.3,.4,.5,.2)),
                ("adversarial", (.1,.2,.3,.4)), ("factual", (.8,.7,.9,.8)),
                ("multi_hop", (.2,.3,.1,.2))])]


def test_group_exact_counts():
    groups = group_by_distribution(load_test_set_50q())
    assert set(groups) == {"factual","multi_hop","adversarial"}
    assert [len(groups[d]) for d in ("factual","multi_hop","adversarial")] == [20,20,10]


def test_ragas_adapter_preserves_rows(monkeypatch):
    questions = load_test_set_50q()
    answers = [{**q, "answer": "A", "contexts": ["C"]} for q in questions]
    metrics = [SimpleNamespace(faithfulness=.8, answer_relevancy=.7,
                               context_precision=.6, context_recall=.5) for _ in answers]
    evaluator_models = ["evaluator-test", "embedding-test"]
    evaluate = Mock(return_value={"per_question": metrics,
                                  "metadata": {"evaluator_models": evaluator_models}})
    monkeypatch.setitem(sys.modules, "src.m4_eval", SimpleNamespace(evaluate_ragas=evaluate))
    evaluation = run_ragas_50q(answers)
    results = evaluation.results
    assert evaluation.evaluator_models == evaluator_models
    assert len(results) == 50
    assert [r.question_id for r in results] == [q["id"] for q in questions]
    assert results[0].faithfulness == .8
    evaluate.assert_called_once()
    assert list(evaluate.call_args.args[0]) == [q["question"] for q in questions]


def test_bottom_nonempty_sorted_complete(dummy_results):
    rows = bottom_10(dummy_results)
    assert len(rows) == 5
    assert [r["rank"] for r in rows] == [1,2,3,4,5]
    assert [r["avg_score"] for r in rows] == sorted(r["avg_score"] for r in rows)
    assert rows[0]["question_id"] == 5
    for row in rows:
        assert {"question_id","distribution","question","worst_metric",
                "diagnosis","suggested_fix"} <= row.keys()
        assert row["diagnosis"].strip() and row["suggested_fix"].strip()


def test_bottom_capped_at_ten(dummy_results):
    repeated = [RagasResult(i+1,r.distribution,r.question,r.answer,r.contexts,r.ground_truth,
                           r.faithfulness,r.answer_relevancy,r.context_precision,r.context_recall)
                for i,r in enumerate(dummy_results*4)]
    assert len(bottom_10(repeated)) == 10


def test_cluster_matrix(dummy_results):
    result = cluster_analysis(dummy_results)
    assert result["matrix"] == {
        "faithfulness":{"factual":0,"multi_hop":0,"adversarial":1},
        "answer_relevancy":{"factual":1,"multi_hop":0,"adversarial":0},
        "context_precision":{"factual":0,"multi_hop":1,"adversarial":0},
        "context_recall":{"factual":1,"multi_hop":1,"adversarial":0}}
    assert result["dominant_failure_metric"] == "context_recall"
    assert result["insight"].strip()


def test_weakest_distribution_is_quality_not_size():
    results = []
    for dist,count,value in [("factual",20,.95),("multi_hop",20,.70),("adversarial",10,.10)]:
        for _ in range(count):
            results.append(RagasResult(len(results)+1,dist,"Q","A",["C"],"GT",
                                       value,value,value,value))
    assert cluster_analysis(results)["dominant_failure_distribution"] == "adversarial"


@pytest.fixture
def adapter_input():
    return [{**q, "answer": f"Saved answer {q['id']}", "contexts": [f"Context {q['id']}"]}
            for q in load_test_set_50q()]


@pytest.fixture
def evaluator_payload(adapter_input, monkeypatch):
    payload = {
        "per_question": [{"faithfulness": .8, "answer_relevancy": .7,
                          "context_precision": .6, "context_recall": .5}
                         for _ in adapter_input],
        "metadata": {"evaluator_models": ["actual-evaluator", "actual-embedding"]},
    }
    evaluate = Mock(return_value=payload)
    monkeypatch.setitem(sys.modules, "src.m4_eval", SimpleNamespace(evaluate_ragas=evaluate))
    return payload, evaluate


def test_adapter_passes_saved_answers_contexts_and_references_separately(adapter_input, evaluator_payload):
    _, evaluate = evaluator_payload
    results = run_ragas_50q(adapter_input).results
    assert evaluate.call_args.args == tuple(
        [row[field] for row in adapter_input]
        for field in ("question", "answer", "contexts", "ground_truth"))
    assert results[0].answer == "Saved answer 1"
    assert results[0].ground_truth == adapter_input[0]["ground_truth"]
    assert type(results[0].faithfulness) is float


@pytest.mark.parametrize("row_count", [0, 49, 51])
def test_adapter_rejects_missing_or_extra_evaluation_rows(adapter_input, evaluator_payload, row_count):
    payload, _ = evaluator_payload
    payload["per_question"] = [payload["per_question"][0]] * row_count
    with pytest.raises(ValueError, match="exactly 50"):
        run_ragas_50q(adapter_input)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -.01, 1.01, True, None])
def test_adapter_rejects_invalid_metric_scores(adapter_input, evaluator_payload, value):
    payload, _ = evaluator_payload
    payload["per_question"][0]["faithfulness"] = value
    with pytest.raises(ValueError, match="faithfulness"):
        run_ragas_50q(adapter_input)


@pytest.mark.parametrize("models", [None, [], "guessed-model", [""], [123]])
def test_adapter_requires_actual_evaluator_models(adapter_input, evaluator_payload, models):
    payload, _ = evaluator_payload
    payload["metadata"]["evaluator_models"] = models
    with pytest.raises(ValueError, match="actual evaluator_models"):
        run_ragas_50q(adapter_input)


def test_adapter_rejects_reordered_source_rows(adapter_input, evaluator_payload):
    payload, _ = evaluator_payload
    payload["per_question"][0]["question"] = adapter_input[1]["question"]
    with pytest.raises(ValueError, match="does not match the source row"):
        run_ragas_50q(adapter_input)


def test_adapter_rejects_duplicate_ids_before_calling_evaluator(adapter_input, evaluator_payload):
    _, evaluate = evaluator_payload
    adapter_input[1]["id"] = adapter_input[0]["id"]
    with pytest.raises(ValueError, match="distinct positive question IDs"):
        run_ragas_50q(adapter_input)
    evaluate.assert_not_called()


def test_adapter_rejects_wrong_distribution_counts_before_evaluation(adapter_input, evaluator_payload):
    _, evaluate = evaluator_payload
    adapter_input[0]["distribution"] = "adversarial"
    with pytest.raises(ValueError, match="20/20/10"):
        run_ragas_50q(adapter_input)
    evaluate.assert_not_called()


def test_group_rejects_unknown_distribution():
    with pytest.raises(ValueError, match="Unknown distribution"):
        group_by_distribution([{"distribution": "unknown"}])


def test_empty_results_have_no_invented_weakest_group():
    assert bottom_10([]) == []
    clusters = cluster_analysis([])
    assert clusters["distribution_avg_scores"] == {}
    assert clusters["dominant_failure_distribution"] is None
    assert clusters["dominant_failure_metric"] is None
    assert all(count == 0 for row in clusters["matrix"].values() for count in row.values())


def test_empty_distributions_are_excluded_from_quality_comparison(dummy_results):
    factual = [result for result in dummy_results if result.distribution == "factual"]
    clusters = cluster_analysis(factual)
    assert set(clusters["distribution_avg_scores"]) == {"factual"}
    assert clusters["dominant_failure_distribution"] == "factual"
