from pybender.render.image import ImageRenderer
from pybender.render.video import VideoRenderer
from pathlib import Path

class ReelGenerator:
    def __init__(
        self,
        image_renderer: ImageRenderer | None = None,
        video_renderer: VideoRenderer | None = None
    ):
        self.image_renderer = image_renderer or ImageRenderer()
        self.video_renderer = video_renderer or VideoRenderer()
    
    def generate(self, questions_per_run: int, subject: str = "python") -> Path:
        print("🚀 Starting reel generation pipeline")

        metadata_path = self.image_renderer.main(questions_per_run=questions_per_run, subject=subject)
        updated_metadata_path = self.video_renderer.main(metadata_path)

        print("🎬 Reel generation process completed successfully")

        return updated_metadata_path

