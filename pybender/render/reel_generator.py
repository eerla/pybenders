import logging
from pathlib import Path

from pybender.config.logging_config import setup_logging
from pybender.render.image import ImageRenderer
from pybender.render.video import VideoRenderer


logger = logging.getLogger(__name__)


def _ensure_logging_configured() -> None:
    if not logging.getLogger().handlers:
        setup_logging()

class ReelGenerator:
    def __init__(
        self,
        image_renderer: ImageRenderer | None = None,
        video_renderer: VideoRenderer | None = None
    ):
        _ensure_logging_configured()
        self.image_renderer = image_renderer or ImageRenderer()
        self.video_renderer = video_renderer or VideoRenderer()
    
    def generate(self, questions_per_run: int, subject: str = "python") -> Path:
        logger.info("🚀 Starting reel generation pipeline")

        metadata_path = self.image_renderer.main(questions_per_run=questions_per_run, subject=subject)
        updated_metadata_path = self.video_renderer.main(metadata_path)

        logger.info("🎬 Reel generation process completed successfully")

        return updated_metadata_path

