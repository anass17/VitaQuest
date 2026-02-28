from unittest.mock import patch, MagicMock
from app.services.utils.rerank import chunks_reranker


@patch("app.services.utils.rerank.CrossEncoder")
def test_chunks_reranker(mock_cross_encoder):

    mock_model = MagicMock()
    mock_cross_encoder.return_value = mock_model

    mock_model.predict.return_value = [0.9, 0.2, 0.7]

    query = "What is AI?"

    chunks = [
        {"text": "Artificial intelligence definition"},
        {"text": "Cooking recipe"},
        {"text": "Machine learning explanation"},
    ]

    result = chunks_reranker(
        query=query, chunks=chunks, model="fake-model", rerank_top_k=2, min_score=0.3
    )

    assert result == [
        {"text": "Artificial intelligence definition"},
        {"text": "Machine learning explanation"},
    ]
