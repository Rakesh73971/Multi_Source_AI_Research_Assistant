import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from app.ingestion.web_loader import VisibleTextParser, extract_web_page


def test_visible_text_parser_basic():
    parser = VisibleTextParser()
    html_content = """
    <html>
      <head>
        <title>My Page Title</title>
        <style>body { color: red; }</style>
        <script>console.log('hello');</script>
      </head>
      <body>
        <h1>Main Heading</h1>
        <p>This is a paragraph of visible text.</p>
        <svg><path d="M10 10"/></svg>
        <span>Inline text here.</span>
      </body>
    </html>
    """
    parser.feed(html_content)

    assert parser.title == "My Page Title"
    
    # Check that style, script, and svg contents are excluded
    assert "body {" not in parser.text
    assert "console.log" not in parser.text
    assert "<path" not in parser.text
    
    # Check that headings, paragraphs, and spans are included
    assert "Main Heading" in parser.text
    assert "This is a paragraph of visible text." in parser.text
    assert "Inline text here." in parser.text


@pytest.mark.anyio
@patch("app.ingestion.web_loader.httpx.AsyncClient")
async def test_extract_web_page_html_success(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/html; charset=utf-8"}
    mock_response.text = "<html><head><title>Test Title</title></head><body>Hello Web!</body></html>"
    
    # Configure mock client context manager
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client_class.return_value.__aenter__.return_value = mock_client

    title, text = await extract_web_page("https://example.com")
    
    assert title == "Test Title"
    assert "Hello Web!" in text
    mock_client.get.assert_called_once_with("https://example.com")


@pytest.mark.anyio
@patch("app.ingestion.web_loader.httpx.AsyncClient")
async def test_extract_web_page_plain_text_success(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/plain"}
    mock_response.text = "This is a plain text file. No HTML here."
    
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client_class.return_value.__aenter__.return_value = mock_client

    title, text = await extract_web_page("https://example.com/file.txt")
    
    assert title == "https://example.com/file.txt"
    assert text == "This is a plain text file. No HTML here."


@pytest.mark.anyio
@patch("app.ingestion.web_loader.httpx.AsyncClient")
async def test_extract_web_page_http_error(mock_client_class):
    mock_client = MagicMock()
    # Mock httpx throwing HTTPError on get
    mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Network down"))
    mock_client_class.return_value.__aenter__.return_value = mock_client

    with pytest.raises(HTTPException) as exc_info:
        await extract_web_page("https://example.com")
        
    assert exc_info.value.status_code == 400
    assert "Could not fetch URL" in exc_info.value.detail


@pytest.mark.anyio
@patch("app.ingestion.web_loader.httpx.AsyncClient")
async def test_extract_web_page_invalid_content_type(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Return non-text format
    mock_response.headers = {"content-type": "application/pdf"}
    
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client_class.return_value.__aenter__.return_value = mock_client

    with pytest.raises(HTTPException) as exc_info:
        await extract_web_page("https://example.com/doc.pdf")
        
    assert exc_info.value.status_code == 400
    assert "URL must return HTML or plain text content" in exc_info.value.detail


@pytest.mark.anyio
@patch("app.ingestion.web_loader.httpx.AsyncClient")
async def test_extract_web_page_empty_text(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/html"}
    mock_response.text = "<html><body></body></html>"
    
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client_class.return_value.__aenter__.return_value = mock_client

    with pytest.raises(HTTPException) as exc_info:
        await extract_web_page("https://example.com/empty")
        
    assert exc_info.value.status_code == 400
    assert "No readable text found at this URL" in exc_info.value.detail
