from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, status


def extract_youtube_video_id(url: str) -> str:
    parsed_url = urlparse(url)

    if parsed_url.netloc in {"youtu.be", "www.youtu.be"}:
        return parsed_url.path.strip("/")

    if parsed_url.netloc.endswith("youtube.com"):
        query_video_id = parse_qs(parsed_url.query).get("v")
        if query_video_id:
            return query_video_id[0]
        if parsed_url.path.startswith("/shorts/"):
            return parsed_url.path.split("/shorts/", 1)[1].split("/", 1)[0]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid YouTube URL",
    )


def extract_youtube_transcript(url: str) -> tuple[str, str]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="youtube-transcript-api is not installed. Run pip install -r requirements.txt",
        ) from exc

    video_id = extract_youtube_video_id(url)

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not load YouTube transcript: {exc}",
        ) from exc

    text = "\n".join(item.text for item in transcript).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcript text found for this YouTube video",
        )

    return f"YouTube video {video_id}", text
