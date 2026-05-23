from html.parser import HTMLParser

import httpx
from fastapi import HTTPException, status


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignored_tag_depth = 0
        self._title_depth = 0
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_tag_depth += 1
        if tag == "title":
            self._title_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self._ignored_tag_depth:
            self._ignored_tag_depth -= 1
        if tag == "title" and self._title_depth:
            self._title_depth -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self._title_depth:
            self.title_parts.append(text)
        if not self._ignored_tag_depth:
            self.text_parts.append(text)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()

    @property
    def text(self) -> str:
        return "\n".join(self.text_parts).strip()


async def extract_web_page(url: str) -> tuple[str, str]:
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "MultiSourceResearchAssistant/1.0"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not fetch URL: {exc}",
        ) from exc

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must return HTML or plain text content",
        )

    parser = VisibleTextParser()
    parser.feed(response.text)
    text = parser.text if "text/html" in content_type else response.text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable text found at this URL",
        )

    title = parser.title or url
    return title, text
