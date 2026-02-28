from unittest.mock import patch, MagicMock
from app.services.utils.evaluate import evaluate_rag


@patch("app.services.utils.evaluate.ContextualRecallMetric")
@patch("app.services.utils.evaluate.ContextualPrecisionMetric")
@patch("app.services.utils.evaluate.FaithfulnessMetric")
@patch("app.services.utils.evaluate.AnswerRelevancyMetric")
def test_evaluate_rag(
    mock_answer_relevancy,
    mock_faithfulness,
    mock_precision,
    mock_recall,
):

    # Create metric instances
    mock_ar_instance = MagicMock()
    mock_f_instance = MagicMock()
    mock_p_instance = MagicMock()
    mock_r_instance = MagicMock()

    mock_answer_relevancy.return_value = mock_ar_instance
    mock_faithfulness.return_value = mock_f_instance
    mock_precision.return_value = mock_p_instance
    mock_recall.return_value = mock_r_instance

    # Fake scores
    mock_ar_instance.score = 0.9
    mock_f_instance.score = 0.8
    mock_p_instance.score = 0.7
    mock_r_instance.score = 0.6

    query = "What is AI?"

    context_chunks = [
        {"text": "AI stands for artificial intelligence"},
        {"text": "Machine learning is a subfield of AI"},
    ]

    answer = "AI means artificial intelligence."
    expected_answer = "Artificial intelligence"

    result = evaluate_rag(
        query=query,
        model="fake-model",
        context_chunks=context_chunks,
        answer=answer,
        expected_answer=expected_answer,
    )

    assert result == {
        "answer_relevancy": 0.9,
        "faithfulness": 0.8,
        "precision_at_k": 0.7,
        "recall_at_k": 0.6,
    }

    # verify measure called
    assert mock_ar_instance.measure.called
    assert mock_f_instance.measure.called
    assert mock_p_instance.measure.called
    assert mock_r_instance.measure.called
