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

        # test with mock data - TODO: add mock data file
        # print("Using mock data for testing")
        # import json
        # metadata_path = Path("output/javascript/runs/2025-12-26_133743/metadata.json")
        # with open(metadata_path, "r") as f:
        #     metadata = json.load(f)
        # print(f"🖼 Images generated. Metadata at: {metadata_path}")

        updated_metadata_path = self.video_renderer.main(metadata_path)

        print("🎬 Reel generation process completed successfully")

        return updated_metadata_path

# if __name__ == "__main__":
#     reel_generator = ReelGenerator()
#     reel_generator.generate(questions_per_run=1)