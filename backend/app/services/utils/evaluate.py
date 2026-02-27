from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase
import mlflow


@mlflow.trace
def evaluate_rag(query, model, context_chunks, answer, expected_answer):

    context_text = [c["text"] for c in context_chunks]

    test_case = LLMTestCase(
        input=query,
        actual_output=answer,
        expected_output=expected_answer,
        retrieval_context=context_text,
    )

    # Metrics
    answer_relevancy = AnswerRelevancyMetric(model=model)
    faithfulness = FaithfulnessMetric(model=model)
    precision = ContextualPrecisionMetric(model=model)
    recall = ContextualRecallMetric(model=model)

    # Measure
    answer_relevancy.measure(test_case)
    faithfulness.measure(test_case)
    precision.measure(test_case)
    recall.measure(test_case)

    return {
        "answer_relevancy": answer_relevancy.score,
        "faithfulness": faithfulness.score,
        "precision_at_k": precision.score,
        "recall_at_k": recall.score,
    }
