from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from common.logger import get_logger
from common.exceptions import TranscriptNotFoundError, InvalidYouTubeURLError

logger = get_logger(__name__)

def extract_video_id(url: str) -> str:
    """Extracts the YouTube video ID from common URL formats."""
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
    else:
        logger.error(f"Invalid YouTube URL: {url}")
        raise InvalidYouTubeURLError("Invalid YouTube URL format.")

    logger.info(f"Extracted video_id: {video_id}")
    return video_id

def get_transcript(video_id: str) -> str:
    """
    Fetches transcript using the latest youtube-transcript-api API.
    Returns a single concatenated string from transcript segments.
    """
    try:
        ytt = YouTubeTranscriptApi()
        fetched = ytt.fetch(video_id)  # modern method
        raw = fetched.to_raw_data()    # [{'text','start','duration'}, ...]

        text = " ".join(d.get("text", "") for d in raw if d.get("text"))
        logger.info(f"Fetched transcript: {len(raw)} segments, {len(text)} chars")
        return text

    except (TranscriptsDisabled, NoTranscriptFound):
        logger.error(f"No transcript available for video_id={video_id}")
        raise TranscriptNotFoundError("Transcript not available for this video.")