from unittest.mock import patch, MagicMock
from app.services.utils.generate import ollama_generate, llm_generate_answer


@patch("app.services.utils.generate.requests.post")
def test_ollama_generate(mock_post):

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "This is the answer"}
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    result = ollama_generate(
        prompt="What is AI?",
        ollama_url="http://localhost:11434/api/generate",
        model="llama3",
    )

    assert result == "This is the answer"

    mock_post.assert_called_once()






@patch("app.services.utils.generate.ollama_generate")
@patch("app.services.utils.generate.llm_prompt")
def test_llm_generate_answer(mock_prompt, mock_ollama):

    mock_prompt.return_value = "FINAL PROMPT"
    mock_ollama.return_value = "Generated answer"

    chunks = [
        {
            "chapter": "Respiratory",
            "section": "Cough",
            "text": "Cough may indicate infection",
        },
        {
            "chapter": "Respiratory",
            "section": "Asthma",
            "text": "Asthma causes breathing difficulty",
        },
    ]

    result = llm_generate_answer(
        query="What causes cough?",
        ollama_url="http://localhost:11434/api/generate",
        model="llama3",
        chunks=chunks,
    )

    assert result == "Generated answer"

    mock_prompt.assert_called_once()
    mock_ollama.assert_called_once()
