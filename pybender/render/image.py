from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from pybender.generator.schema import Question
from pybender.generator.question_gen import generate_questions
import json
from datetime import datetime

class ImageRenderer:
    """
    Wrapper class for image rendering functions.
    """
    def __init__(self):
        # Canvas
        self.WIDTH, self.HEIGHT = 1080, 1920
        # if for_carousel:
        # WIDTH, HEIGHT = 1080, 1080
        self.PADDING_X = 60
        self.PADDING_Y = 50
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
        self.CODE_FONT = ImageFont.truetype(str(self.FONT_DIR / "JetBrainsMono-Regular.ttf"), 40)
        self.HEADER_FONT = ImageFont.truetype(str(self.FONT_DIR / "Inter-Regular.ttf"), 48)

        self.RUN_DATE = datetime.now().strftime("%Y%m%d")
        self.RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def wrap_code_line(draw, line, font, max_width):
        """
        Wrap a single line of code while preserving leading indentation.
        """
        # Extract leading spaces (indentation)
        stripped = line.lstrip(" ")
        indent = line[:len(line) - len(stripped)]

        if not stripped:
            return [line]

        words = stripped.split(" ")
        lines = []
        current = ""

        for word in words:
            test = current + (" " if current else "") + word
            width = draw.textlength(indent + test, font=font)

            if width <= max_width:
                current = test
            else:
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
        words = text.split(" ")
        lines = []
        current = ""

        for word in words:
            test_line = current + (" " if current else "") + word
            width = draw.textlength(test_line, font=font)

            if width <= max_width:
                current = test_line
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines


    def render_question_image(self, q: Question, out_path: Path) -> None:

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Main Card
        # --------------------------------------------------
        card_x, card_y = 40, 80
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120
        radius = 28

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            fill=self.CARD_COLOR
        )

        y = card_y + 40
        content_x = card_x + 40
        max_width = card_w - 80

        # --------------------------------------------------
        # Calculate total content height first
        # --------------------------------------------------
        # Header
        header_text = "Daily Dose of Python"
        header_height = 60

        # Title
        title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
        title_height = 70

        # Code block
        code_lines = q.code.split("\n")
        line_height = 44
        block_padding = 20
        all_wrapped_lines = []
        for raw_line in code_lines:
            wrapped = self.wrap_code_line(
                draw,
                raw_line,
                self.CODE_FONT,
                max_width - 40
            )
            all_wrapped_lines.extend(wrapped)
        code_block_height = len(all_wrapped_lines) * line_height + block_padding * 2
        code_section_height = code_block_height + 40

        # Question text
        question_lines = self.wrap_text(draw, q.question, self.TEXT_FONT, max_width)
        question_height = len(question_lines) * 48 + 20

        # Options
        options_height = 4 * 46

        # Total content height
        total_content_height = header_height + title_height + code_section_height + question_height + options_height
        card_content_height = card_h - 80  # Account for top and bottom padding

        # Calculate starting y position to center vertically
        y = card_y + (card_content_height - total_content_height) // 2

        # --------------------------------------------------
        # Header
        # --------------------------------------------------
        hw = draw.textbbox((0, 0), header_text, font=self.HEADER_FONT)[2]
        draw.text(
            (content_x + (max_width - hw) // 2, y),
            header_text,
            font=self.HEADER_FONT,
            fill=self.SUBTLE_TEXT
        )
        y += header_height

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title_x = content_x + (max_width - title_bbox[2]) // 2
        draw.text((title_x, y), q.title, font=self.TITLE_FONT, fill=self.ACCENT_COLOR)
        y += title_height

        # --------------------------------------------------
        # Code Block
        # --------------------------------------------------
        draw.rounded_rectangle(
            [
                content_x,
                y,
                content_x + max_width,
                y + code_block_height
            ],
            radius=18,
            fill=self.CODE_BG
        )

        draw.rectangle(
            [content_x, y, content_x + 6, y + code_block_height],
            fill=self.ACCENT_COLOR
        )

        cy = y + block_padding
        for line in all_wrapped_lines:
            draw.text(
                (content_x + 20, cy),
                line,
                font=self.CODE_FONT,
                fill=self.TEXT_COLOR
            )
            cy += line_height

        y += code_section_height

        # --------------------------------------------------
        # Question Text
        # --------------------------------------------------
        for line in question_lines:
            draw.text((content_x, y), line, font=self.TEXT_FONT, fill=self.TEXT_COLOR)
            y += 48
        y += 20

        # --------------------------------------------------
        # Options
        # --------------------------------------------------
        for label, option in zip(["A", "B", "C", "D"], q.options):
            option_text = f"{label}. {option}"
            draw.text(
                (content_x, y),
                option_text,
                font=self.TEXT_FONT,
                fill=self.TEXT_COLOR
            )
            y += 56

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)


    def render_answer_image(self, q: Question, out_path: Path) -> None:
        """
        Render answer-reveal image highlighting the correct option.
        """

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Main Card
        # --------------------------------------------------
        card_x, card_y = 40, 80
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120
        radius = 28

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            fill=self.CARD_COLOR
        )

        content_x = card_x + 40
        max_width = card_w - 80

        # --------------------------------------------------
        # Calculate total content height first
        # --------------------------------------------------
        # Answer label
        answer_label_height = 70
        
        # Title
        title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
        title_height = 80

        # Code block
        code_lines = q.code.split("\n")
        line_height = 44
        block_padding = 20
        all_wrapped_lines = []
        for raw_line in code_lines:
            wrapped = self.wrap_code_line(
                draw,
                raw_line,
                self.CODE_FONT,
                max_width - 40
            )
            all_wrapped_lines.extend(wrapped)
        code_block_height = len(all_wrapped_lines) * line_height + block_padding * 2
        code_section_height = code_block_height + 40

        # Answer option
        option_h = 60
        answer_section_height = option_h + 32

        # Explanation
        explanation_height = 0
        if q.explanation:
            explanation_lines = self.wrap_text(draw, q.explanation, self.TEXT_FONT, max_width)
            explanation_height = 28 + 60 + (len(explanation_lines) * 50)  # divider + label + content

        # Total content height
        total_content_height = answer_label_height + title_height + code_section_height + answer_section_height + explanation_height
        card_content_height = card_h - 80  # Account for top and bottom padding

        # Calculate starting y position to center vertically
        y = card_y + (card_content_height - total_content_height) // 2

        # --------------------------------------------------
        # Answer Label
        # --------------------------------------------------
        answer_text = "Answer"
        aw = draw.textbbox((0, 0), answer_text, font=self.HEADER_FONT)[2]
        draw.text(
            (content_x + (max_width - aw) // 2, y),
            answer_text,
            font=self.HEADER_FONT,
            fill=self.SUBTLE_TEXT
        )
        y += answer_label_height

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title_x = content_x + (max_width - title_bbox[2]) // 2
        draw.text((title_x, y), q.title, font=self.TITLE_FONT, fill=self.ACCENT_COLOR)
        y += title_height

        # --------------------------------------------------
        # Code Block
        # --------------------------------------------------
        draw.rounded_rectangle(
            [
                content_x,
                y,
                content_x + max_width,
                y + code_block_height
            ],
            radius=18,
            fill=self.CODE_BG
        )

        draw.rectangle(
            [content_x, y, content_x + 6, y + code_block_height],
            fill=self.ACCENT_COLOR
        )

        cy = y + block_padding
        for line in all_wrapped_lines:
            draw.text(
                (content_x + 20, cy),
                line,
                font=self.CODE_FONT,
                fill=self.TEXT_COLOR
            )
            cy += line_height

        y += code_section_height

        # --------------------------------------------------
        # Answer Option (highlight correct)
        # --------------------------------------------------
        correct_label = q.correct.upper()
        option = q.options[ord(correct_label) - ord("A")]
        
        # Highlight background
        draw.rounded_rectangle(
            [content_x, y - 6, content_x + max_width, y + option_h],
            radius=14,
            fill=self.CORRECT_BG
        )
        draw.rectangle(
            [content_x, y - 6, content_x + 6, y + option_h],
            fill=self.SUCCESS_COLOR
        )

        draw.text(
            (content_x + 18, y),
            f"{correct_label}. {option}",
            font=self.TEXT_FONT,
            fill=self.SUCCESS_COLOR
        )

        y += answer_section_height

        # --------------------------------------------------
        # Explanation (optional but powerful)
        # --------------------------------------------------
        if q.explanation:
            draw.line(
                [(content_x, y), (content_x + max_width, y)],
                fill=self.ACCENT_COLOR,
                width=2
            )
            y += 18

            explanation_label = "Explanation: "
            explanation_content = q.explanation
            
            # Draw "Explanation:" in accent color
            draw.text(
                (content_x, y),
                explanation_label,
                font=self.TEXT_FONT,
                fill=self.ACCENT_COLOR
            )
            y += 60
            
            # Draw the explanation text
            for line in self.wrap_text(draw, explanation_content, self.TEXT_FONT, max_width):
                draw.text(
                    (content_x, y),
                    line,
                    font=self.TEXT_FONT,
                    fill=self.SUBTLE_TEXT
                )
                y += 50

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)


    def render_single_post_image(self, q: Question, out_path: Path) -> None:
        """
        Render a single-post image with question + answer together.
        Output: pybenders/output/images/singles/<slug>.png
        """
        # out_path = Path("output/images/singles") / f"{q.title.lower().replace(' ', '_')}.png"
        # out_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Main Card
        # --------------------------------------------------
        card_x, card_y = 40, 70
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 110

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=28,
            fill=self.CARD_COLOR
        )

        content_x = card_x + 40
        max_width = card_w - 80
        y = card_y + 30

        # --------------------------------------------------
        # Header (Brand) - moved inside card
        # --------------------------------------------------
        header = "Daily Dose of Python"
        hw = draw.textbbox((0, 0), header, font=self.HEADER_FONT)[2]
        draw.text(
            (content_x + (max_width - hw) // 2, y),
            header,
            font=self.HEADER_FONT,
            fill=self.SUBTLE_TEXT
        )
        y += 50

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
        draw.text(
            (content_x + (max_width - title_bbox[2]) // 2, y),
            q.title,
            font=self.TITLE_FONT,
            fill=self.ACCENT_COLOR
        )
        y += 80

        # --------------------------------------------------
        # Code Block
        # --------------------------------------------------
        code_lines = q.code.split("\n")
        line_height = 42
        block_padding = 20

        wrapped_lines = []
        for raw in code_lines:
            wrapped_lines.extend(
                self.wrap_code_line(draw, raw, self.CODE_FONT, max_width - 40)
            )

        block_height = len(wrapped_lines) * line_height + block_padding * 2

        draw.rounded_rectangle(
            [content_x, y, content_x + max_width, y + block_height],
            radius=18,
            fill=self.CODE_BG
        )

        draw.rectangle(
            [content_x, y, content_x + 6, y + block_height],
            fill=self.ACCENT_COLOR
        )

        cy = y + block_padding
        for line in wrapped_lines:
            draw.text(
                (content_x + 20, cy),
                line,
                font=self.CODE_FONT,
                fill=self.TEXT_COLOR
            )
            cy += line_height

        y = cy + 30

        # --------------------------------------------------
        # Question Text
        # --------------------------------------------------
        question_lines = self.wrap_text(draw, q.question, self.TEXT_FONT, max_width)
        for line in question_lines:
            draw.text((content_x, y), line, font=self.TEXT_FONT, fill=self.TEXT_COLOR)
            y += 48
        y += 20

        # --------------------------------------------------
        # All Options
        # --------------------------------------------------
        for label, option in zip(["A", "B", "C", "D"], q.options):
            option_text = f"{label}. {option}"
            draw.text(
                (content_x, y),
                option_text,
                font=self.TEXT_FONT,
                fill=self.TEXT_COLOR
            )
            y += 56

        y += 20
        # --------------------------------------------------
        # Correct Answer Highlight
        # --------------------------------------------------
        correct_label = q.correct.upper()
        correct_option = q.options[ord(correct_label) - ord("A")]

        answer_height = 80
        draw.rounded_rectangle(
            [content_x, y, content_x + max_width, y + answer_height],
            radius=18,
            fill=self.CORRECT_BG
        )
        draw.rectangle(
            [content_x, y, content_x + 6, y + answer_height],
            fill=self.SUCCESS_COLOR
        )

        draw.text(
            (content_x + 20, y + 18),
            f"Correct Answer: {correct_option}",
            font=self.TEXT_FONT,
            fill=self.SUCCESS_COLOR
        )

        y += answer_height + 24

        # --------------------------------------------------
        # Explanation (optional but powerful) 
        # --------------------------------------------------
        if q.explanation:
            y += 10
            draw.line(
                [(content_x, y), (content_x + max_width, y)],
                fill=self.ACCENT_COLOR,
                width=2
            )
            y += 18

            explanation_label = "Explanation: "
            explanation_content = q.explanation
            
            # Draw "Explanation:" in accent color
            label_width = draw.textbbox((0, 0), explanation_label, font=self.TEXT_FONT)[2]
            draw.text(
                (content_x, y),
                explanation_label,
                font=self.TEXT_FONT,
                fill=self.ACCENT_COLOR
            )
            y += 60
            
            # Draw the explanation text starting from the next line
            for line in self.wrap_text(draw, explanation_content, self.TEXT_FONT, max_width):
                draw.text(
                (content_x, y),
                line,
                font=self.TEXT_FONT,
                fill=self.SUBTLE_TEXT
                )
                y += 50

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        img.save(out_path)
        print(f"Single post image saved → {out_path}")

    
    def render_day1_cta_image(self) -> None:
        """
        Render a reusable Call-To-Action image (dark theme).
        Saved once and reused for all reels.
        """
        out_path = Path("output/images/cta/day1_carousel.png")
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
        follow_text = "Follow for daily Python challenges"

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


    def render_day2_cta_image(self) -> None:
        """
        Render a reusable Call-To-Action image (dark theme).
        Saved once and reused for all reels.
        """
        out_path = Path("output/images/cta/day2_carousel.png")
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
            "Python tricky questions."
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


    def render_welcome_image(self) -> None:
        """
        Render a welcome image: 'Welcome to Daily Dose of Python'
        """
        out_path = Path("output/images/welcome/welcome_carousel.png")
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
        brand = "Daily Dose of Python"
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
        subtitle = "Bite-sized Python challenges.\nThink. Comment. Learn."
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
        overlay_path = Path("output/images/media/pyimg.png")
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

    # not used at the moment
    def render_explanation_image(self, q: Question, out_path: Path) -> None:
        """
        Render a dark-themed explanation image for reels/posts.
        """

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------
        header = "Explanation"
        hw = draw.textbbox((0, 0), header, font=self.HEADER_FONT)[2]
        draw.text(
            ((self.WIDTH - hw) // 2, 20),
            header,
            font=self.HEADER_FONT,
            fill=self.SUBTLE_TEXT
        )

        # --------------------------------------------------
        # Main Card
        # --------------------------------------------------
        card_x, card_y = 40, 70
        card_w, card_h = self.WIDTH - 80, self.HEIGHT - 110

        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=28,
            fill=self.CARD_COLOR
        )

        content_x = card_x + 40
        max_width = card_w - 80
        y = card_y + 30

        # --------------------------------------------------
        # Title (Question Title)
        # --------------------------------------------------
        title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
        draw.text(
            (content_x + (max_width - title_bbox[2]) // 2, y),
            q.title,
            font=self.TITLE_FONT,
            fill=self.ACCENT_COLOR
        )
        y += 70

        # --------------------------------------------------
        # Optional Code Block
        # --------------------------------------------------
        if q.code:
            code_lines = q.code.split("\n")
            line_height = 42
            padding = 20

            wrapped_lines = []
            for raw_line in code_lines:
                wrapped_lines.extend(
                    self.wrap_code_line(
                        draw,
                        raw_line,
                        self.CODE_FONT,
                        max_width - 40
                    )
                )

            block_height = len(wrapped_lines) * line_height + padding * 2

            draw.rounded_rectangle(
                [
                    content_x,
                    y,
                    content_x + max_width,
                    y + block_height
                ],
                radius=18,
                fill=self.CODE_BG
            )

            draw.rectangle(
                [content_x, y, content_x + 6, y + block_height],
                fill=self.ACCENT_COLOR
            )

            cy = y + padding
            for line in wrapped_lines:
                draw.text(
                    (content_x + 20, cy),
                    line,
                    font=self.CODE_FONT,
                    fill=self.TEXT_COLOR
                )
                cy += line_height

            y = cy + padding + 20

        # --------------------------------------------------
        # Explanation Text
        # --------------------------------------------------
        if q.explanation:
            for line in self.wrap_text(draw, q.explanation, self.TEXT_FONT, max_width):
                draw.text(
                    (content_x, y),
                    line,
                    font=self.TEXT_FONT,
                    fill=self.TEXT_COLOR
                )
                y += 46

        # --------------------------------------------------
        # Footer (subtle CTA)
        # --------------------------------------------------
        footer = "Follow for daily Python challenges"
        fw = draw.textbbox((0, 0), footer, font=self.HEADER_FONT)[2]
        draw.text(
            (content_x + (max_width - fw) // 2, self.HEIGHT - 70),
            footer,
            font=self.HEADER_FONT,
            fill=self.SUBTLE_TEXT
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)

    def main():
        questions = generate_questions(1)
        # with open("output/questions.json", "r") as f:
        #     questions_data = json.load(f)
        #     questions = [Question(**q) for q in questions_data]

        # test question image rendering
        print("rendering question images...")
        output_dir = Path(f"output/images/{self.RUN_DATE}/questions")
        output_dir.mkdir(parents=True, exist_ok=True)
        for question in questions:
            renderer.render_question_image(
                question,
                output_dir / f"{question.title.replace(' ', '_')}.png"
            )

        print("Question Images rendered successfully")

        # test answer image rendering
        print("rendering answer images...")
        output_dir = Path(f"output/images/{self.RUN_DATE}/answers")
        output_dir.mkdir(parents=True, exist_ok=True)
        for question in questions:
            renderer.render_answer_image(
                question,
                output_dir / f"{question.title.replace(' ', '_')}.png"
            )

        print("Answer Image rendered successfully")

        # test single post rendering
        print("rendering single post images...")
        output_dir = Path(f"output/images/{self.RUN_DATE}/singles")
        output_dir.mkdir(parents=True, exist_ok=True)
        for question in questions:
            renderer.render_single_post_image(
                question, 
                output_dir / f"{question.title.replace(' ', '_')}.png"
            )

        print("Single post Image rendered successfully")

        renderer.render_day1_cta_image()
        renderer.render_day2_cta_image()
        renderer.render_welcome_image()
# if __name__ == "__main__":
#     renderer = ImageRenderer()
#     # testing
#     # # questions = generate_questions("python internals", 1)
#     with open("output/questions.json", "r") as f:
#         questions_data = json.load(f)
#         questions = [Question(**q) for q in questions_data]

    # test question image rendering
    # output_dir = Path("output/images/questions")
    # output_dir.mkdir(parents=True, exist_ok=True)

    # for question in questions:
    #     # print(question)
    #     renderer.render_question_image(
    #         question,
    #         output_dir / f"{question.title.replace(' ', '_')}.png"
    #     )

    # print("Question Image rendered successfully")

    # test answer image rendering
    # output_dir = Path("output/images/answers")
    # output_dir.mkdir(parents=True, exist_ok=True)

    # for question in questions:
    #     # print(question)
    #     renderer.render_answer_image(
    #         question,
    #         output_dir / f"{question.title.replace(' ', '_')}.png"
    #     )

    # print("Answer Image rendered successfully")

    # test single post rendering
    # for question in questions:
    #     # print(question)
    #     renderer.render_single_post_image(
    #         question,
    #     )

    # print("Single post Image rendered successfully")

    # renderer.render_day1_cta_image()
    # renderer.render_day2_cta_image()
    # renderer.render_welcome_image()