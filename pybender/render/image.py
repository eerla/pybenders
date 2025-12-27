import json
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pybender.generator.schema import Question
from pybender.render.layout_profiles import LAYOUT_PROFILES
from pybender.generator.question_gen import QuestionGenerator
from pybender.render.layout_resolver import resolve_layout_profile
from pybender.render.render_mode import RenderMode

class ImageRenderer:
    """
    Wrapper class for image rendering functions.
    """
    def __init__(self):
        self.MODEL = "gpt-4o-mini"
        # Canvas
        self.WIDTH, self.HEIGHT = 1080, 1920
        # if for_carousel:
        # WIDTH, HEIGHT = 1080, 1080
        self.PADDING_X = 60
        self.PADDING_Y = 60
        # Colors (match CTA theme)
        self.BG_COLOR = (9, 12, 24)
        self.CARD_COLOR = (11, 18, 32)
        self.CODE_BG = (15, 23, 42)
        self.TEXT_COLOR = (226, 232, 240)
        self.SUBTLE_TEXT = (148, 163, 184)
        self.ACCENT_COLOR = (76, 201, 240)
        self.CORRECT_BG = (20, 45, 70)
        self.SUCCESS_COLOR = (72, 187, 120)
        self.TEXT_PRIMARY = (255, 255, 255)
        self.TEXT_SECONDARY = (160, 174, 192)
        # Fonts
        self.FONT_DIR = Path("pybender/assets/fonts")

        self.TITLE_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-SemiBold.ttf"), 48)
        self.TEXT_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-Regular.ttf"), 48)
        self.CODE_FONT = ImageFont.truetype(str(self.FONT_DIR / "JetBrainsMono-Regular.ttf"), 48)
        self.HEADER_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-Regular.ttf"), 48)

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


    # ---------- SCENARIO ----------
    def _draw_scenario(self, canvas, scenario_text: str):
        scenario_text = scenario_text.replace("\\n", " ")
        lines = self.wrap_text(self.draw, scenario_text, self.TEXT_FONT, self.max_width)
        
        for i, line in enumerate(lines):
            prefix = "Q. " if i == 0 else ""
            self.draw.text(
                (self.content_x, self.y_cursor),
                prefix + line,
                font=self.TEXT_FONT,
                fill=self.TEXT_COLOR
            )
            self.y_cursor += 50
        
        self.y_cursor += 20

    # ---------- CODE ----------
    def _draw_code(self, canvas, code: str, style: str):
        draw = self.draw
        font = self.CODE_FONT
        max_width = self.WIDTH - (self.PADDING_X * 2) - 40
        line_height = 48
        padding = 20

        # Normalize
        code = code.replace("\\n", "\n").replace("\t", "    ")
        raw_lines = code.split("\n")

        wrapped_lines = []
        for line in raw_lines:
            wrapped_lines.extend(
                self.wrap_code_line(draw, line, font, max_width)
            )

        block_height = len(wrapped_lines) * line_height + padding * 2

        # Background
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

        # Accent bar
        self.draw.rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.PADDING_X + 6,
                self.y_cursor + block_height,
            ],
            fill=self.ACCENT_COLOR,
        )

        y = self.y_cursor + padding
        for line in wrapped_lines:
            self.draw.text(
                (self.PADDING_X + 40, y),
                line,
                font=font,
                fill=self.TEXT_COLOR,
            )
            y += line_height

        self.y_cursor += block_height + 40


    # ---------- OPTIONS ----------
    def _draw_options(self, canvas, options: list[str]):
        draw = ImageDraw.Draw(canvas)
        # font = ImageFont.truetype("assets/fonts/Inter-Regular.ttf", 40)

        max_width = self.WIDTH - (self.PADDING_X * 2)
        line_height = 50
        box_padding_y = 18
        option_gap = 14

        for idx, opt in enumerate(options):
            label = chr(65 + idx)

            # Normalize escaped newlines
            opt = opt.replace("\\n", "\n")

            # Split explicit newlines, then wrap each part
            raw_lines = opt.split("\n")
            wrapped_lines = []

            for line in raw_lines:
                wrapped_lines.extend(
                    self.wrap_text(draw, line, self.TEXT_FONT, max_width - 60)
                )

            # Compute block height
            block_height = (
                len(wrapped_lines) * line_height
                + box_padding_y * 2
            )

            # Draw background card
            self.draw.rounded_rectangle(
                [
                    self.PADDING_X - 10,
                    self.y_cursor,
                    self.WIDTH - self.PADDING_X + 10,
                    self.y_cursor + block_height,
                ],
                radius=18,
                fill=self.CARD_COLOR,
            )

            # Draw accent bar on the left
            self.draw.rectangle(
                [
                    self.PADDING_X - 10,
                    self.y_cursor,
                    self.PADDING_X - 4,
                    self.y_cursor + block_height,
                ],
                fill=self.ACCENT_COLOR,
            )

            # Draw text lines
            text_y = self.y_cursor + box_padding_y
            for i, line in enumerate(wrapped_lines):
                prefix = f"{label}. " if i == 0 else "    "
                self.draw.text(
                    (self.PADDING_X, text_y),
                    prefix + line,
                    font=self.TEXT_FONT,
                    fill=self.TEXT_COLOR,
                )
                text_y += line_height

            self.y_cursor += block_height + option_gap

        self.y_cursor += 20

    # ---------- OPTIONS WITH ANSWER HIGHLIGHT ----------
    def _draw_options_with_answer(self, canvas, options, correct):
        draw = self.draw
        font = self.TEXT_FONT
        max_width = self.WIDTH - (self.PADDING_X * 2)
        line_height = 50
        padding = 18
        option_gap = 14

        correct_idx = ord(correct.upper()) - 65

        for idx, opt in enumerate(options):
            opt = opt.replace("\\n", "\n")
            raw_lines = opt.split("\n")
            wrapped = []

            for line in raw_lines:
                wrapped.extend(
                    self.wrap_text(draw, line, font, max_width - 60)
                )

            block_height = len(wrapped) * line_height + padding * 2

            bg = self.CORRECT_BG if idx == correct_idx else self.CARD_COLOR
            accent = self.SUCCESS_COLOR if idx == correct_idx else self.ACCENT_COLOR

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

            self.draw.rectangle(
                [
                    self.PADDING_X - 10, # accent bar left
                    self.y_cursor, # accent bar left
                    self.PADDING_X - 4, # accent bar width
                    self.y_cursor + block_height, # accent bar height
                ],
                fill=accent,
            )

            y = self.y_cursor + padding
            for i, line in enumerate(wrapped):
                prefix = f"{chr(65+idx)}. " if i == 0 else "    "
                self.draw.text(
                    (self.PADDING_X, y),
                    prefix + line,
                    font=font,
                    fill=self.TEXT_COLOR,
                )
                y += line_height

            self.y_cursor += block_height + option_gap

        self.y_cursor += 20

    def _draw_options_with_answer_highlight_only(self, canvas, options, correct):
        # function to display only the correct answer highlighted
        draw = self.draw
        font = self.TEXT_FONT
        max_width = self.WIDTH - (self.PADDING_X * 2)
        line_height = 50
        padding = 18

        correct_idx = ord(correct.upper()) - 65
        opt = options[correct_idx]
        
        opt = opt.replace("\\n", "\n")
        raw_lines = opt.split("\n")
        wrapped = []

        for line in raw_lines:
            wrapped.extend(
                self.wrap_text(draw, line, font, max_width - 60)
            )

        block_height = len(wrapped) * line_height + padding * 2

        self.draw.rounded_rectangle(
            [
                self.PADDING_X - 10,
                self.y_cursor,
                self.WIDTH - self.PADDING_X + 10,
                self.y_cursor + block_height,
            ],
            radius=18,
            fill=self.CORRECT_BG,
        )

        self.draw.rectangle(
            [
                self.PADDING_X - 10,
                self.y_cursor,
                self.PADDING_X - 4,
                self.y_cursor + block_height,
            ],
            fill=self.SUCCESS_COLOR,
        )

        y = self.y_cursor + padding
        for i, line in enumerate(wrapped):
            prefix = f"{chr(65+correct_idx)}. " if i == 0 else "    "
            self.draw.text(
                (self.PADDING_X, y),
                prefix + line,
                font=font,
                fill=self.TEXT_COLOR,
            )
            y += line_height

        self.y_cursor += block_height + 20

    # ---------- EXPLANATION ----------
    def _draw_explanation(self, canvas, explanation: str):
        font = self.TEXT_FONT
        max_width = self.WIDTH - (self.PADDING_X * 2)

        explanation = explanation.replace("\\n", " ")
        lines = self.wrap_text(self.draw, explanation, font, max_width)

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
            font=self.HEADER_FONT,
            fill=self.SUBTLE_TEXT,
        )


    @staticmethod
    def slugify(text: str) -> str:
        return text.lower().replace(" ", "_")
    
    @staticmethod
    def wrap_code_line(draw, line, font, max_width):
        stripped = line.lstrip(" ")
        indent = line[:len(line) - len(stripped)]

        if not stripped:
            return [line]

        words = stripped.split(" ")
        lines = []
        current = ""

        for word in words:
            test = (current + " " + word).strip()
            width = draw.textlength(indent + test, font=font)

            if width <= max_width:
                current = test
            else:
                if current:
                    lines.append(indent + current)
                current = word

        if current:
            lines.append(indent + current)

        return lines

    @staticmethod
    def wrap_text(draw, text, font, max_width):
        """
        Wrap text so that each line fits within max_width.
        Returns a list of lines.
        """
        if not text:
            return [""]
        words = text.split(" ")
        lines = []
        current = ""

        for word in words:
            test = current + (" " if current else "") + word
            if draw.textlength(test, font=font) <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    @staticmethod
    def normalize_code(code: str) -> list[str]:
        """
        Normalize code string into clean lines:
        - Converts escaped newlines (\\n) to real newlines
        - Converts tabs to 4 spaces
        - Strips trailing whitespace
        """
        if not code:
            return []

        # Convert literal "\n" into actual newlines
        code = code.replace("\\n", "\n")

        lines = []
        for line in code.split("\n"):
            # Convert tabs to spaces (visual stability)
            line = line.replace("\t", " " * 4)
            lines.append(line.rstrip())

        return lines

    @staticmethod
    def normalize_option_text(option: str) -> list[str]:
        """
        Normalize option text into wrapped lines.
        Supports explicit newlines + auto wrapping.
        """
        option = option.replace("\\n", "\n")
        return option.split("\n")


    def render_image(
        self,
        question: dict,
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
        
        # Code block height
        code_height = 0
        if layout_profile.has_code and question.code:
            code_lines = self.normalize_code(question.code)
            wrapped_lines = []
            for line in code_lines:
                wrapped_lines.extend(self.wrap_code_line(self.draw, line, self.CODE_FONT, self.WIDTH - 120 - 40))
            code_height = len(wrapped_lines) * 48 + 40 + 40  # line_height + padding + gap
        
        # Question height
        scenario_lines = self.wrap_text(self.draw, question.question, self.TEXT_FONT, self.WIDTH - 120)
        scenario_height = len(scenario_lines) * 50 + 20  # line_height + gap
        
        # Options height
        options_height = 0
        if layout_profile.has_options:
            for opt in question.options:
                opt = opt.replace("\\n", "\n")
                raw_lines = opt.split("\n")
                wrapped = []
                for line in raw_lines:
                    wrapped.extend(self.wrap_text(self.draw, line, self.TEXT_FONT, self.WIDTH - 120 - 60))
                block_height = len(wrapped) * 50 + 36  # line_height + padding
                options_height += block_height + 14  # option_gap
        
        # Explanation height
        explanation_height = 0
        if layout_profile.has_explanation and mode in (RenderMode.ANSWER, RenderMode.SINGLE):
            explanation_lines = self.wrap_text(self.draw, question.explanation, self.TEXT_FONT, self.WIDTH - 120)
            explanation_height = 18 + 55 + len(explanation_lines) * 50  # divider + label + lines
        
        total_content_height = (
            header_height + title_height + code_height + 
            scenario_height + options_height + explanation_height + 20
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
        if mode == RenderMode.QUESTION:
            header = f"Daily dose of {subject}"
        elif mode == RenderMode.ANSWER:
            header = f"{subject} Answer"
        else:
            header = subject.upper()

        self._draw_header(canvas, header)
        self._draw_title(question.title)

        # ---------- BODY ----------
        # ---------- CODE BLOCK ----------
        if layout_profile.has_code and question.code:
            self._draw_code(canvas, question.code, layout_profile.code_style)

        # ----------- QUESTION TEXT ----------
        self._draw_scenario(canvas, question.question)
        # ---------- OPTIONS ----------
        if layout_profile.has_options:
            if mode == RenderMode.QUESTION:
                self._draw_options(canvas, question.options)
            elif mode == RenderMode.SINGLE:
                self._draw_options_with_answer(
                    canvas,
                    question.options,
                    question.correct,
                )
            elif mode == RenderMode.ANSWER:
                self._draw_options_with_answer_highlight_only(
                    canvas,
                    question.options,
                    question.correct,
                )
        # ---------- EXPLANATION ----------
        if layout_profile.has_explanation and mode in (RenderMode.ANSWER, RenderMode.SINGLE):
            self._draw_explanation(canvas, question.explanation)

        # ---------- FOOTER ----------
        self._draw_footer(canvas, subject)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path)
        print(f"image saved to: {out_path}")


    def render_day1_cta_image(self, subject: str) -> None:
        """
        Render a reusable Call-To-Action image (dark theme).
        Saved once and reused for all reels.
        """
        out_path = Path(f"output/{subject}/images/cta/day1.png")
        if out_path.exists():
            print(f"!!! {out_path} exists! remove that to recreate with new changes !!!")
            return

        out_path.parent.mkdir(parents=True, exist_ok=True)

        # --------------------------------------------------
        # Canvas
        # --------------------------------------------------
        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Card Geometry
        # --------------------------------------------------
        card_w, card_h = 920, 720
        card_x = (self.WIDTH - card_w) // 2
        card_y = (self.HEIGHT - card_h) // 2
        radius = 32

        # Rounded card
        draw.rounded_rectangle(
            [
                card_x,
                card_y,
                card_x + card_w,
                card_y + card_h,
            ],
            radius=radius,
            fill=self.CARD_COLOR,
        )

        # --------------------------------------------------
        # Fonts (adjust paths as needed)
        # --------------------------------------------------
        FONT_DIR = Path("pybender/assets/fonts")

        title_font = ImageFont.truetype(str(FONT_DIR / "Inter-Bold.ttf"), 72)
        body_font = ImageFont.truetype(str(FONT_DIR / "Inter-SemiBold.ttf"), 50)
        follow_font = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 44)

        # --------------------------------------------------
        # Text Content
        # --------------------------------------------------
        title_text = "What's Your Answer?"
        body_text = "Drop A, B, C, or D below!\n\nAnswer drops tomorrow"
        follow_text = f"Follow for daily {subject.capitalize()} challenges"

        # --------------------------------------------------
        # Text Positions
        # --------------------------------------------------
        center_x = self.WIDTH // 2

        def draw_centered_text(text, font, y, color):
            w, h = draw.textbbox((0, 0), text, font=font)[2:]
            draw.text(
                (center_x - w // 2, y),
                text,
                font=font,
                fill=color,
                align="center",
            )

        draw_centered_text(
            title_text,
            title_font,
            card_y + 90,
            self.ACCENT_COLOR,
        )

        draw_centered_text(
            body_text,
            body_font,
            card_y + 260,
            self.TEXT_PRIMARY,
        )

        draw_centered_text(
            follow_text,
            follow_font,
            card_y + 520,
            self.TEXT_SECONDARY,
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        img.save(out_path, format="PNG")
        print(f"CTA image rendered at: {out_path}")


    def render_day2_cta_image(self, subject: str) -> None:
        """
        Render a reusable Call-To-Action image (dark theme).
        Saved once and reused for all reels.
        """
        out_path = Path(f"output/{subject}/images/cta/day2.png")
        if out_path.exists():
            print(f"!!! {out_path} exists! remove that to recreate with new changes !!!")
            return

        TITLE_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-SemiBold.ttf"), 84)
        TEXT_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-Regular.ttf"), 48)
        SUBTLE_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-Regular.ttf"), 42)

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
            fill=self.ACCENT_COLOR
        )
        y += 120

        # --------------------------------------------------
        # Body
        # --------------------------------------------------
        body_lines = [
            "Hope that one made you think.",
            "",
            "Follow for daily",
            f"{subject.capitalize()} tricky questions."
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
        print(f"Day 2 CTA image saved → {out_path}")


    def render_welcome_image(self, subject: str) -> None:
        """
        Render a welcome image: 'Welcome to Daily Dose of Python'
        """
        out_path = Path(f"output/{subject}/images/welcome/welcome.png")
        if out_path.exists():
            print(f"!!! {out_path} exists! remove that to recreate with new changes !!!")
            return

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Main Card
        # --------------------------------------------------
        card_x, card_y = 60, 220
        card_w, card_h = self.WIDTH - 120, self.HEIGHT - 440

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
        brand = f"Daily Dose of {subject.capitalize()}"
        bw = draw.textbbox((0, 0), brand, font=self.TITLE_FONT)[2]
        draw.text(
            (content_x + (max_width - bw) // 2, y),
            brand,
            font=self.TITLE_FONT,
            fill=self.ACCENT_COLOR
        )
        y += 90

        # --------------------------------------------------
        # Divider
        # --------------------------------------------------
        draw.line(
            [
                content_x + 120,
                y,
                content_x + max_width - 120,
                y
            ],
            fill=self.ACCENT_COLOR,
            width=2
        )
        y += 150

        # --------------------------------------------------
        # Subtitle
        # --------------------------------------------------
        subtitle = f"Bite-sized {subject.capitalize()} challenges.\nThink. Comment. Learn."
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
        overlay_path = Path("output/images/welcome/media/pyimg.png")
        overlay_h = 0
        if overlay_path.exists():
            overlay = Image.open(overlay_path).convert("RGBA")
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


    def main(self, questions_per_run: int, subject: str = "python") -> Path:

        # --------------------------------------------------
        # Run context
        # --------------------------------------------------
        RUN_DATE = datetime.now().strftime("%Y-%m-%d")
        RUN_TIMESTAMP = datetime.now().strftime("%H%M%S")
        RUN_ID = f"{RUN_DATE}_{RUN_TIMESTAMP}"
        topic = None
        print(f"Starting run: {RUN_ID}")
        
        # --------------------------------------------------
        # Generate questions
        # --------------------------------------------------
        qg = QuestionGenerator()
        questions, topic, content_type = qg.generate_questions(questions_per_run, subject=subject)  # get from LLM
        # with open("output/questions.json", "r") as f:
        #     questions_data = json.load(f)
        #     topic, content_type = "python", "code_output"
        #     # topic, content_type = "javascript", "code_output"
        #     questions = [Question(**q) for q in questions_data]
        

        # Assign stable question IDs
        for idx, q in enumerate(questions, start=1):
            q.question_id = f"{RUN_ID}_q{idx:02d}"

        # --------------------------------------------------
        # Output directories (type-based)
        # --------------------------------------------------
        base_img_dir = Path(f"output/{subject}/images")
        question_dir = base_img_dir / "questions"
        answer_dir = base_img_dir / "answers"
        single_dir = base_img_dir / "singles"
        run_dir = Path(f"output/{subject}/runs") / RUN_ID
        for d in [question_dir, answer_dir, single_dir, run_dir]:
            d.mkdir(parents=True, exist_ok=True)

        metadata = {
            "run_id": RUN_ID,
            "run_date": RUN_DATE,
            "run_timestamp": RUN_TIMESTAMP,
            "subject": subject,
            "content_type": content_type,
            "generator": {
                "model": self.MODEL,
                "topic": topic if topic else "DEFAULT" # or return topic from generate_questions()
            },
            "questions": []
        }


        # --------------------------------------------------
        # Render assets
        # --------------------------------------------------
        print("Rendering images...")

        for q in questions:
            q_slug = self.slugify(q.title)

            question_img_out_path = question_dir / f"{q.question_id}_question.png"
            answer_img_out_path = answer_dir / f"{q.question_id}_answer.png"
            single_img_out_path = single_dir / f"{q.question_id}_single.png"

            self.render_image(q, question_img_out_path, resolve_layout_profile(content_type), subject, RenderMode.QUESTION)
            self.render_image(q, answer_img_out_path, resolve_layout_profile(content_type), subject, RenderMode.ANSWER)
            self.render_image(q, single_img_out_path, resolve_layout_profile(content_type), subject, RenderMode.SINGLE)

            metadata["questions"].append({
                "question_id": q.question_id,
                "title": q.title,
                "slug": q_slug,
                "content": q.model_dump(),
                "assets": {
                    "question_image": str(question_img_out_path),
                    "answer_image": str(answer_img_out_path),
                    "single_post_image": str(single_img_out_path)
                }
            })

        print("All images rendered successfully")

        # --------------------------------------------------
        # Write metadata.json (single source of truth)
        # --------------------------------------------------
        metadata_path = run_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"Metadata written to {metadata_path}")
        # TODO: create separate welcome pages per subject
        self.render_day1_cta_image(subject)
        self.render_day2_cta_image(subject)
        self.render_welcome_image(subject)
        print("Image rendering process completed successfully")
        return metadata_path

# if __name__ == "__main__":
#     renderer = ImageRenderer()
#     renderer.main(1, subject="python")