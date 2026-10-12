from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import json
import math
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ARTIFACTS_DIR, TEST_SET_PATH

EVALUATOR_LLM_MODEL = "gpt-4o-mini"
EVALUATOR_EMBEDDING_MODEL = "text-embedding-3-small"
EVALUATOR_CACHE_DIR = os.path.join(ARTIFACTS_DIR, ".phase_a_cache")
METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Evaluate saved answers once using inexpensive models and no transport retries.

    Errors are propagated instead of replacing failed evaluations with zero scores.
    Keep answer-relevancy's standard three generated questions in one completion call.
    """
    if not (len(questions) == len(answers) == len(contexts) == len(ground_truths)):
        raise ValueError("Questions, answers, contexts and ground truths must have equal lengths")
    if not questions:
        raise ValueError("RAGAS evaluation needs at least one question")

    from datasets import Dataset
    from langchain.embeddings import CacheBackedEmbeddings
    from langchain.storage import LocalFileStore
    from langchain_community.cache import SQLiteCache
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas import evaluate
    from ragas.embeddings.base import LangchainEmbeddingsWrapper
    from ragas.llms.base import LangchainLLMWrapper
    from ragas.metrics import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness
    from ragas.run_config import RunConfig

    dataset = Dataset.from_dict({
        "question": questions, "answer": answers,
        "contexts": contexts, "ground_truth": ground_truths,
    })
    # RAGAS max_retries is a total attempt count: 1 means no automatic retry.
    run_config = RunConfig(timeout=120, max_retries=1, max_workers=2)
    os.makedirs(EVALUATOR_CACHE_DIR, exist_ok=True)
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(
        model=EVALUATOR_LLM_MODEL, max_retries=0, timeout=120,
        cache=SQLiteCache(database_path=os.path.join(EVALUATOR_CACHE_DIR, "llm.sqlite")),
    ), run_config=run_config)
    underlying_embeddings = OpenAIEmbeddings(
        model=EVALUATOR_EMBEDDING_MODEL, max_retries=0, request_timeout=120,
    )
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings, LocalFileStore(os.path.join(EVALUATOR_CACHE_DIR, "embeddings")),
        namespace=underlying_embeddings.model, query_embedding_cache=True,
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(cached_embeddings, run_config=run_config)
    metrics = [Faithfulness(max_retries=0), AnswerRelevancy(),
               ContextPrecision(max_retries=0), ContextRecall(max_retries=0)]
    result = evaluate(dataset, metrics=metrics, llm=evaluator_llm,
                      embeddings=evaluator_embeddings, run_config=run_config,
                      raise_exceptions=True)
    df = result.to_pandas()
    if len(df) != len(questions):
        raise ValueError("RAGAS returned incomplete per-question results")
    per_question = []
    for _, row in df.iterrows():
        scores = {metric: float(row[metric]) for metric in METRICS}
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in scores.values()):
            raise ValueError("RAGAS returned invalid metric scores; no submission report was written")
        per_question.append(EvalResult(
            question=row["question"], answer=row["answer"],
            contexts=list(row["contexts"]), ground_truth=row["ground_truth"], **scores,
        ))
    return {
        **{metric: float(result[metric]) for metric in METRICS},
        "per_question": per_question,
        "metadata": {"evaluator_models": sorted({
            evaluator_llm.langchain_llm.model_name, underlying_embeddings.model,
        })},
    }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N questions by mean metric score using Diagnostic Tree."""
    if not eval_results or bottom_n <= 0:
        return []

    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
    }
    failures = []
    for result in eval_results:
        metrics = {name: getattr(result, name) for name in diagnostic_tree}
        average_score = sum(metrics.values()) / len(metrics)
        worst_metric = min(metrics, key=metrics.get)
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        failures.append({
            "question": result.question,
            "worst_metric": worst_metric,
            "score": average_score,
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })

    return sorted(failures, key=lambda failure: failure["score"])[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
