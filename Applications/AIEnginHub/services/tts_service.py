import urllib.parse
import hashlib
import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_tts_audio_bytes(query: str, target_lang: str = 'en') -> tuple[bytes | None, str | None]:
    """
    Fetches Google Translate TTS audio bytes for regional speech (Malayalam, Tamil, Hindi, German, French, etc.)
    with local cache to optimize bandwidth and eliminate redundant requests.
    Returns (audio_bytes, error_message).
    """
    if not query:
        return None, "Empty text provided for TTS"

    # Normalize hash
    query_hash = hashlib.md5(query.encode('utf-8')).hexdigest()
    cache_key = f"tts_audio_{target_lang}_{query_hash}"

    cached = cache.get(cache_key)
    if cached:
        return cached, None

    encoded_q = urllib.parse.quote(query)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={target_lang}&client=tw-ob&q={encoded_q}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            audio_bytes = res.content
            # Cache for 7 days
            cache.set(cache_key, audio_bytes, timeout=60 * 60 * 24 * 7)
            return audio_bytes, None
        else:
            return None, f"Upstream TTS returned HTTP {res.status_code}"
    except Exception as exc:
        logger.error(f"[TTS Service Error] {exc}")
        return None, str(exc)
