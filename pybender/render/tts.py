"""
Narration via edge-tts (Microsoft Edge neural voices) - free, no API key required.
"""
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import edge_tts

logger = logging.getLogger(__name__)

DEFAULT_VOICE = "en-US-AndrewNeural"
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.5

if sys.platform == "win32":
    # aiohttp + the default ProactorEventLoop intermittently raise
    # "OSError: [WinError 64] The specified network name is no longer
    # available" on otherwise-healthy connections. The selector loop doesn't
    # have this issue; only affects this module's own asyncio.run() calls.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _synthesize(text: str, voice: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_path))


def synthesize_narration(text: str, out_path: Path, voice: str = DEFAULT_VOICE) -> Optional[Path]:
    """
    Generate narration audio for `text` via edge-tts, saved to out_path.

    Returns out_path on success, or None if text is empty or synthesis fails
    after retries (e.g. persistent network issue) so callers can fall back to
    music-only rather than crash the whole render.
    """
    text = (text or "").strip()
    if not text:
        logger.info("🎙️ No narration text provided for %s, skipping (music-only)", out_path.name)
        return None

    out_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("🎙️ Synthesizing narration (%d chars) -> %s", len(text), out_path.name)

    last_error: Optional[Exception] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            asyncio.run(_synthesize(text, voice, out_path))
            logger.info("🎙️ Narration ready: %s", out_path.name)
            return out_path
        except Exception as e:
            last_error = e
            if attempt < MAX_ATTEMPTS:
                logger.warning(
                    "TTS synthesis attempt %s/%s failed, retrying: %s",
                    attempt, MAX_ATTEMPTS, e,
                )
                time.sleep(RETRY_DELAY_SECONDS)

    logger.warning(
        "TTS synthesis failed after %s attempts, falling back to music-only: %s",
        MAX_ATTEMPTS, last_error,
    )
    return None
