from app.services.utils.extract import extract_content_from_uploaded_pdf
from unittest.mock import MagicMock, patch
import io


class FakeUpload:
    def __init__(self, content: bytes):
        self.file = io.BytesIO(content)


@patch("app.services.utils.extract.LlamaParse")
def test_extract_content_from_uploaded_pdf(mock_llama):

    mock_parser = MagicMock()
    mock_llama.return_value = mock_parser

    mock_parser.load_data.return_value = [
        MagicMock(text="Page 1"),
        MagicMock(text="Page 2"),
    ]

    fake_file = FakeUpload(b"fake pdf content")

    result = extract_content_from_uploaded_pdf(fake_file)

    assert result == ["Page 1", "Page 2"]
