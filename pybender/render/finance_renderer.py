import logging
import random
from pathlib import Path
from typing import Dict, Tuple, List

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from pybender.generator.schema import FinanceCard
from pybender.render.themes import FINANCE_THEMES
from pybender.render.text_utils import wrap_text

logger = logging.getLogger(__name__)


class FinanceRenderer:
    """Renders finance insight cards (reel + carousel) with dark gold theme."""

    REEL_SIZE = (1080, 1920)
    CAROUSEL_SIZE = (1080, 1080)

    LAYOUT_CONFIG = {
        "reel": {
            "welcome": {"card_margin": 80, "card_h": 900, "headline_y": 220, "spacing": 140},
            "insight": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "explanation": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "example": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "action": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "cta": {"card_w": 920, "card_h": 640, "content_y": 110, "shadow_blur": 18},
        },
        "carousel": {
            "welcome": {"card_margin": 40, "card_h": 700, "headline_y": 130, "spacing": 100},
            "insight": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "explanation": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "example": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "action": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "cta": {"card_w": 700, "card_h": 500, "content_y": 80, "shadow_blur": 14},
        },
    }

    def __init__(self):
        self.WIDTH, self.HEIGHT = self.REEL_SIZE
        self.THEMES = FINANCE_THEMES

        self.FONT_DIR = Path("pybender/assets/fonts")
        self.INTER_DIR = self.FONT_DIR / "Inter-4.1" / "extras" / "ttf"

        self.TITLE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Bold.ttf"), 56)
        self.SUBTITLE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-SemiBold.ttf"), 48)
        self.TEXT_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 42)
        self.BADGE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 36)

    def _get_format(self, size: Tuple[int, int]) -> str:
        return "carousel" if size == self.CAROUSEL_SIZE else "reel"

    def _get_layout(self, size: Tuple[int, int], card_type: str) -> Dict:
        return self.LAYOUT_CONFIG[self._get_format(size)].get(card_type, {})

    def select_random_theme(self) -> Dict:
        name = random.choice(list(self.THEMES.keys()))
        theme = self.THEMES[name]
        logger.info("🎨 Selected finance theme: %s", theme.get("name", name))
        return theme

    def create_gradient_background(self, theme: Dict, size: Tuple[int, int]) -> Image.Image:
        width, height = size
        base = Image.new("RGB", size, theme["bg_primary"])
        top = Image.new("RGB", size, theme["bg_secondary"])
        mask = Image.new("L", size)
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        return wrap_text(draw, text, font, max_width)

    def _wrap_text_centered(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        if not text:
            return [""]
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        words = text.split(" ")
        lines: List[str] = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    # ---------- Card Renders ----------
    def render_welcome_card(self, theme: Dict, output_path: Path, size: Tuple[int, int], category: str) -> Path:
        width, height = size
        layout = self._get_layout(size, "welcome")
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)

        card_margin = layout["card_margin"]
        card_w = width - (card_margin * 2)
        card_h = layout["card_h"]
        card_x = card_margin
        card_y = (height - card_h) // 2

        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 12, card_y + 12, card_x + card_w + 12, card_y + card_h + 12],
            radius=48,
            fill=(0, 0, 0, 90),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(24))
        canvas.paste(shadow, (0, 0), shadow)

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=48,
            fill=theme["card_bg"],
        )

        center_x = width // 2
        y_pos = card_y + layout["headline_y"]

        badge_text = category.replace("_", " ").title()
        badge_bbox = draw.textbbox((0, 0), badge_text, font=self.TEXT_FONT)
        badge_w = badge_bbox[2] - badge_bbox[0] + 40
        badge_h = badge_bbox[3] - badge_bbox[1] + 18
        badge_x = center_x - badge_w // 2
        draw.rounded_rectangle(
            [badge_x, y_pos - 14, badge_x + badge_w, y_pos + badge_h - 14],
            radius=20,
            fill=theme["accent"],
        )
        draw.text((center_x, y_pos - 14 + badge_h // 2), badge_text, font=self.TEXT_FONT, fill=(0, 0, 0), anchor="mm")

        y_pos += layout["spacing"]
        headline = "Finance, simplified."
        for line in self._wrap_text_centered(headline, self.TITLE_FONT, card_w - 80):
            draw.text((center_x, y_pos), line, font=self.TITLE_FONT, fill=theme["text_primary"], anchor="mm")
            y_pos += layout["spacing"]

        sub = "Swipe for insights you can use today."
        for line in self._wrap_text_centered(sub, self.TEXT_FONT, card_w - 80):
            draw.text((center_x, y_pos), line, font=self.TEXT_FONT, fill=theme["text_secondary"], anchor="mm")
            y_pos += 60

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        return output_path

    def _render_body_card(self, card_type: str, heading: str, body: str, theme: Dict, output_path: Path, size: Tuple[int, int]):
        width, height = size
        layout = self._get_layout(size, card_type)
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)

        card_margin = layout["card_margin"]
        card_w = width - (card_margin * 2)
        card_h = layout["card_h"]
        card_x = card_margin
        card_y = (height - card_h) // 2

        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 10, card_y + 10, card_x + card_w + 10, card_y + card_h + 10],
            radius=40,
            fill=(0, 0, 0, 70),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(layout["shadow_blur"]))
        canvas.paste(shadow, (0, 0), shadow)

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=40,
            fill=theme["puzzle_box"],
        )

        center_x = width // 2

        heading_font = self.TITLE_FONT if size == self.REEL_SIZE else self.SUBTITLE_FONT
        heading_lines = self._wrap_text_centered(heading, heading_font, card_w - 100)
        heading_line_height = 70 if size == self.REEL_SIZE else 60

        body_lines = self._wrap_text_centered(body, self.TEXT_FONT, card_w - 120)
        body_line_height = 58 if size == self.REEL_SIZE else 52

        gap = 20
        total_block_h = len(heading_lines) * heading_line_height + gap + len(body_lines) * body_line_height
        y_pos = card_y + (card_h - total_block_h) // 2

        for line in heading_lines:
            draw.text((center_x, y_pos), line, font=heading_font, fill=theme["accent"], anchor="mm")
            y_pos += heading_line_height

        y_pos += gap
        for line in body_lines:
            draw.text((center_x, y_pos), line, font=self.TEXT_FONT, fill=theme["text_primary"], anchor="mm")
            y_pos += body_line_height

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        return output_path

    def render_insight_card(self, question: FinanceCard, theme: Dict, output_path: Path, size: Tuple[int, int]):
        return self._render_body_card("insight", question.insight, question.explanation, theme, output_path, size)

    def render_explanation_card(self, question: FinanceCard, theme: Dict, output_path: Path, size: Tuple[int, int]):
        return self._render_body_card("explanation", "Why it matters", question.explanation, theme, output_path, size)

    def render_example_card(self, question: FinanceCard, theme: Dict, output_path: Path, size: Tuple[int, int]):
        return self._render_body_card("example", "Example", question.example, theme, output_path, size)

    def render_action_card(self, question: FinanceCard, theme: Dict, output_path: Path, size: Tuple[int, int]):
        return self._render_body_card("action", "Try this", question.action, theme, output_path, size)

    def render_cta_card(self, theme: Dict, reel_cta_path: Path, carousel_cta_path: Path) -> Dict[str, Path]:
        for size, path, format_name in [
            (self.REEL_SIZE, reel_cta_path, "REEL"),
            (self.CAROUSEL_SIZE, carousel_cta_path, "CAROUSEL"),
        ]:
            path.parent.mkdir(parents=True, exist_ok=True)
            width, height = size
            layout = self._get_layout(size, "cta")

            canvas = self.create_gradient_background(theme, size)
            draw = ImageDraw.Draw(canvas)

            card_w = layout["card_w"]
            card_h = layout["card_h"]
            card_x = (width - card_w) // 2
            card_y = (height - card_h) // 2

            shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle(
                [card_x + 12, card_y + 12, card_x + card_w + 12, card_y + card_h + 12],
                radius=36,
                fill=(0, 0, 0, 90),
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(layout["shadow_blur"]))
            canvas.paste(shadow, (0, 0), shadow)

            draw.rounded_rectangle(
                [card_x, card_y, card_x + card_w, card_y + card_h],
                radius=36,
                fill=theme["puzzle_box"],
            )

            y = card_y + layout["content_y"]
            center_x = width // 2

            title = "That's the Insight"
            for line in self._wrap_text_centered(title, self.TITLE_FONT, card_w - 100):
                draw.text((center_x, y), line, font=self.TITLE_FONT, fill=theme["text_primary"], anchor="mm")
                y += 110

            body_lines = [
                "Money made simple.",
                "Save & share this insight!",
            ]
            for raw_line in body_lines:
                for line in self._wrap_text_centered(raw_line, self.TEXT_FONT, card_w - 100):
                    draw.text((center_x, y), line, font=self.TEXT_FONT, fill=theme["text_secondary"], anchor="mm")
                    y += 60 if size == self.CAROUSEL_SIZE else 68

            y += 14 if size == self.CAROUSEL_SIZE else 20
            badge_text = "Follow for daily finance tips"
            badge_font = self.BADGE_FONT if size == self.CAROUSEL_SIZE else self.TEXT_FONT
            max_badge_width = card_w - 120
            badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
            badge_text_width = badge_bbox[2] - badge_bbox[0]
            badge_w = min(max_badge_width, badge_text_width + 80)
            badge_h = badge_bbox[3] - badge_bbox[1] + 32
            badge_x = center_x - badge_w // 2

            draw.rounded_rectangle(
                [badge_x, y, badge_x + badge_w, y + badge_h],
                radius=28,
                fill=theme["accent"],
            )
            draw.text((center_x, y + badge_h // 2), badge_text, font=badge_font, fill=(0, 0, 0), anchor="mm")

            canvas.save(path)
            logger.info("✅ Saved %s CTA: %s", format_name, path)

        return {"reel": reel_cta_path, "carousel": carousel_cta_path}
