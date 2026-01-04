import logging
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pybender.generator.schema import Question
from pybender.render.code_renderer import draw_editor_code_with_ide
from pybender.render.render_mode import RenderMode
from pybender.render.text_utils import normalize_code, wrap_code_line, wrap_text, wrap_text_with_prefix
from pybender.config.logging_config import setup_logging
logger = logging.getLogger(__name__)

def _ensure_logging_configured() -> None:
    if not logging.getLogger().handlers:
        setup_logging()

class TechContentRenderer:
    _ensure_logging_configured()
    def __init__(self):
        # Canvas
        self.WIDTH, self.HEIGHT = 1080, 1920
        self.PADDING_X = 60

        # Colors (match CTA theme)
        self.BG_COLOR = (9, 12, 24)
        self.CARD_COLOR = (11, 18, 32)
        self.CODE_BG = (16, 24, 40)
        self.TEXT_COLOR = (226, 232, 240)
        self.SUBTLE_TEXT = (131, 145, 161)
        self.ACCENT_COLOR = (76, 201, 240)
        self.CORRECT_BG = (20, 45, 70)
        self.SUCCESS_COLOR = (52, 211, 153)
        self.SUBJECT_ACCENTS = {
            "python": (19, 88, 174),      # cyan
            "sql": (88, 157, 246),         # azure
            "regex": (255, 107, 107),       # amber
            "linux": (72, 187, 120),       # green
            "javascript": (255, 223, 99),  # gold
            "rust": (237, 125, 49),        # orange
            "system_design": (129, 140, 248),  # indigo
            "docker_k8s": (59, 130, 246),      # kubernetes blue
            "golang": (0, 173, 216),           # go cyan
        }
        
        # Fonts
        self.FONT_DIR = Path("pybender/assets/fonts")
        self.INTER_FONT_DIR = self.FONT_DIR / "Inter-4.1" / "extras" / "ttf"
        self.JETBRAINS_MONO_FONT_DIR = self.FONT_DIR / "JetBrainsMono-2.304" / "fonts" / "ttf"
        self.TITLE_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 48)
        self.TEXT_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 38)
        self.CODE_FONT = ImageFont.truetype(str(self.JETBRAINS_MONO_FONT_DIR / "JetBrainsMono-Regular.ttf"), 38)
        self.HEADER_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 44)
        self.FOOTER_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 44) 
        self.SMALL_LABEL_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 38)

        # Logo config
        self.ASSETS_DIR = Path("pybender/assets/backgrounds")
        self.LOGO_PATH = self.ASSETS_DIR / "ddop1.PNG"
        self.DEFAULT_OVERLAY_PATH = self.ASSETS_DIR / "ddop3.PNG"
        self.LOGO_HEIGHT = 40  # 40x120 pixels
        self.LOGO_WIDTH = 60  # 40x120 pixels
        self.LOGO_PADDING = 20  # 20px from edges

        # IDE-style code config
        self.IDE_CODE_STYLE = True  # Set to False to use plain code blocks
        self.IDE_HEADER_HEIGHT = 36
        self.IDE_GUTTER_WIDTH = 45
        self.IDE_HEADER_BG = (20, 26, 40)  # Darker than CODE_BG
        self.IDE_GUTTER_BG = (13, 19, 36)  # Even darker
        self.IDE_LINE_NUMBER_COLOR = (100, 116, 139)  # Subtle gray
        self.LANGUAGE_MAP = {
            "python": "Python",
            "javascript": "JavaScript",
            "rust": "Rust",
            "golang": "Go",
            "sql": "SQL",
            "regex": "Regex",
            "system_design": "Design",
            "docker_k8s": "YAML",
            "linux": "Bash",
        }

    # ---------- BASE CANVAS ----------
    def _create_base_canvas(self, subject: str) -> Image.Image:
        canvas = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        self.draw = ImageDraw.Draw(canvas)
        
        # Main Card
        card_x, card_y = 40, 80
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120
        radius = 28

        self.draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            fill=self.CARD_COLOR
        )

        self.y_cursor = card_y + 40
        self.content_x = card_x + 40
        self.max_width = card_w - 80
        self.ACCENT_COLOR = self.SUBJECT_ACCENTS.get(
            subject, self.ACCENT_COLOR
            )

        
        return canvas

    # ---------- HEADER ----------
    def _draw_header(self, canvas, text: str):
        bbox = self.draw.textbbox((0, 0), text, font=self.HEADER_FONT)
        x = (self.WIDTH - bbox[2]) // 2
        self.draw.text((x, self.y_cursor), text, font=self.HEADER_FONT, fill=self.SUBTLE_TEXT)
        self.y_cursor += bbox[3] + 30

    # --------- TITLE ----------
    def _draw_title(self, title: str):
        bbox = self.draw.textbbox((0, 0), title, font=self.TITLE_FONT)
        x = (self.WIDTH - bbox[2]) // 2
        self.draw.text((x, self.y_cursor), title, font=self.TITLE_FONT, fill=self.ACCENT_COLOR)
        self.y_cursor += bbox[3] + 30

    # ---------- SCENARIO (STYLED) - docker & system design ----------
    def _draw_scenario_styled(self, canvas, scenario_text: str, prefix: str = "Q:"):
        """
        Draw scenario with clean, subtle styling - minimal and modern.
        Features:
        - Slightly lighter background (subtle elevation)
        - Thin accent border (cleaner than heavy bar)
        - No competing visual elements with options
        - Compact and professional
        """
        scenario_text = scenario_text.replace("\\n", " ")
        
        # Measure the prefix in pixels and wrap the first line using the reduced width.
        prefix_width = self.draw.textlength(f"{prefix} ", font=self.TEXT_FONT)
        lines = wrap_text_with_prefix(
            self.draw,
            scenario_text,
            self.TEXT_FONT,
            self.max_width,
            prefix_width,
        )
        
        # Configuration
        scenario_padding = 16
        
        # Calculate block height - match plain version height
        block_height = len(lines) * 50 + scenario_padding * 2
        
        # Draw slightly lighter background (subtle elevation effect)
        lighter_bg = tuple(min(c + 4, 255) for c in self.CARD_COLOR)
        self.draw.rounded_rectangle(
            [
                self.content_x - 10,
                self.y_cursor,
                self.WIDTH - self.content_x + 10,
                self.y_cursor + block_height,
            ],
            radius=16,
            fill=lighter_bg,
        )
        
        # Draw thin accent border (cleaner than bar)
        self.draw.rounded_rectangle(
            [
                self.content_x - 10,
                self.y_cursor,
                self.WIDTH - self.content_x + 10,
                self.y_cursor + block_height,
            ],
            radius=16,
            outline=self.ACCENT_COLOR,
            width=1,
        )
        
        # Draw text lines with proper alignment
        text_y = self.y_cursor + scenario_padding
        for i, line in enumerate(lines):
            line_prefix = f"{prefix} " if i == 0 else ""
            if line_prefix:
                # Draw prefix in accent color
                self.draw.text(
                    (self.content_x + 8, text_y),
                    line_prefix,
                    font=self.TEXT_FONT,
                    fill=self.ACCENT_COLOR
                )
                # Draw rest of line in regular text color
                prefix_pixel_width = self.draw.textlength(line_prefix, font=self.TEXT_FONT)
                self.draw.text(
                    (self.content_x + 8 + prefix_pixel_width, text_y),
                    line,
                    font=self.TEXT_FONT,
                    fill=self.TEXT_COLOR
                )
            else:
                self.draw.text(
                    (self.content_x + 8, text_y),
                    line,
                    font=self.TEXT_FONT,
                    fill=self.TEXT_COLOR
                )
            text_y += 50
        

        self.y_cursor += block_height + 20

    def _draw_editor_code(self, canvas, code: str): # Plain code block without IDE styling - not active
        font = self.CODE_FONT
        line_height = 48
        max_width = self.WIDTH - (self.PADDING_X * 2) - 40

        # -------- Measure total height first --------
        wrapped_lines = []
        for line in code:
            wrapped = wrap_code_line(self.draw, line, font, max_width)
            wrapped_lines.extend(wrapped)

        block_height = len(wrapped_lines) * line_height + 30

        # -------- Background --------
        self.draw.rounded_rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.WIDTH - self.PADDING_X,
                self.y_cursor + block_height,
            ],
            radius=18,
            fill=self.CODE_BG,
        )

        # -------- Accent bar --------
        self.draw.rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.PADDING_X + 6,
                self.y_cursor + block_height,
            ],
            fill=self.ACCENT_COLOR,
        )

        # -------- Draw code text --------
        text_x = self.PADDING_X + 20
        text_y = self.y_cursor + 15

        for wline in wrapped_lines:
            self.draw.text(
                (text_x, text_y),
                wline,
                font=font,
                fill=self.TEXT_COLOR,
            )
            text_y += line_height

        self.y_cursor += block_height + 20

    def _draw_terminal_code(self, canvas, code: str):
        font = self.CODE_FONT
        line_height = 48
        max_width = self.WIDTH - (self.PADDING_X * 2) - 40
        terminal_padding = 20
        
        # Terminal colors (Linux/Ubuntu style)
        TERMINAL_BG = (24, 24, 24)  # Dark gray/black
        TERMINAL_BORDER = (51, 51, 51)  # Slightly lighter for border
        TERMINAL_GREEN = (166, 226, 46)  # Command prompt green
        TERMINAL_HEADER_BG = (40, 40, 40)  # Header bar color
        TERMINAL_DOT_CLOSE = (255, 95, 86)  # Red dot
        TERMINAL_DOT_MINIMIZE = (255, 189, 46)  # Yellow dot
        TERMINAL_DOT_MAXIMIZE = (40, 201, 64)  # Green dot
        
        bg_height_start = self.y_cursor
        
        # Calculate total height needed
        wrapped_lines = []
        for line in code:
            line = line.strip()
            if line:
                line = f"$ {line}"
            wrapped = wrap_code_line(self.draw, line, font, max_width)
            wrapped_lines.extend(wrapped)
        
        # Terminal block dimensions
        header_height = 40
        content_height = len(wrapped_lines) * line_height + terminal_padding * 2
        total_height = header_height + content_height
        
        # Draw main terminal background
        self.draw.rounded_rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.WIDTH - self.PADDING_X,
                self.y_cursor + total_height,
            ],
            radius=12,
            fill=TERMINAL_BG,
            outline=TERMINAL_BORDER,
            width=2
        )
        
        # Draw terminal header bar (like Ubuntu terminal)
        self.draw.rounded_rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.WIDTH - self.PADDING_X,
                self.y_cursor + header_height,
            ],
            radius=12,
            fill=TERMINAL_HEADER_BG
        )
        
        # Draw window control dots (macOS/Ubuntu style)
        dot_y = self.y_cursor + header_height // 2
        dot_radius = 6
        dot_spacing = 20
        start_x = self.PADDING_X + 16
        
        # Close (red)
        self.draw.ellipse(
            [start_x, dot_y - dot_radius, start_x + dot_radius * 2, dot_y + dot_radius],
            fill=TERMINAL_DOT_CLOSE
        )
        # Minimize (yellow)
        self.draw.ellipse(
            [start_x + dot_spacing, dot_y - dot_radius, start_x + dot_spacing + dot_radius * 2, dot_y + dot_radius],
            fill=TERMINAL_DOT_MINIMIZE
        )
        # Maximize (green)
        self.draw.ellipse(
            [start_x + dot_spacing * 2, dot_y - dot_radius, start_x + dot_spacing * 2 + dot_radius * 2, dot_y + dot_radius],
            fill=TERMINAL_DOT_MAXIMIZE
        )
        
        # Optional: Terminal title
        title_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 28)
        title = "terminal"
        title_bbox = self.draw.textbbox((0, 0), title, font=title_font)
        title_x = (self.WIDTH - (title_bbox[2] - title_bbox[0])) // 2
        self.draw.text(
            (title_x, self.y_cursor + 8),
            title,
            font=title_font,
            fill=(160, 160, 160)
        )
        
        # Move cursor past header
        self.y_cursor += header_height + terminal_padding
        
        # Draw terminal commands
        text_x = self.PADDING_X + terminal_padding
        for wline in wrapped_lines:
            self.draw.text(
                (text_x, self.y_cursor),
                wline,
                font=font,
                fill=TERMINAL_GREEN,
            )
            self.y_cursor += line_height
        
        # Add bottom padding
        self.y_cursor += terminal_padding + 20

    def _draw_code(self, canvas, code, code_style: str | None, subject: str | None = None):
        if code_style is None:
            return

        # Normalize code first (fix \t and escaped \n)
        code = normalize_code(code)

        if code_style == "terminal": # linux - terminal commands -fixed
            self._draw_terminal_code(canvas, code)
        elif code_style == "editor":
            # Use IDE-style if enabled and subject provided
            if self.IDE_CODE_STYLE and subject:
                self.y_cursor = draw_editor_code_with_ide(
                    draw=self.draw,
                    code=code,
                    subject=subject,
                    y_cursor=self.y_cursor,
                    width=self.WIDTH,
                    padding_x=self.PADDING_X,
                    code_font=self.CODE_FONT,
                    small_label_font=self.SMALL_LABEL_FONT,
                    code_bg=self.CODE_BG,
                    ide_header_bg=self.IDE_HEADER_BG,
                    ide_gutter_bg=self.IDE_GUTTER_BG,
                    text_color=self.TEXT_COLOR,
                    subtle_text=self.SUBTLE_TEXT,
                    ide_line_number_color=self.IDE_LINE_NUMBER_COLOR,
                    language_map=self.LANGUAGE_MAP,
                    ide_gutter_width=self.IDE_GUTTER_WIDTH,
                    ide_header_height=self.IDE_HEADER_HEIGHT,
                    line_height=48
                )
            else:
                self._draw_editor_code(canvas, code)
        else:
            # default editor style - all programming languages + system design + docker_k8s
            if self.IDE_CODE_STYLE and subject:
                self.y_cursor = draw_editor_code_with_ide(
                    draw=self.draw,
                    code=code,
                    subject=subject,
                    y_cursor=self.y_cursor,
                    width=self.WIDTH,
                    padding_x=self.PADDING_X,
                    code_font=self.CODE_FONT,
                    small_label_font=self.SMALL_LABEL_FONT,
                    code_bg=self.CODE_BG,
                    ide_header_bg=self.IDE_HEADER_BG,
                    ide_gutter_bg=self.IDE_GUTTER_BG,
                    text_color=self.TEXT_COLOR,
                    subtle_text=self.SUBTLE_TEXT,
                    ide_line_number_color=self.IDE_LINE_NUMBER_COLOR,
                    language_map=self.LANGUAGE_MAP,
                    ide_gutter_width=self.IDE_GUTTER_WIDTH,
                    ide_header_height=self.IDE_HEADER_HEIGHT,
                    line_height=48
                )
            else:
                self._draw_editor_code(canvas, code)

    # ---------- OPTIONS (UNIFIED) ----------
    def _draw_options_v2(self, canvas, options: list[str], mode: RenderMode, correct: str = None):
        """
        Unified options rendering function supporting three modes:
        - RenderMode.QUESTION: Show all options without highlighting
        - RenderMode.SINGLE: Show all options with correct one highlighted in green
        - RenderMode.ANSWER: Show only the correct option highlighted in green
        
        Args:
            canvas: PIL Image canvas to draw on
            options: List of option text strings
            mode: RenderMode enum (QUESTION, SINGLE, or ANSWER)
            correct: Correct answer letter (A/B/C/D) - required for SINGLE and ANSWER modes
        """
        draw = self.draw
        font = self.TEXT_FONT
        max_width = self.WIDTH - (self.PADDING_X * 2)
        line_height = 32
        padding = 18
        option_gap = 14

        correct_idx = ord(correct.upper()) - 65 if correct else -1

        # Determine which options to display
        options_to_display = options if mode != RenderMode.SINGLE else [options[correct_idx]]
        start_idx = 0 if mode != RenderMode.SINGLE else correct_idx

        for display_idx, opt in enumerate(options_to_display):
            idx = start_idx + display_idx if mode == RenderMode.ANSWER else display_idx
            
            # Normalize escaped newlines
            opt = opt.replace("\\n", "\n")
            raw_lines = opt.split("\n")
            wrapped = []

            for line in raw_lines:
                wrapped.extend(
                    wrap_text(draw, line, font, max_width - 60)
                )

            block_height = len(wrapped) * line_height + padding * 2

            # Determine colors based on mode
            is_correct = (idx == correct_idx)
            
            if mode == RenderMode.QUESTION:
                # All options same styling
                bg = self.CARD_COLOR
                accent = self.ACCENT_COLOR
            elif mode == RenderMode.ANSWER:
                # Highlight correct answer in green
                bg = self.CORRECT_BG if is_correct else self.CARD_COLOR
                accent = self.SUCCESS_COLOR if is_correct else self.ACCENT_COLOR
            else:  # RenderMode.SINGLE
                # Only showing correct answer, always green
                bg = self.CORRECT_BG
                accent = self.SUCCESS_COLOR

            # Draw background card
            self.draw.rounded_rectangle(
                [
                    self.PADDING_X - 10,
                    self.y_cursor,
                    self.WIDTH - self.PADDING_X + 10,
                    self.y_cursor + block_height,
                ],
                radius=18,
                fill=bg,
            )

            # Draw accent bar on the left
            self.draw.rectangle(
                [
                    self.PADDING_X - 10,
                    self.y_cursor,
                    self.PADDING_X - 4,
                    self.y_cursor + block_height,
                ],
                fill=accent,
            )

            # Draw text lines
            text_y = self.y_cursor + padding
            for i, line in enumerate(wrapped):
                prefix = f"{chr(65 + idx)}. " if i == 0 else "    "
                self.draw.text(
                    (self.PADDING_X, text_y),
                    prefix + line,
                    font=font,
                    fill=self.TEXT_COLOR,
                )
                text_y += line_height

            self.y_cursor += block_height + option_gap

        self.y_cursor += 20

    # ---------- EXPLANATION ----------
    def _draw_explanation(self, canvas, explanation: str):
        font = self.TEXT_FONT
        max_width = self.WIDTH - (self.PADDING_X * 2)

        explanation = explanation.replace("\\n", " ")
        lines = wrap_text(self.draw, explanation, font, max_width)

        self.draw.line(
            [(self.PADDING_X, self.y_cursor),
            (self.WIDTH - self.PADDING_X, self.y_cursor)],
            fill=self.ACCENT_COLOR,
            width=2,
        )
        self.y_cursor += 18

        # Draw "Explanation:" in accent color
        self.draw.text(
            (self.PADDING_X, self.y_cursor),
            "Explanation: ",
            font=self.TEXT_FONT,
            fill=self.ACCENT_COLOR
        )
        self.y_cursor += 55

        for line in lines:
            self.draw.text(
                (self.PADDING_X, self.y_cursor),
                line,
                font=font,
                fill=self.SUBTLE_TEXT,
            )
            self.y_cursor += 50

    # ---------- FOOTER ----------
    def _draw_footer(self, canvas, subject: str):
        text = f"Follow for daily {subject}"
        bbox = self.draw.textbbox((0, 0), text, font=self.HEADER_FONT)
        x = (self.WIDTH - bbox[2]) // 2
        self.draw.text(
            (x, self.HEIGHT - 100),
            text,
            font=self.FOOTER_FONT,
            fill=self.SUBTLE_TEXT,
        )

    # ---------- LOGO ----------
    def _draw_logo(self, canvas):
        """
        Draw DDOP logo in the bottom-right corner of the card.
        Logo has transparent background, no shadow added.
        """
        if not self.LOGO_PATH.exists():
            return canvas

        # Card bounds
        card_x, card_y = 40, 80
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120

        # Load and resize logo
        try:
            logo = Image.open(self.LOGO_PATH).convert("RGBA")
            logo = logo.resize((self.LOGO_WIDTH, self.LOGO_HEIGHT), Image.Resampling.LANCZOS)
        except Exception as e:
            logger.warning("Could not load logo: %s", e)
            return canvas

        # Position: bottom-right corner of card with padding
        logo_x = card_x + card_w - self.LOGO_WIDTH - self.LOGO_PADDING
        logo_y = card_y + card_h - self.LOGO_HEIGHT - self.LOGO_PADDING

        # Apply slight transparency to logo (75% opacity)
        logo.putalpha(int(255 * 0.75))

        # Composite logo directly onto canvas
        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.paste(logo, (logo_x, logo_y), logo)

        return canvas_rgba.convert("RGB")

    # ---------- WATERMARK ----------
    def _draw_watermark(self, canvas):
        """
        Draw a subtle tiled diagonal watermark across the card area.
        Uses 'DDOP' text with low opacity (~12-18%) to make removal difficult.
        """
        # Card bounds (from _create_base_canvas)
        card_x, card_y = 40, 80
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120

        # Watermark config
        watermark_text = "DDOP"
        watermark_font = ImageFont.truetype(
            str(self.JETBRAINS_MONO_FONT_DIR / "JetBrainsMono-Regular.ttf"), 72
        )
        base_opacity = 54  # Base alpha value (out of 255)
        tile_spacing_x = 220  # Horizontal spacing between tiles
        tile_spacing_y = 180  # Vertical spacing between tiles
        rotation_angle = -30  # Diagonal tilt in degrees

        # Create a transparent overlay for the watermark
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Tile the watermark across the card area
        for y in range(card_y, card_y + card_h, tile_spacing_y):
            for x in range(card_x, card_x + card_w, tile_spacing_x):
                # Add slight opacity jitter (±3 alpha) for each tile
                alpha = base_opacity + random.randint(-3, 3)
                alpha = max(8, min(255, alpha))  # Clamp between 8-255

                # Create a temporary image for rotated text
                text_bbox = overlay_draw.textbbox((0, 0), watermark_text, font=watermark_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Create text image with padding for rotation
                text_img = Image.new("RGBA", (text_width + 40, text_height + 40), (0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_img)
                text_draw.text(
                    (20, 20),
                    watermark_text,
                    font=watermark_font,
                    fill=(255, 255, 255, alpha)
                )

                # Rotate the text
                rotated = text_img.rotate(rotation_angle, expand=True)

                # Paste onto overlay at tile position
                overlay.paste(rotated, (x, y), rotated)

        # Composite watermark onto canvas and return modified canvas
        canvas_rgba = canvas.convert("RGBA")
        watermarked = Image.alpha_composite(canvas_rgba, overlay)
        return watermarked.convert("RGB")

    def render_cta_image(self, subject: str, out_path: Path) -> None:
        """
        Render a reusable Call-To-Action image (dark theme).
        Saved once and reused for all reels.
        """
        if out_path.exists():
            logger.info("CTA image already exists at %s", out_path)
            return

        TITLE_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 84)
        TEXT_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 48)
        SUBTLE_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 42)

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # CTA Card
        # --------------------------------------------------
        card_w, card_h = 920, 640
        card_x = (self.WIDTH - card_w) // 2
        card_y = (self.HEIGHT - card_h) // 2

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=32,
            fill=self.CARD_COLOR
        )

        content_x = card_x + 60
        y = card_y + 90

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title = "That’s the Answer"
        tw = draw.textbbox((0, 0), title, font=TITLE_FONT)[2]
        draw.text(
            (card_x + (card_w - tw) // 2, y),
            title,
            font=TITLE_FONT,
            fill= self.SUBJECT_ACCENTS.get(subject, self.ACCENT_COLOR)
        )
        y += 120

        # --------------------------------------------------
        # Body
        # --------------------------------------------------
        body_lines = [
            "Hope that one made you think.",
            "",
            "Follow for daily",
            f"{subject.replace('_', ' ').title()} tricky questions."
        ]

        for line in body_lines:
            lw = draw.textbbox((0, 0), line, font=TEXT_FONT)[2]
            draw.text(
                (card_x + (card_w - lw) // 2, y),
                line,
                font=TEXT_FONT,
                fill=self.TEXT_COLOR
            )
            y += 64

        y += 40

        # --------------------------------------------------
        # Subtle Footer
        # --------------------------------------------------
        footer = "Save & share if this helped"
        fw = draw.textbbox((0, 0), footer, font=SUBTLE_FONT)[2]
        draw.text(
            (card_x + (card_w - fw) // 2, y),
            footer,
            font=SUBTLE_FONT,
            fill=self.SUBTLE_TEXT
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        logger.info("CTA image saved → %s", out_path)

    def render_welcome_image(self, subject: str, out_path: Path) -> None:
        """
        Render a welcome image: 'Welcome to Daily Dose of Python'
        """
        
        if out_path.exists():
            logger.info("Welcome image already exists at %s", out_path)
            return

        overlay_path = self.ASSETS_DIR / "overlays" / f"{subject}_img_new.png"
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Main Card
        # --------------------------------------------------
        card_x, card_y = 60, 220
        card_w, card_h = self.WIDTH - 120, self.HEIGHT - 440
        accent_color = self.SUBJECT_ACCENTS.get(subject, self.ACCENT_COLOR)

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=32,
            fill=self.CARD_COLOR
        )

        content_x = card_x + 60
        max_width = card_w - 120
        y = card_y + 220

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title = "Welcome to"
        tw = draw.textbbox((0, 0), title, font=self.TITLE_FONT)[2]
        draw.text(
            (content_x + (max_width - tw) // 2, y),
            title,
            font=self.TITLE_FONT,
            fill=self.SUBTLE_TEXT
        )
        y += 70

        # --------------------------------------------------
        # Brand Name
        # --------------------------------------------------
        brand = f"Daily Dose of {subject.replace('_', ' ').title()}"
        bw = draw.textbbox((0, 0), brand, font=self.TITLE_FONT)[2]
        draw.text(
            (content_x + (max_width - bw) // 2, y),
            brand,
            font=self.TITLE_FONT,
            fill=accent_color
        )
        y += 90

        # --------------------------------------------------
        # Divider
        # --------------------------------------------------
        draw.line(
            [content_x + 120, y, content_x + max_width - 120, y],
            fill=accent_color,
            width=2
        )
        y += 150

        # --------------------------------------------------
        # Subtitle
        # --------------------------------------------------
        subtitle = f"Bite-sized {subject.replace('_', ' ').title()} challenges.\nThink. Comment. Learn."
        for line in subtitle.split("\n"):
            lw = draw.textbbox((0, 0), line, font=self.TITLE_FONT)[2]
            draw.text(
                (content_x + (max_width - lw) // 2, y),
                line,
                font=self.TITLE_FONT,
                fill=self.TEXT_COLOR
            )
            y += 70

        # --------------------------------------------------
        # Overlay Image
        # --------------------------------------------------
        overlay_h = 0
        if overlay_path.exists():
            overlay = Image.open(overlay_path).convert("RGBA")
            overlay_w, overlay_h = 600, 600
            overlay_resized = overlay.resize((overlay_w, overlay_h), Image.Resampling.LANCZOS)
            overlay_x = (self.WIDTH - overlay_w) // 2
            overlay_y = y + 20
            img.paste(overlay_resized, (overlay_x, overlay_y), overlay_resized)
        else:
            # Fallback to default overlay if subject-specific doesn't exist
            default_overlay_path = self.DEFAULT_OVERLAY_PATH
            if default_overlay_path.exists():
                overlay = Image.open(default_overlay_path).convert("RGBA")
                overlay_w, overlay_h = 600, 600
                overlay_resized = overlay.resize((overlay_w, overlay_h), Image.Resampling.LANCZOS)
                overlay_x = (self.WIDTH - overlay_w) // 2
                overlay_y = y + 20
                img.paste(overlay_resized, (overlay_x, overlay_y), overlay_resized)
        y += overlay_h + 60  # Adjust y position for footer text

        # --------------------------------------------------
        # Footer Text
        # --------------------------------------------------
        footer = "New challenges every day"
        fb = draw.textbbox((0, 0), footer, font=self.TITLE_FONT)
        fw = fb[2] - fb[0]
        draw.text(
            (content_x + (max_width - fw) // 2, y),
            footer,
            font=self.TITLE_FONT,
            fill=self.SUBTLE_TEXT
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        logger.info("Welcome image saved → %s", out_path)

    def render_transition_sequence(self, subject, transition_dir) -> dict:
        """
        Generate a reusable countdown transition sequence (4 images).
        Used for combined reel strategy with 2-second countdown timer.
        
        Returns dict with paths to all 4 transition images:
        {
            "base": Path to "Want to guess?" image (0.6s),
            "2": Path to "2" countdown image (0.6s),
            "1": Path to "1" countdown image (0.6s),
            "ready": Path to "Ready for the answer?" image (0.2s)
        }
        
        Total duration: 2 seconds
        """
        transition_dir.mkdir(parents=True, exist_ok=True)
        
        transition_paths = {
            "base": transition_dir / "transition_base.png",
            "2": transition_dir / "transition_2.png",
            "1": transition_dir / "transition_1.png",
            "ready": transition_dir / "transition_ready.png",
        }
        
        # Check if all images already exist
        if all(p.exists() for p in transition_paths.values()):
            logger.info("✅ Transition sequence already exists")
            return transition_paths
        
        # --------------------------------------------------
        # 1. Base: "Want to guess?"
        # --------------------------------------------------
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        content_w, content_h = 800, 600
        content_x = (self.WIDTH - content_w) // 2
        content_y = (self.HEIGHT - content_h) // 2
        
        # Background card
        draw.rounded_rectangle(
            [content_x, content_y, content_x + content_w, content_y + content_h],
            radius=32,
            fill=self.CARD_COLOR
        )
        draw.rounded_rectangle(
            [content_x, content_y, content_x + content_w, content_y + content_h],
            radius=32,
            outline=self.ACCENT_COLOR,
            width=2
        )
        
        # Main text
        main_text = "Want to guess?"
        main_bbox = draw.textbbox((0, 0), main_text, font=self.TITLE_FONT)
        main_w = main_bbox[2] - main_bbox[0]
        main_x = (self.WIDTH - main_w) // 2
        main_y = content_y + 150
        
        draw.text((main_x, main_y), main_text, font=self.TITLE_FONT, fill=self.ACCENT_COLOR)
        
        # Subtitle
        subtitle = "Pause the video and think..."
        sub_bbox = draw.textbbox((0, 0), subtitle, font=self.TEXT_FONT)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_x = (self.WIDTH - sub_w) // 2
        sub_y = main_y + 100
        
        draw.text((sub_x, sub_y), subtitle, font=self.TEXT_FONT, fill=self.SUBTLE_TEXT)
        
        # Decorative dots
        dot_y = sub_y + 120
        dot_spacing = 80
        dot_radius = 8
        
        for i in range(3):
            dot_x = (self.WIDTH // 2) - 80 + (i * dot_spacing)
            draw.ellipse(
                [dot_x - dot_radius, dot_y - dot_radius, 
                dot_x + dot_radius, dot_y + dot_radius],
                fill=self.ACCENT_COLOR
            )
        
        img.save(transition_paths["base"])
        logger.info("✅ Transition base image created")
        
        # --------------------------------------------------
        # 2. Countdown: "2"
        # --------------------------------------------------
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Background card (slightly dimmer)
        dimmer_color = tuple(int(c * 0.8) for c in self.CARD_COLOR)
        draw.rounded_rectangle(
            [content_x, content_y, content_x + content_w, content_y + content_h],
            radius=32,
            fill=dimmer_color
        )
        
        # Large "2" number
        countdown_font = ImageFont.truetype(str(self.JETBRAINS_MONO_FONT_DIR / "JetBrainsMono-Regular.ttf"), 320)
        number_text = "2"
        num_bbox = draw.textbbox((0, 0), number_text, font=countdown_font)
        num_w = num_bbox[2] - num_bbox[0]
        num_h = num_bbox[3] - num_bbox[1]
        num_x = (self.WIDTH - num_w) // 2
        num_y = (self.HEIGHT - num_h) // 2 - 50
        
        draw.text((num_x, num_y), number_text, font=countdown_font, fill=self.ACCENT_COLOR)
        
        img.save(transition_paths["2"])
        logger.info("✅ Transition countdown '2' image created")
        
        # --------------------------------------------------
        # 3. Countdown: "1"
        # --------------------------------------------------
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Background card (even dimmer)
        dimmer_color = tuple(int(c * 0.7) for c in self.CARD_COLOR)
        draw.rounded_rectangle(
            [content_x, content_y, content_x + content_w, content_y + content_h],
            radius=32,
            fill=dimmer_color
        )
        
        # Large "1" number
        number_text = "1"
        num_bbox = draw.textbbox((0, 0), number_text, font=countdown_font)
        num_w = num_bbox[2] - num_bbox[0]
        num_h = num_bbox[3] - num_bbox[1]
        num_x = (self.WIDTH - num_w) // 2
        num_y = (self.HEIGHT - num_h) // 2 - 50
        
        draw.text((num_x, num_y), number_text, font=countdown_font, fill=self.SUCCESS_COLOR)
        
        img.save(transition_paths["1"])
        logger.info("✅ Transition countdown '1' image created")
        
        # --------------------------------------------------
        # 4. Ready: "Ready for the answer?"
        # --------------------------------------------------
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Background card (back to normal)
        draw.rounded_rectangle(
            [content_x, content_y, content_x + content_w, content_y + content_h],
            radius=32,
            fill=self.CARD_COLOR
        )
        draw.rounded_rectangle(
            [content_x, content_y, content_x + content_w, content_y + content_h],
            radius=32,
            outline=self.ACCENT_COLOR,
            width=2
        )
        
        # Ready text
        ready_text = "Ready for the answer?"
        ready_bbox = draw.textbbox((0, 0), ready_text, font=self.TITLE_FONT)
        ready_w = ready_bbox[2] - ready_bbox[0]
        ready_x = (self.WIDTH - ready_w) // 2
        ready_y = content_y + 200
        
        draw.text((ready_x, ready_y), ready_text, font=self.TITLE_FONT, fill=self.SUCCESS_COLOR)
        
        # Subtitle
        emoji_text = "Let's go!"
        emoji_bbox = draw.textbbox((0, 0), emoji_text, font=self.TEXT_FONT)
        emoji_w = emoji_bbox[2] - emoji_bbox[0]
        emoji_x = (self.WIDTH - emoji_w) // 2
        emoji_y = ready_y + 120
        
        draw.text((emoji_x, emoji_y), emoji_text, font=self.TEXT_FONT, fill=self.ACCENT_COLOR)
        
        img.save(transition_paths["ready"])
        logger.info("✅ Transition ready image created")
        
        logger.info("✅ Complete transition sequence generated (4 images, 2 seconds total)")
        return transition_paths

    def render_image(
        self,
        question: Question,
        out_path: Path,
        layout_profile,
        subject: str,
        mode: RenderMode,
        ):
        canvas = self._create_base_canvas(subject)

        # ---------- CALCULATE TOTAL CONTENT HEIGHT ----------
        # You need to measure all elements before drawing
        # For each drawing method, calculate its height:
        header_height = 78  # bbox height + gap
        title_height = 78   # bbox height + gap
        
        # Scenario block height (drawn inline for QUESTION and SINGLE modes)
        scenario_height = 0
        if layout_profile.has_scenario and question.scenario and mode in (RenderMode.QUESTION, RenderMode.SINGLE):
            scenario_lines = wrap_text_with_prefix(
                self.draw,
                question.scenario.replace("\\n", " "),
                self.TEXT_FONT,
                self.max_width,
                self.draw.textlength("Setup: ", font=self.TEXT_FONT),
            )
            scenario_height = len(scenario_lines) * 50 + 20  # line_height + gap

        # Code block height (comes after scenario for scenario-based questions)
        code_height = 0
        if layout_profile.has_code and question.code:
            code_lines = normalize_code(question.code)
            wrapped_lines = []
            for line in code_lines:
                wrapped_lines.extend(wrap_code_line(self.draw, line, self.CODE_FONT, self.WIDTH - 120 - 40))
            code_height = len(wrapped_lines) * 48 + 40 + 40  # line_height + padding + gap

        # Question height
        question_lines = wrap_text_with_prefix(
            self.draw,
            question.question,
            self.TEXT_FONT,
            self.max_width,
            self.draw.textlength("Q: ", font=self.TEXT_FONT),
        )
        question_height = len(question_lines) * 50 + 20  # line_height + gap
        
        # Options height
        options_height = 0
        if layout_profile.has_options:
            for opt in question.options:
                opt = opt.replace("\\n", "\n")
                raw_lines = opt.split("\n")
                wrapped = []
                for line in raw_lines:
                    wrapped.extend(wrap_text(self.draw, line, self.TEXT_FONT, self.WIDTH - 120 - 60))
                block_height = len(wrapped) * 50 + 36  # line_height + padding
                options_height += block_height + 14  # option_gap
        
        # Explanation height
        explanation_height = 0
        if layout_profile.has_explanation and mode in (RenderMode.ANSWER, RenderMode.SINGLE):
            explanation_lines = wrap_text(self.draw, question.explanation, self.TEXT_FONT, self.WIDTH - 120)
            explanation_height = 18 + 55 + len(explanation_lines) * 50  # divider + label + lines
        
        total_content_height = (
            header_height + title_height + code_height + scenario_height + question_height + 
            options_height + explanation_height + 20
        )
        
        # Available space in card (from _create_base_canvas: card_y=80, card_h=HEIGHT-120)
        card_y = 80
        card_h = self.HEIGHT - 120
        available_height = card_h - 80  # Account for top and bottom padding
        
        # Calculate starting y to center content
        if available_height > total_content_height:
            start_y = card_y + (available_height - total_content_height) // 2
        else:
            start_y = card_y + 40  # Fallback to top if content is too large
        
        self.y_cursor = start_y


        # ---------- HEADER ----------
        subject_header = f"{subject.replace('_', ' ').title()}"
        if mode == RenderMode.QUESTION:
            header = f"Daily dose of {subject_header}"
        elif mode == RenderMode.ANSWER:
            header = f"{subject_header} Answer"
        else:
            header = subject_header

        self._draw_header(canvas, header)
        self._draw_title(question.title)

        # ---------- BODY ----------
        # ----------- SCENARIO TEXT ---------- 
        # Scenario included inline for docker_k8s/system_design in QUESTION and SINGLE modes
        # (has_code is false for these, so scenario replaces code position)

        if layout_profile.has_scenario \
                and question.scenario \
                and mode in (RenderMode.QUESTION, RenderMode.SINGLE):
            self._draw_scenario_styled(canvas, question.scenario, prefix="Setup:")

        # ---------- CODE BLOCK ----------
        # Code comes after scenario for scenario-based questions (docker_k8s, system_design)
        if layout_profile.has_code and question.code:
            self._draw_code(canvas, question.code, layout_profile.code_style, subject=subject)

        # ----------- QUESTION TEXT ----------
        self._draw_scenario_styled(canvas, question.question)

        # ---------- OPTIONS ----------
        if layout_profile.has_options:
            self._draw_options_v2(
                canvas,
                question.options,
                mode,
                correct=question.correct
            )
        
        # ---------- EXPLANATION ----------
        if layout_profile.has_explanation and mode in (RenderMode.ANSWER, RenderMode.SINGLE):
            self._draw_explanation(canvas, question.explanation)

        # ---------- FOOTER ----------
        self._draw_footer(canvas, subject.replace('_', ' ').title())

        # ---------- WATERMARK ----------
        canvas = self._draw_watermark(canvas)

        # ---------- LOGO ----------
        canvas = self._draw_logo(canvas)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path)
        logger.info("Image saved to %s", out_path)
