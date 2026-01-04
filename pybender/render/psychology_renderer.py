




import logging
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Dict, Tuple, List
from pybender.generator.schema import PsychologyCard
from pybender.render.themes import PSYCHOLOGY_THEMES
from pybender.render.text_utils import wrap_text

logger = logging.getLogger(__name__)

class PsychologyRenderer:
    """Renders psychology wisdom cards with colorful, friendly themes."""
    
    # Standard sizes
    REEL_SIZE = (1080, 1920)
    CAROUSEL_SIZE = (1080, 1080)
    
    # Layout configurations for different formats
    LAYOUT_CONFIG = {
        "reel": {
            "welcome": {"card_margin": 80, "card_h": 900, "headline_y": 220, "spacing": 140},
            "statement": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "explanation": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "example": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "application": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "cta": {"card_w": 920, "card_h": 640, "content_y": 110, "shadow_blur": 18},
        },
        "carousel": {
            "welcome": {"card_margin": 40, "card_h": 700, "headline_y": 130, "spacing": 100},
            "statement": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "explanation": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "example": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "application": {"card_margin": 40, "card_h": 900, "content_y": 70, "shadow_blur": 16},
            "cta": {"card_w": 700, "card_h": 500, "content_y": 80, "shadow_blur": 14},
        }
    }

    def __init__(self):
        self.WIDTH, self.HEIGHT = self.REEL_SIZE
        
        # Theme definitions
        self.THEMES = PSYCHOLOGY_THEMES
        
        # Fonts (friendly, rounded)
        self.FONT_DIR = Path("pybender/assets/fonts")
        self.INTER_DIR = self.FONT_DIR / "Inter-4.1" / "extras" / "ttf"
        
        # Larger, more readable fonts for non-technical content
        self.TITLE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Bold.ttf"), 56)
        self.PUZZLE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-SemiBold.ttf"), 56)
        self.TEXT_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 42)
        self.BADGE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 32)
        self.OPTION_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Medium.ttf"), 48)
        self.EXPLANATION_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 38)
        self.EMOJI_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 64)
    
    def render_welcome_card(self, theme: Dict, output_path: Path, size: Tuple[int, int] = None, category: str = None) -> Path:
        """Render welcome/cover card for psychology profile."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        layout = self._get_layout(size, "welcome")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)

        # Subtle card container
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']

        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 12, card_y + 12, card_x + card_w + 12, card_y + card_h + 12],
            radius=48,
            fill=(0, 0, 0, 70)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(24))
        canvas.paste(shadow, (0, 0), shadow)

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=48,
            fill=theme['puzzle_box']
        )

        center_x = width // 2
        y_pos = card_y + layout['headline_y']

        # Category badge (if provided)
        if category:
            category_text = category.upper().replace("_", " ")
            cat_bbox = draw.textbbox((0, 0), category_text, font=self.TEXT_FONT)
            cat_w = cat_bbox[2] - cat_bbox[0] + 40
            cat_h = cat_bbox[3] - cat_bbox[1] + 16
            cat_x = center_x - cat_w // 2
            
            badge_top = y_pos - 20
            badge_bottom = y_pos + cat_h - 20
            badge_center_y = badge_top + (badge_bottom - badge_top) // 2
            
            draw.rounded_rectangle(
                [cat_x, badge_top, cat_x + cat_w, badge_bottom],
                radius=20,
                fill=theme['accent']
            )
            draw.text(
                (center_x, badge_center_y),
                category_text,
                font=self.TEXT_FONT,
                fill=(255, 255, 255),
                anchor="mm"
            )
            y_pos += 80

        # Main headline
        headline = "Daily Psychology Insight"
        headline_lines = self._wrap_text_centered(headline, self.PUZZLE_FONT, card_w - 80)
        for line in headline_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.PUZZLE_FONT,
                fill=theme['text_primary'],
                anchor="mm"
            )
            y_pos += layout['spacing']

        # Supporting line
        subline = "Understanding human behavior"
        subline_lines = self._wrap_text_centered(subline, self.TEXT_FONT, card_w - 80)
        for line in subline_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TEXT_FONT,
                fill=theme['text_secondary'],
                anchor="mm"
            )
            y_pos += 60

        y_pos += 60

        # CTA badge
        badge_text = "Keep watching for daily insights"
        badge_bbox = draw.textbbox((0, 0), badge_text, font=self.TEXT_FONT)
        badge_w = badge_bbox[2] - badge_bbox[0] + 80
        badge_h = badge_bbox[3] - badge_bbox[1] + 32
        badge_x = center_x - badge_w // 2

        draw.rounded_rectangle(
            [badge_x, y_pos, badge_x + badge_w, y_pos + badge_h],
            radius=30,
            fill=theme['accent']
        )
        draw.text(
            (center_x, y_pos + badge_h // 2),
            badge_text,
            font=self.TEXT_FONT,
            fill=(255, 255, 255),
            anchor="mm"
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        logger.info(f"✅ Saved psychology welcome cover: {output_path}")
        return output_path
    
    def render_statement_card(self, card: Dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None) -> Path:
        """Render statement card - the main psychology fact/principle."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        layout = self._get_layout(size, "statement")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)
        
        # Card with shadow
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']
        
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 10, card_y + 10, card_x + card_w + 10, card_y + card_h + 10],
            radius=40,
            fill=(0, 0, 0, 60)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(layout['shadow_blur']))
        canvas.paste(shadow, (0, 0), shadow)
        
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=40,
            fill=theme['puzzle_box']
        )
        
        center_x = width // 2
        y_pos = card_y + layout['content_y']
        
        # Category badge
        category = card['category'].replace('_', ' ').title()
        badge_text = category
        bbox = draw.textbbox((0, 0), badge_text, font=self.TEXT_FONT)
        badge_w = bbox[2] - bbox[0] + 40
        badge_h = bbox[3] - bbox[1] + 20
        badge_x = center_x - badge_w // 2
        
        draw.rounded_rectangle(
            [badge_x, y_pos, badge_x + badge_w, y_pos + badge_h],
            radius=25,
            fill=theme['accent']
        )
        draw.text(
            (center_x, y_pos + badge_h // 2),
            badge_text,
            font=self.TEXT_FONT,
            fill=(255, 255, 255),
            anchor="mm"
        )
        
        y_pos += badge_h + 80
        
        # Title (principle name)
        title = card['title']
        title_lines = self._wrap_text_centered(title, self.TITLE_FONT, card_w - 100)
        for line in title_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TITLE_FONT,
                fill=theme['accent'],
                anchor="mm"
            )
            y_pos += 80
        
        y_pos += 40
        
        # Statement (bold fact) - largest text on this card
        statement = card['statement']
        statement_lines = self._wrap_text_centered(statement, self.PUZZLE_FONT, card_w - 100)
        for line in statement_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.PUZZLE_FONT,
                fill=theme['text_primary'],
                anchor="mm"
            )
            y_pos += 90
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        logger.info(f"✅ Saved psychology statement card: {output_path}")
        return output_path
    
    def render_explanation_card(self, card: Dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None) -> Path:
        """Render explanation card - why this psychology principle matters."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        layout = self._get_layout(size, "explanation")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)
        
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']
        
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 10, card_y + 10, card_x + card_w + 10, card_y + card_h + 10],
            radius=40,
            fill=(0, 0, 0, 60)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(layout['shadow_blur']))
        canvas.paste(shadow, (0, 0), shadow)
        
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=40,
            fill=theme['puzzle_box']
        )
        
        center_x = width // 2
        y_pos = card_y + layout['content_y']
        
        # Header
        header = "Why It Matters"
        draw.text(
            (center_x, y_pos),
            header,
            font=self.TITLE_FONT,
            fill=theme['accent'],
            anchor="mm"
        )
        y_pos += 100
        
        # Explanation text (wrapped)
        explanation = card['explanation']
        explanation_lines = self._wrap_text_centered(explanation, self.TEXT_FONT, card_w - 100)
        for line in explanation_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TEXT_FONT,
                fill=theme['text_primary'],
                anchor="mm"
            )
            y_pos += 70
        
        # Source citation (if available)
        if card.get('source'):
            y_pos += 40
            source_text = f"Source: {card['source']}"
            draw.text(
                (center_x, y_pos),
                source_text,
                font=self.EXPLANATION_FONT,
                fill=theme['text_secondary'],
                anchor="mm"
            )
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        logger.info(f"✅ Saved psychology explanation card: {output_path}")
        return output_path
    
    def render_example_card(self, card: Dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None) -> Path:
        """Render example card - real-life scenario showing the principle in action."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        layout = self._get_layout(size, "example")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)
        
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']
        
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 10, card_y + 10, card_x + card_w + 10, card_y + card_h + 10],
            radius=40,
            fill=(0, 0, 0, 60)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(layout['shadow_blur']))
        canvas.paste(shadow, (0, 0), shadow)
        
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=40,
            fill=theme['puzzle_box']
        )
        
        center_x = width // 2
        y_pos = card_y + layout['content_y']
        
        # Header
        header = "Real-Life Example"
        draw.text(
            (center_x, y_pos),
            header,
            font=self.TITLE_FONT,
            fill=theme['accent'],
            anchor="mm"
        )
        y_pos += 100
        
        # Example text (wrapped)
        example = card['real_example']
        example_lines = self._wrap_text_centered(example, self.TEXT_FONT, card_w - 100)
        for line in example_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TEXT_FONT,
                fill=theme['text_primary'],
                anchor="mm"
            )
            y_pos += 70
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        logger.info(f"✅ Saved psychology example card: {output_path}")
        return output_path
    
    def render_application_card(self, card: Dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None) -> Path:
        """Render application card - actionable tip the reader can use today."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        layout = self._get_layout(size, "application")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)
        
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']
        
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 10, card_y + 10, card_x + card_w + 10, card_y + card_h + 10],
            radius=40,
            fill=(0, 0, 0, 60)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(layout['shadow_blur']))
        canvas.paste(shadow, (0, 0), shadow)
        
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=40,
            fill=theme['puzzle_box']
        )
        
        center_x = width // 2
        y_pos = card_y + layout['content_y']
        
        # Header
        header = "Try This Today"
        draw.text(
            (center_x, y_pos),
            header,
            font=self.TITLE_FONT,
            fill=theme['accent'],
            anchor="mm"
        )
        y_pos += 100
        
        # Application text (wrapped, actionable)
        application = card['application']
        app_lines = self._wrap_text_centered(application, self.TEXT_FONT, card_w - 100)
        for line in app_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TEXT_FONT,
                fill=theme['text_primary'],
                anchor="mm"
            )
            y_pos += 70
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        logger.info(f"✅ Saved psychology application card: {output_path}")
        return output_path
    
    def render_cta_card(self, theme: Dict, reel_cta_path: Path, carousel_cta_path: Path) -> Dict[str, Path]:
        """Render CTA images for both reel and carousel formats."""
        
        for size, path, format_name in [
            (self.REEL_SIZE, reel_cta_path, "REEL"),
            (self.CAROUSEL_SIZE, carousel_cta_path, "CAROUSEL"),
        ]:
            path.parent.mkdir(parents=True, exist_ok=True)

            width, height = size
            layout = self._get_layout(size, "cta")

            canvas = self.create_gradient_background(theme, size)
            draw = ImageDraw.Draw(canvas)

            card_w = layout['card_w']
            card_h = layout['card_h']
            card_x = (width - card_w) // 2
            card_y = (height - card_h) // 2

            # Card with shadow
            shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle(
                [card_x + 12, card_y + 12, card_x + card_w + 12, card_y + card_h + 12],
                radius=36,
                fill=(0, 0, 0, 70),
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(layout['shadow_blur']))
            canvas.paste(shadow, (0, 0), shadow)

            draw.rounded_rectangle(
                [card_x, card_y, card_x + card_w, card_y + card_h],
                radius=36,
                fill=theme['puzzle_box'],
            )

            y = card_y + layout['content_y']
            center_x = width // 2

            title = "That's the Insight"
            title_lines = self._wrap_text_centered(title, self.PUZZLE_FONT, card_w - 100)
            for line in title_lines:
                draw.text(
                    (center_x, y),
                    line,
                    font=self.PUZZLE_FONT,
                    fill=theme['text_primary'],
                    anchor="mm",
                )
                y += 120

            body_lines = [
                "Understanding yourself and others deeply.",
                "Save & share this insight!",
            ]
            for raw_line in body_lines:
                wrapped = self._wrap_text_centered(raw_line, self.TEXT_FONT, card_w - 100)
                for line in wrapped:
                    draw.text(
                        (center_x, y),
                        line,
                        font=self.TEXT_FONT,
                        fill=theme['text_secondary'],
                        anchor="mm",
                    )
                    y += 64 if size == self.CAROUSEL_SIZE else 70

            y += 14 if size == self.CAROUSEL_SIZE else 20
            badge_text = "Follow for daily psychology insights"
            # Cap badge width to leave space on sides (margin of 60px on each side)
            max_badge_width = card_w - 120
            badge_font = self.BADGE_FONT if size == self.CAROUSEL_SIZE else self.TEXT_FONT
            badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
            badge_text_width = badge_bbox[2] - badge_bbox[0]
            badge_w = min(max_badge_width, badge_text_width + 80)
            badge_h = badge_bbox[3] - badge_bbox[1] + 32
            badge_x = center_x - badge_w // 2

            draw.rounded_rectangle(
                [badge_x, y, badge_x + badge_w, y + badge_h],
                radius=28,
                fill=theme['accent'],
            )
            draw.text(
                (center_x, y + badge_h // 2),
                badge_text,
                font=badge_font,
                fill=(255, 255, 255),
                anchor="mm",
            )

            canvas.save(path)
            logger.info(f"✅ Saved {format_name} psychology CTA: {path}")

        return {"reel": reel_cta_path, "carousel": carousel_cta_path}

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _get_format(self, size: Tuple[int, int]) -> str:
        """Infer format key from size."""
        return "reel" if size[1] > size[0] else "carousel"

    def _get_layout(self, size: Tuple[int, int], card_type: str) -> Dict:
        fmt = self._get_format(size)
        return self.LAYOUT_CONFIG[fmt][card_type]

    def select_random_theme(self) -> Dict:
        key = random.choice(list(self.THEMES.keys()))
        theme = dict(self.THEMES[key])
        theme["name"] = theme.get("name", key.replace("_", " ").title())
        return theme

    def create_gradient_background(self, theme: Dict, size: Tuple[int, int]) -> Image.Image:
        """Create a soft vertical gradient between primary and secondary background colors."""
        width, height = size
        base = Image.new("RGB", size, theme["bg_primary"])
        top = theme["bg_primary"]
        bottom = theme["bg_secondary"]

        gradient = Image.new("RGB", (1, height), color=0)
        for y in range(height):
            ratio = y / float(height)
            r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
            g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
            b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
            gradient.putpixel((0, y), (r, g, b))

        gradient = gradient.resize((width, height))
        base.paste(gradient, (0, 0))
        return base

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Left-aligned text wrapping using shared util."""
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        return wrap_text(draw, text, font, max_width)

    def _wrap_text_centered(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Center-aligned wrapping; lines returned without centering applied so caller can anchor."""
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