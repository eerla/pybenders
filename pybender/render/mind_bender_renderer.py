# pybender/render/mind_bender_renderer.py
"""
Mind Benders (Brain Teasers) Image Renderer with Colorful Themes.

This renderer creates vibrant, non-technical puzzle cards with:
- 5 rotating color themes (sunset, ocean, mint, lavender, golden)
- Large, readable text optimized for quick comprehension
- Emoji support for visual interest
- Friendly, accessible design (not code-centric)
"""

import logging
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Dict, Tuple
from pybender.generator.schema import MindBenderQuestion
from pybender.render.themes import MIND_BENDERS_THEMES

logger = logging.getLogger(__name__)

class MindBenderRenderer:
    """Renders brain teaser puzzles with colorful, friendly themes."""
    
    # Standard sizes
    REEL_SIZE = (1080, 1920)
    CAROUSEL_SIZE = (1080, 1080)
    
    # Layout configurations for different formats
    LAYOUT_CONFIG = {
        "reel": {
            "welcome": {"card_margin": 80, "card_h": 900, "headline_y": 220, "spacing": 140},
            "puzzle": {"card_margin": 60, "card_h": 1200, "content_y": 80, "shadow_blur": 20},
            "answer": {"card_margin": 60, "card_h": 1200, "content_y": 100, "shadow_blur": 20},
            "hint": {"card_margin": 60, "card_h": 1300, "content_y": 160, "shadow_blur": 20},
            "cta": {"card_w": 920, "card_h": 640, "content_y": 110, "shadow_blur": 18},
        },
        "carousel": {
            "welcome": {"card_margin": 40, "card_h": 700, "headline_y": 130, "spacing": 100},
            "puzzle": {"card_margin": 40, "card_h": 1000, "content_y": 52, "shadow_blur": 16},
            "answer": {"card_margin": 40, "card_h": 900, "content_y": 60, "shadow_blur": 16},
            "hint": {"card_margin": 40, "card_h": 950, "content_y": 120, "shadow_blur": 16},
            "cta": {"card_w": 700, "card_h": 500, "content_y": 80, "shadow_blur": 14},
        }
    }
    
    def __init__(self):
        self.WIDTH, self.HEIGHT = self.REEL_SIZE
        
        # Theme definitions
        self.THEMES = MIND_BENDERS_THEMES
        
        # Fonts (friendly, rounded)
        self.FONT_DIR = Path("pybender/assets/fonts")
        self.INTER_DIR = self.FONT_DIR / "Inter-4.1" / "extras" / "ttf"
        
        # Larger, more readable fonts for non-technical content
        self.TITLE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Bold.ttf"), 56)
        self.PUZZLE_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-SemiBold.ttf"), 56)
        self.PUZZLE_FONT_CAROUSEL = ImageFont.truetype(str(self.INTER_DIR / "Inter-SemiBold.ttf"), 52)
        self.TEXT_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 42)
        self.OPTION_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Medium.ttf"), 48)
        self.OPTION_FONT_CAROUSEL = ImageFont.truetype(str(self.INTER_DIR / "Inter-Medium.ttf"), 44)
        self.EXPLANATION_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 38)
        self.EMOJI_FONT = ImageFont.truetype(str(self.INTER_DIR / "Inter-Regular.ttf"), 64)
    
    def _get_format(self, size: Tuple[int, int]) -> str:
        """Determine format (reel or carousel) from size."""
        if size == self.CAROUSEL_SIZE:
            return "carousel"
        return "reel"
    
    def _get_layout(self, size: Tuple[int, int], card_type: str) -> Dict:
        """Get layout config for given size and card type."""
        format_type = self._get_format(size)
        return self.LAYOUT_CONFIG[format_type].get(card_type, {})
        
    def select_random_theme(self) -> Dict:
        """Randomly select one of 5 color themes."""
        theme_name = random.choice(list(self.THEMES.keys()))
        theme = self.THEMES[theme_name]
        logger.info(f"🎨 Selected theme: {theme['name']}")
        return theme
    
    def create_gradient_background(self, theme: Dict, size: Tuple[int, int]) -> Image.Image:
        """Create smooth gradient background from theme colors."""
        width, height = size
        base = Image.new('RGB', size, theme['bg_primary'])
        top = Image.new('RGB', size, theme['bg_secondary'])
        mask = Image.new('L', size)
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base

    def render_theme_transition_sequence(self, theme: Dict, output_dir: Path) -> Dict[str, Path]:
        """Generate reusable transition sequence for a theme if missing.

        Returns dict with paths: base, 2, 1, ready.
        Skips work when all files already exist.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "base": output_dir / "transition_base.png",
            "2": output_dir / "transition_2.png",
            "1": output_dir / "transition_1.png",
            "ready": output_dir / "transition_ready.png",
        }

        if all(p.exists() for p in paths.values()):
            logger.info("✅ Theme transitions already exist for %s", theme.get("name", ""))
            return paths

        # Shared geometry
        width, height = self.WIDTH, self.HEIGHT
        content_w, content_h = 820, 720
        content_x = (width - content_w) // 2
        content_y = (height - content_h) // 2

        # Fonts
        large_num_font = ImageFont.truetype(str(self.INTER_DIR / "Inter-Bold.ttf"), 320)
        title_font = self.TITLE_FONT
        body_font = self.TEXT_FONT

        def draw_card(bg: Image.Image, border: bool = False) -> Image.Image:
            draw = ImageDraw.Draw(bg)
            draw.rounded_rectangle(
                [content_x, content_y, content_x + content_w, content_y + content_h],
                radius=36,
                fill=theme["puzzle_box"],
                outline=theme["accent"] if border else None,
                width=2 if border else 0,
            )
            return draw

        # 1) Base: "Want to guess?"
        img = self.create_gradient_background(theme, (width, height))
        draw = draw_card(img, border=True)
        headline = "Want to guess?"
        sub = "Pause and think for a sec"
        h_bbox = draw.textbbox((0, 0), headline, font=title_font)
        s_bbox = draw.textbbox((0, 0), sub, font=body_font)
        draw.text(((width - h_bbox[2]) // 2, content_y + 200), headline, font=title_font, fill=theme["accent"])
        draw.text(((width - s_bbox[2]) // 2, content_y + 320), sub, font=body_font, fill=theme["text_secondary"])
        img.save(paths["base"])
        logger.info("✅ Created transition base for %s", theme.get("name", ""))

        # 2) Countdown "2"
        img = self.create_gradient_background(theme, (width, height))
        draw = draw_card(img)
        draw.text(
            ((width) // 2, content_y + 220),
            "2",
            font=large_num_font,
            fill=theme["accent"],
            anchor="mm",
        )
        img.save(paths["2"])
        logger.info("✅ Created transition 2 for %s", theme.get("name", ""))

        # 3) Countdown "1"
        img = self.create_gradient_background(theme, (width, height))
        draw = draw_card(img)
        draw.text(
            ((width) // 2, content_y + 220),
            "1",
            font=large_num_font,
            fill=theme["text_primary"],
            anchor="mm",
        )
        img.save(paths["1"])
        logger.info("✅ Created transition 1 for %s", theme.get("name", ""))

        # 4) Ready card
        img = self.create_gradient_background(theme, (width, height))
        draw = draw_card(img, border=True)
        ready_text = "Ready for the answer?"
        emoji_text = "Let's go!"
        r_bbox = draw.textbbox((0, 0), ready_text, font=title_font)
        e_bbox = draw.textbbox((0, 0), emoji_text, font=body_font)
        draw.text(((width - r_bbox[2]) // 2, content_y + 210), ready_text, font=title_font, fill=theme["accent"])
        draw.text(((width - e_bbox[2]) // 2, content_y + 330), emoji_text, font=body_font, fill=theme["text_secondary"])
        img.save(paths["ready"])
        logger.info("✅ Created transition ready for %s", theme.get("name", ""))

        return paths

    def render_welcome_cover(self, theme: Dict, output_path: Path, size: Tuple[int, int] = None, category: str = None) -> Path:
        """Render a welcome/cover image for mind_benders (supports reel and carousel sizes).
        
        Args:
            theme: Color theme dictionary
            output_path: Path to save the image
            size: Image size (defaults to REEL_SIZE)
            category: Question category to display on the welcome image
        """
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

        # Main headline (wrapped if needed)
        headline = "Can YOU solve this?"
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

        # Supporting line (wrapped if needed)
        subline = "Fresh brain teasers, daily."
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
        format_type = self._get_format(size)
        badge_text = "Keep watching for the challenge" if format_type == "reel" else "Swipe for the challenge →"
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
        logger.info(f"✅ Saved mind_benders welcome cover: {output_path}")
        return output_path

    def render_theme_cta(
        self,
        theme: Dict,
        reel_cta_path: Path,
        carousel_cta_path: Path,
    ) -> Dict[str, Path]:
        """Render CTA images for both reel and carousel formats into specific paths."""

        # Generate both formats (skip if file already exists at the provided path)
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

            title = "That’s the Answer"
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
                "Hope that one stretched your brain.",
                "Save & share if you liked it!",
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
            badge_text = "Follow for daily mind benders"
            badge_bbox = draw.textbbox((0, 0), badge_text, font=self.TEXT_FONT)
            badge_w = badge_bbox[2] - badge_bbox[0] + 80
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
                font=self.TEXT_FONT,
                fill=(255, 255, 255),
                anchor="mm",
            )

            canvas.save(path)
            logger.info(f"✅ Saved {format_name} CTA: {path}")

        return {"reel": reel_cta_path, "carousel": carousel_cta_path}

    def render_hint_card(self, question: dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None) -> Path:
        """Render hint/nudge card with ego-triggering psychology.
        
        Flow: welcome → puzzle → HINT (ego hook) → answer → cta
        Creates engagement by making users feel smart when hint helps them.
        """
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        format_type = self._get_format(size)
        layout = self._get_layout(size, "hint")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)

        # Main hint card
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']

        # Shadow effect
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

        # Ego-triggering hook
        ego_hooks = [
            "Getting close?",
            "Need a little nudge?",
            "Here's your hint...",
            "Still thinking? Let this help!",
            "You're almost there!",
        ]
        hook = random.choice(ego_hooks)
        hook_font = self.TITLE_FONT if format_type == "reel" else self.TEXT_FONT
        hook_lines = self._wrap_text_centered(hook, hook_font, card_w - 80)
        hook_line_spacing = 60 if format_type == "reel" else 48
        for line in hook_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=hook_font,
                fill=theme['accent'],
                anchor="mm"
            )
            y_pos += hook_line_spacing

        y_pos += 32 if format_type == "carousel" else 40

        # Mini puzzle (smaller, centered)
        puzzle_text = question.get('puzzle', '')
        if question.get('visual_elements'):
            puzzle_text += f"\n{question['visual_elements']}"
        
        # Use smaller font for carousel
        mini_puzzle_size = 48 if format_type == "carousel" else 52
        mini_puzzle_font = ImageFont.truetype(str(self.INTER_DIR / "Inter-SemiBold.ttf"), mini_puzzle_size)
        lines = puzzle_text.split('\n')
        puzzle_line_spacing = 62 if format_type == "carousel" else 70
        for line in lines:
            wrapped_lines = self._wrap_text_centered(line, mini_puzzle_font, card_w - 100)
            for wrapped_line in wrapped_lines:
                draw.text(
                    (center_x, y_pos),
                    wrapped_line,
                    font=mini_puzzle_font,
                    fill=theme['text_primary'],
                    anchor="mm"
                )
                y_pos += puzzle_line_spacing

        y_pos += 48 if format_type == "carousel" else 60

        # Divider line
        draw.line(
            [(card_x + 80, y_pos), (card_x + card_w - 80, y_pos)],
            fill=theme['accent'],
            width=2
        )
        y_pos += 48 if format_type == "carousel" else 60

        # Hint box (highlighted)
        hint_text = question.get('hint', '')
        if hint_text:
            # Hint background box (slightly lighter)
            hint_bg = tuple(min(c + 8, 255) for c in theme['card_bg'])
            hint_box_h = 160 if format_type == "carousel" else 200
            draw.rounded_rectangle(
                [card_x + 40, y_pos, card_x + card_w - 40, y_pos + hint_box_h],
                radius=24,
                fill=hint_bg,
                outline=theme['accent'],
                width=2
            )

            # Hint text (wrapped and centered)
            hint_font = self.TEXT_FONT
            hint_lines = self._wrap_text_centered(hint_text, hint_font, card_w - 100)
            hint_y = y_pos + (36 if format_type == "carousel" else 50)
            hint_line_spacing = 42 if format_type == "carousel" else 50
            for line in hint_lines:
                draw.text(
                    (center_x, hint_y),
                    line,
                    font=hint_font,
                    fill=theme['text_primary'],
                    anchor="mm"
                )
                hint_y += hint_line_spacing

            y_pos += hint_box_h + (60 if format_type == "carousel" else 80)

        # CTA swipe prompt (format-specific)
        cta_text = "Keep watching to reveal the answer" if format_type == "reel" else "Swipe to reveal the answer →"
        cta_lines = self._wrap_text_centered(cta_text, self.TEXT_FONT, card_w - 80)
        cta_line_spacing = 48 if format_type == "carousel" else 60
        for line in cta_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TEXT_FONT,
                fill=theme['accent'],
                anchor="mm"
            )
            y_pos += cta_line_spacing

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path)
        logger.info(f"✅ Saved hint card: {output_path}")
        return output_path
    
    def render_puzzle_card(self, question: dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None):
        """Render puzzle question card (supports reel and carousel sizes)."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        format_type = self._get_format(size)
        layout = self._get_layout(size, "puzzle")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)
        
        # Centered white card with shadow
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']
        
        # Shadow effect
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [card_x + 10, card_y + 10, card_x + card_w + 10, card_y + card_h + 10],
            radius=40,
            fill=(0, 0, 0, 60)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(layout['shadow_blur']))
        canvas.paste(shadow, (0, 0), shadow)
        
        # Main card
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=40,
            fill=theme['puzzle_box']
        )
        
        # Content positioning
        y_pos = card_y + layout['content_y']
        center_x = width // 2
        
        # Category badge
        category = question.get('category', 'puzzle').replace('_', ' ').title()
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
        
        y_pos += badge_h + (50 if format_type == "carousel" else 58)
        
        # Puzzle text (large, centered) - with wrapping
        puzzle_font = self.PUZZLE_FONT if format_type == "reel" else self.PUZZLE_FONT_CAROUSEL
        puzzle_text = question.get('puzzle', '')
        if question.get('visual_elements'):
            puzzle_text += f"\n{question['visual_elements']}"
        
        lines = puzzle_text.split('\n')
        for text_line in lines:
            wrapped = self._wrap_text_centered(text_line, puzzle_font, card_w - 100)
            for line in wrapped:
                draw.text(
                    (center_x, y_pos),
                    line,
                    font=puzzle_font,
                    fill=theme['text_primary'],
                    anchor="mm"
                )
                y_pos += 60 if format_type == "carousel" else 66
        
        y_pos += 30
        
        # Question (wrapped if needed) - adjust spacing based on number of lines
        question_text = question['question']
        question_lines = self._wrap_text_centered(question_text, self.TEXT_FONT, card_w - 100)
        
        # Calculate space needed for options (2x2 grid + spacing)
        row_height = 100 if format_type == "carousel" else 120
        row_spacing = 24 if format_type == "carousel" else 28
        options_grid_height = (row_height * 2) + row_spacing
        
        # Calculate available space for question
        card_bottom = card_y + card_h - 38  # Leave 38px margin at bottom
        available_space = card_bottom - y_pos
        space_for_question = available_space - options_grid_height - 38  # 38px spacing before options
        
        # Dynamically adjust question line spacing based on available space
        question_line_spacing = max(36, space_for_question // max(len(question_lines), 1) - 10)
        question_line_spacing = min(54, question_line_spacing)  # Cap at 54 max
        
        for line in question_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.TEXT_FONT,
                fill=theme['text_secondary'],
                anchor="mm"
            )
            y_pos += question_line_spacing

        y_pos += 18
        
        # Options (A, B, C, D in grid)
        option_labels = ['A', 'B', 'C', 'D']
        options = question['options']
        
        # 2x2 grid
        grid_start_y = y_pos
        col_width = (card_w - 120) // 2
        
        for idx, (label, option) in enumerate(zip(option_labels, options)):
            row = idx // 2
            col = idx % 2
            
            opt_x = card_x + 60 + (col * (col_width + 40))
            opt_y = grid_start_y + (row * (row_height + row_spacing))
            
            # Option box
            draw.rounded_rectangle(
                [opt_x, opt_y, opt_x + col_width, opt_y + row_height],
                radius=20,
                fill=theme['card_bg']
            )
            
            # Label circle
            circle_r = 22 if format_type == "carousel" else 25
            circle_x = opt_x + 30
            circle_y = opt_y + row_height // 2
            draw.ellipse(
                [circle_x - circle_r, circle_y - circle_r,
                 circle_x + circle_r, circle_y + circle_r],
                fill=theme['accent']
            )
            draw.text(
                (circle_x, circle_y),
                label,
                font=self.TEXT_FONT,
                fill=(255, 255, 255),
                anchor="mm"
            )
            
            # Option text (wrapped to fit in box)
            text_x = opt_x + 80
            available_width = (col_width - 100)  # Space after label circle + margins
            option_font = self.OPTION_FONT if format_type == "reel" else self.OPTION_FONT_CAROUSEL
            option_wrapped = self._wrap_text(option, option_font, available_width)
            opt_text_y = opt_y + row_height // 2 - ((len(option_wrapped) - 1) * 20)  # Center multi-line text
            for opt_line in option_wrapped[:2]:  # Max 2 lines per option
                draw.text(
                    (text_x, opt_text_y),
                    opt_line,
                    font=option_font,
                    fill=theme['text_primary'],
                    anchor="lm"
                )
                opt_text_y += 40
        
        canvas.save(output_path)
        logger.info(f"✅ Saved puzzle card: {output_path}")
        return output_path
    
    def render_answer_card(self, question: dict, theme: Dict, output_path: Path, size: Tuple[int, int] = None):
        """Render answer reveal card with celebration (supports reel and carousel sizes)."""
        if size is None:
            size = self.REEL_SIZE
        width, height = size
        layout = self._get_layout(size, "answer")
        
        canvas = self.create_gradient_background(theme, size)
        draw = ImageDraw.Draw(canvas)
        
        # Similar card structure
        card_margin = layout['card_margin']
        card_x = card_margin
        card_y = (height - layout['card_h']) // 2
        card_w = width - (card_margin * 2)
        card_h = layout['card_h']
        
        # Shadow + Card (same as puzzle)
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
        
        # "Answer" header
        answer_header = "Answer"
        draw.text(
            (center_x, y_pos),
            answer_header,
            font=self.TITLE_FONT,
            fill=theme['accent'],
            anchor="mm"
        )
        y_pos += 120
        
        # Correct answer (huge, wrapped if needed)
        correct_label = question['correct']
        correct_option = question['options'][ord(correct_label) - ord('A')]
        
        answer_lines = self._wrap_text_centered(correct_option, self.PUZZLE_FONT, card_w - 100)
        for line in answer_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.PUZZLE_FONT,
                fill=theme['text_primary'],
                anchor="mm"
            )
            y_pos += 150
        
        # Explanation (wrapped text)
        explanation = question['explanation']
        wrapped_lines = self._wrap_text(explanation, self.EXPLANATION_FONT, card_w - 100)
        
        for line in wrapped_lines:
            draw.text(
                (center_x, y_pos),
                line,
                font=self.EXPLANATION_FONT,
                fill=theme['text_secondary'],
                anchor="mm"
            )
            y_pos += 55
        
        # Fun fact (if exists, wrapped)
        if question.get('fun_fact'):
            y_pos += 60
            fun_fact_text = f"Fun Fact: {question['fun_fact']}"
            fun_fact_lines = self._wrap_text_centered(fun_fact_text, self.TEXT_FONT, card_w - 100)
            for line in fun_fact_lines:
                draw.text(
                    (center_x, y_pos),
                    line,
                    font=self.TEXT_FONT,
                    fill=theme['accent'],
                    anchor="mm"
                )
                y_pos += 50
        
        canvas.save(output_path)
        logger.info(f"✅ Saved answer card: {output_path}")
        return output_path
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width. Left-aligned wrapper."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _wrap_text_centered(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text for centered alignment. Returns lines that will fit within max_width."""
        # For single-line text that fits, return as-is
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_width:
            return [text]
        
        # Multi-word text: wrap intelligently
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]