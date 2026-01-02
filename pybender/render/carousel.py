"""
Carousel Image Generator for Instagram Posts.

Carousel-specific image rendering:
- 1080×1080px square format (vs 1080×1920 for reels)
- 6 slides per question: Cover, Question, Wait, Answer, Explanation, CTA
- Optimized layout for carousel readability
"""
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pybender.config.logging_config import setup_logging
from pybender.generator.schema import Question
from pybender.render.layout_profiles import LAYOUT_PROFILES
from pybender.render.layout_resolver import resolve_layout_profile
from pybender.render.text_utils import (
    normalize_code,
    wrap_code_line,
    wrap_text,
    wrap_text_with_prefix,
)
from pybender.render.code_renderer import draw_editor_code_with_ide


logger = logging.getLogger(__name__)


def _ensure_logging_configured() -> None:
    if not logging.getLogger().handlers:
        setup_logging()


class CarouselRenderer:
    """
    Generates carousel slides for Instagram posts.
    
    Each question produces 6 slides:
    1. Cover - Welcome/Question teaser
    2. Question - Full question text
    3. Wait - Prompt to swipe for answer
    4. Answer - Solution reveal
    5. Explanation - Brief reasoning
    6. CTA - Next challenge
    """
    
    def __init__(self):
        _ensure_logging_configured()
        self.MODEL = "gpt-4o-mini"
        # Carousel dimensions (square format)
        self.WIDTH, self.HEIGHT = 1080, 1080
        self.PADDING_X = 50
        self.PADDING_Y = 50
        
        # Colors
        self.BG_COLOR = (9, 12, 24)
        self.CARD_COLOR = (11, 18, 32)
        self.CODE_BG = (15, 23, 42)
        self.TEXT_COLOR = (226, 232, 240)
        self.SUBTLE_TEXT = (148, 163, 184)
        self.ACCENT_COLOR = (76, 201, 240)
        self.SUCCESS_COLOR = (72, 187, 120)
        self.TEXT_PRIMARY = (255, 255, 255)
        self.DIVIDER_COLOR = (30, 41, 59)
        
        self.SUBJECT_ACCENTS = {
            "python": (19, 88, 174),
            "sql": (88, 157, 246),
            "regex": (255, 107, 107),
            "linux": (72, 187, 120),
            "javascript": (255, 223, 99),
            "rust": (237, 125, 49),
            "system_design": (129, 140, 248),
            "docker_k8s": (59, 130, 246),
            "golang": (0, 173, 216),
        }
        
        # Fonts
        self.FONT_DIR = Path("pybender/assets/fonts")
        self.INTER_FONT_DIR = self.FONT_DIR / "Inter-4.1" / "extras" / "ttf"
        self.JETBRAINS_MONO_FONT_DIR = self.FONT_DIR / "JetBrainsMono-2.304" / "fonts" / "ttf"
        
        # Carousel-specific font sizes (smaller to fit square)
        self.TITLE_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 42)
        self.TEXT_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 32)
        self.CODE_FONT = ImageFont.truetype(str(self.JETBRAINS_MONO_FONT_DIR / "JetBrainsMono-Regular.ttf"), 28)
        self.HEADER_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 38)
        self.LABEL_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 32)
        self.SMALL_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 24)
        
        # Assets
        self.ASSETS_DIR = Path("pybender/assets/backgrounds")
        self.LOGO_PATH = self.ASSETS_DIR / "ddop1.PNG"
        self.LOGO_HEIGHT = 35
        self.LOGO_WIDTH = 55
        self.LOGO_PADDING = 15
        
        # Carousel-specific config
        self.IDE_CODE_STYLE = True
        self.IDE_HEADER_HEIGHT = 30
        self.IDE_GUTTER_WIDTH = 35
        self.IDE_HEADER_BG = (20, 26, 40)
        self.IDE_GUTTER_BG = (13, 19, 36)
        self.IDE_LINE_NUMBER_COLOR = (100, 116, 139)
        
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
    
    def _create_base_canvas(self, subject: str) -> Image.Image:
        """Create a base carousel slide."""
        canvas = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
        draw = ImageDraw.Draw(canvas)
        
        # Main card (carousel-optimized)
        card_x, card_y = 30, 30
        card_w, card_h = self.WIDTH - 60, self.HEIGHT - 60
        radius = 24
        
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            fill=self.CARD_COLOR
        )
        
        accent_color = self.SUBJECT_ACCENTS.get(subject, self.ACCENT_COLOR)
        
        return canvas, draw, accent_color
    
    def _add_slide_indicator(self, draw, slide_num: int, total_slides: int = 6):
        """Add slide counter in bottom right."""
        text = f"{slide_num}/{total_slides}"
        bbox = draw.textbbox((0, 0), text, font=self.SMALL_FONT)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = self.WIDTH - self.PADDING_X - text_width
        y = self.HEIGHT - self.PADDING_Y - text_height
        
        draw.text((x, y), text, font=self.SMALL_FONT, fill=self.SUBTLE_TEXT)
    
    def _wrap_text(self, draw, text: str, font, max_width: int) -> list:
        """Wrap text to fit width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def generate_cover_slide(
        self,
        question: Question,
        subject: str,
        out_path: Path
        ) -> None:
        """
        Slide 1: Cover/Welcome slide - engaging and centered.
        
        Layout (vertically & horizontally centered):
        - "DDOP" branding at top (larger)
        - "Daily Dose of Programming" main heading (larger)
        - Subject name (larger)
        - Question title (teaser, larger)
        - Hook line to encourage swipe (larger)
        - Logo (larger)
        - Slide indicator
        """
        canvas, draw, accent_color = self._create_base_canvas(subject)
        
        content_x = self.PADDING_X + 30
        content_width = self.WIDTH - (self.PADDING_X + 30) * 2
        
        # Larger fonts for cover slide
        brand_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 42)
        tagline_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 68)
        title_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 52)
        hook_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 36)
        
        # Calculate total content height for vertical centering
        logo_section_height = 0
        logo_width_scaled = 0
        logo_height_scaled = 0
        if self.LOGO_PATH.exists():
            logo_width_scaled = int(self.LOGO_WIDTH * 1.6)
            logo_height_scaled = int(self.LOGO_HEIGHT * 1.6)
            logo_section_height = logo_height_scaled + 30
        
        # Measure all content
        brand_height = 55
        tagline_height = 80
        title_lines = self._wrap_text(draw, question.title, title_font, content_width - 40)[:2]
        title_height = len(title_lines) * 65 + 30
        hook_height = 45
        
        total_content_height = (logo_section_height + brand_height + tagline_height + 
                               title_height + hook_height + 80)  # gaps
        
        # Start Y position (centered)
        y_pos = (self.HEIGHT - total_content_height) // 2

    
        brand_subtitle = f"Daily Dose of Programming"
        brand_sub_bbox = draw.textbbox((0, 0), brand_subtitle, font=brand_font)
        brand_sub_width = brand_sub_bbox[2] - brand_sub_bbox[0]
        brand_sub_x = (self.WIDTH - brand_sub_width) // 2
        draw.text((brand_sub_x, y_pos), brand_subtitle, font=brand_font, fill=self.SUBTLE_TEXT)
        y_pos += 60

        subject_display = subject.replace('_', ' ').title()
        tagline_text = subject_display
        tagline_bbox = draw.textbbox((0, 0), tagline_text, font=tagline_font)
        tagline_width = tagline_bbox[2] - tagline_bbox[0]
        tagline_x = (self.WIDTH - tagline_width) // 2
        draw.text((tagline_x, y_pos), tagline_text, font=tagline_font, fill=accent_color)
        y_pos += 75
        
        # Divider line (wider and thicker)
        divider_width = 300
        divider_x = (self.WIDTH - divider_width) // 2
        draw.line([(divider_x, y_pos), (divider_x + divider_width, y_pos)], 
                 fill=accent_color, width=3)
        y_pos += 40
        
        # Question title (centered, teaser - max 2 lines, larger)
        for line in title_lines:
            line_bbox = draw.textbbox((0, 0), line, font=title_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (self.WIDTH - line_width) // 2
            draw.text((line_x, y_pos), line, font=title_font, fill=self.TEXT_PRIMARY)
            y_pos += 65
        
        y_pos += 40
        
        # Hook line (centered, subtle, larger)
        hook_text = "Swipe to test your knowledge →"
        hook_bbox = draw.textbbox((0, 0), hook_text, font=hook_font)
        hook_width = hook_bbox[2] - hook_bbox[0]
        hook_x = (self.WIDTH - hook_width) // 2
        draw.text((hook_x, y_pos), hook_text, font=hook_font, fill=self.SUBTLE_TEXT)
        y_pos += 60
        
        # Logo at bottom (centered horizontally, larger)
        if self.LOGO_PATH.exists():
            try:
                logo = Image.open(self.LOGO_PATH).resize((logo_width_scaled, logo_height_scaled))
                logo_x = (self.WIDTH - logo_width_scaled) // 2
                canvas.paste(logo, (logo_x, y_pos), logo if logo.mode == 'RGBA' else None)
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        # Slide indicator
        self._add_slide_indicator(draw, 1)

        canvas.save(out_path)
        logger.debug(f"Generated cover slide: {out_path}")
    
    def generate_question_slide(
        self,
        question: Question,
        subject: str,
        out_path: Path
        ) -> None:
        """
        Slide 2: Question slide with full question text and options.
        
        Layout (vertically centered):
        - Scenario (if available, for docker_k8s/system_design)
        - "Question" label
        - Full question text
        - Code snippet if available
        - Options (A, B, C, D)
        - Slide indicator
        """
        canvas, draw, accent_color = self._create_base_canvas(subject)
        
        content_x = self.PADDING_X + 30
        content_width = self.WIDTH - (self.PADDING_X + 30) * 2
        
        # Subject header at the top
        subject_display = subject.replace('_', ' ').title()
        subject_header_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 28)
        subject_bbox = draw.textbbox((0, 0), subject_display, font=subject_header_font)
        subject_width = subject_bbox[2] - subject_bbox[0]
        subject_x = (self.WIDTH - subject_width) // 2
        draw.text((subject_x, 60), subject_display, font=subject_header_font, fill=accent_color)
        
        # Calculate total content height for vertical centering
        label_height = 50
        
        # Scenario height if available
        scenario_height = 0
        if question.scenario:
            scenario_text = question.scenario.replace("\\n", " ")
            scenario_lines = self._wrap_text(draw, scenario_text, self.TEXT_FONT, content_width - 40)
            scenario_box_padding = 12
            scenario_height = len(scenario_lines) * 40 + scenario_box_padding * 2 + 15  # lines + padding + gap
        
        # Question text height
        q_lines = self._wrap_text(draw, question.question, self.TEXT_FONT, content_width)
        question_text_height = len(q_lines) * 45 + 20
        
        # Code height if available
        code_height = 0
        if question.code:
            code_lines = question.code.split('\n')[:5]  # Limit to 5 lines
            code_height = len(code_lines) * 35 + 50
        
        # Options height
        options_height = 0
        if question.options:
            for opt in question.options[:4]:  # A, B, C, D
                opt_lines = self._wrap_text(draw, opt, self.TEXT_FONT, content_width - 40)
                options_height += len(opt_lines) * 40 + 20
        
        total_content_height = scenario_height + label_height + question_text_height + code_height + options_height
        
        # Start Y position (centered)
        y_pos = (self.HEIGHT - total_content_height) // 2
        
        # Scenario if available (docker_k8s, system_design) - COMES FIRST NOW
        if question.scenario:
            scenario_text = question.scenario.replace("\\n", " ")
            scenario_lines = self._wrap_text(draw, scenario_text, self.TEXT_FONT, content_width - 40)
            
            # "Scenario" label badge
            scenario_label_text = "SCENARIO"
            scenario_label_bbox = draw.textbbox((0, 0), scenario_label_text, font=self.LABEL_FONT)
            scenario_label_width = scenario_label_bbox[2] - scenario_label_bbox[0]
            scenario_label_height = scenario_label_bbox[3] - scenario_label_bbox[1]
            
            # Draw scenario label badge above the box
            label_padding_x = 12
            label_padding_y = 6
            draw.rounded_rectangle(
                [content_x - label_padding_x, y_pos - label_padding_y,
                 content_x + scenario_label_width + label_padding_x, y_pos + scenario_label_height + label_padding_y],
                radius=6,
                fill=(20, 28, 45),
                outline=accent_color,
                width=2
            )
            draw.text((content_x, y_pos), scenario_label_text, font=self.LABEL_FONT, fill=accent_color)
            y_pos += scenario_label_height + label_padding_y + 20
            
            # Scenario box with subtle background
            scenario_box_padding = 12
            scenario_box_height = len(scenario_lines) * 40 + scenario_box_padding * 2
            draw.rounded_rectangle(
                [content_x - scenario_box_padding, y_pos - scenario_box_padding,
                 self.WIDTH - content_x + scenario_box_padding, y_pos + scenario_box_height - scenario_box_padding],
                radius=8,
                fill=(20, 28, 45),
                outline=accent_color,
                width=1
            )
            
            # Draw scenario text lines
            y_offset = y_pos + scenario_box_padding
            for line in scenario_lines:
                draw.text((content_x + 5, y_offset), line, font=self.TEXT_FONT, fill=self.TEXT_PRIMARY)
                y_offset += 40
            
            y_pos += scenario_box_height + 15
        
        # "Question" label with badge background (softer style) - NOW COMES AFTER SCENARIO
        label_text = "QUESTION"
        label_bbox = draw.textbbox((0, 0), label_text, font=self.LABEL_FONT)
        label_width = label_bbox[2] - label_bbox[0]
        label_height = label_bbox[3] - label_bbox[1]
        
        # Draw subtle badge background with accent border
        badge_padding_x = 12
        badge_padding_y = 8
        draw.rounded_rectangle(
            [content_x - badge_padding_x, y_pos - badge_padding_y, 
             content_x + label_width + badge_padding_x, y_pos + label_height + badge_padding_y],
            radius=6,
            fill=(20, 28, 45),  # Subtle dark background
            outline=accent_color,
            width=2
        )
        draw.text((content_x, y_pos), label_text, font=self.LABEL_FONT, fill=accent_color)
        y_pos += label_height + badge_padding_y + 20
        
        # Question text with subtle background box
        question_box_padding = 15
        question_box_height = len(q_lines) * 45 + question_box_padding * 2
        draw.rounded_rectangle(
            [content_x - question_box_padding, y_pos - question_box_padding,
             self.WIDTH - content_x + question_box_padding, y_pos + question_box_height - question_box_padding],
            radius=10,
            fill=(20, 28, 45)  # Slightly lighter than card background
        )
        
        for line in q_lines:
            draw.text((content_x, y_pos), line, font=self.TEXT_FONT, fill=self.TEXT_PRIMARY)
            y_pos += 45
        
        y_pos += question_box_padding
        
        # Code if available (IDE-style)
        if question.code:
            y_pos += 20
            # Normalize code
            normalized_lines = normalize_code(question.code)[:5]  # Limit to 5 source lines
            
            # Draw IDE-style code block
            y_pos = draw_editor_code_with_ide(
                draw=draw,
                code=normalized_lines,
                subject=subject,
                y_cursor=y_pos,
                width=self.WIDTH,
                padding_x=self.PADDING_X,
                code_font=self.CODE_FONT,
                small_label_font=self.SMALL_FONT,
                code_bg=self.CODE_BG,
                ide_header_bg=self.IDE_HEADER_BG,
                ide_gutter_bg=self.IDE_GUTTER_BG,
                text_color=self.TEXT_COLOR,
                subtle_text=self.SUBTLE_TEXT,
                ide_line_number_color=self.IDE_LINE_NUMBER_COLOR,
                language_map=self.LANGUAGE_MAP,
                ide_gutter_width=self.IDE_GUTTER_WIDTH,
                ide_header_height=self.IDE_HEADER_HEIGHT,
                line_height=35
            )
        
        # Options (A, B, C, D)
        if question.options:
            y_pos += 20
            option_labels = ['A', 'B', 'C', 'D']
            for idx, opt in enumerate(question.options[:4]):
                label = option_labels[idx]
                opt_lines = self._wrap_text(draw, opt, self.TEXT_FONT, content_width - 40)
                
                # Option background
                opt_block_height = len(opt_lines) * 40 + 15
                draw.rounded_rectangle(
                    [content_x - 5, y_pos, self.WIDTH - content_x + 5, y_pos + opt_block_height],
                    radius=8,
                    fill=self.CODE_BG
                )
                
                # Option label (A, B, C, D) in accent color
                draw.text((content_x + 5, y_pos + 5), f"{label}.", font=self.LABEL_FONT, fill=accent_color)
                
                # Option text
                opt_y = y_pos + 8
                for line in opt_lines:
                    draw.text((content_x + 35, opt_y), line, font=self.TEXT_FONT, fill=self.TEXT_PRIMARY)
                    opt_y += 40
                
                y_pos += opt_block_height + 12
        
        # Slide indicator
        self._add_slide_indicator(draw, 2)
        
        canvas.save(out_path)
        logger.debug(f"Generated question slide: {out_path}")
    
    def generate_wait_slide(
        self,
        subject: str,
        out_path: Path
        ) -> None:
        """
        Slide 3: Wait slide prompting swipe for answer.
        
        Layout (vertically & horizontally centered, larger):
        - "Swipe" prompt centered (larger font)
        - Directional arrow text
        - Subtle background
        - Slide indicator
        """
        canvas, draw, accent_color = self._create_base_canvas(subject)
        
        # Larger fonts for wait slide
        prompt_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 60)
        subtext_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 36)
        
        # Centered prompt
        prompt = "Swipe to reveal answer →"
        subtext = "Keep going for the solution"
        
        # Calculate content height for vertical centering
        prompt_bbox = draw.textbbox((0, 0), prompt, font=prompt_font)
        prompt_h = prompt_bbox[3] - prompt_bbox[1]
        
        sub_bbox = draw.textbbox((0, 0), subtext, font=subtext_font)
        sub_h = sub_bbox[3] - sub_bbox[1]
        
        total_height = prompt_h + 50 + sub_h  # prompt + gap + subtext
        
        # Start Y position (centered)
        y_pos = (self.HEIGHT - total_height) // 2
        
        # Prompt (centered horizontally)
        prompt_bbox = draw.textbbox((0, 0), prompt, font=prompt_font)
        prompt_w = prompt_bbox[2] - prompt_bbox[0]
        x = (self.WIDTH - prompt_w) // 2
        draw.text((x, y_pos), prompt, font=prompt_font, fill=accent_color)
        
        # Subtext below (centered horizontally, larger)
        y_pos += prompt_h + 50
        sub_bbox = draw.textbbox((0, 0), subtext, font=subtext_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_x = (self.WIDTH - sub_w) // 2
        draw.text((sub_x, y_pos), subtext, font=subtext_font, fill=self.SUBTLE_TEXT)
        
        # Slide indicator
        self._add_slide_indicator(draw, 3)
        
        canvas.save(out_path)
        logger.debug(f"Generated wait slide: {out_path}")
    
    def generate_answer_slide(
        self,
        question: Question,
        subject: str,
        out_path: Path
        ) -> None:
        """
        Slide 4: Answer slide - reuses question layout with correct option highlighted.
        
        Layout (same as question slide):
        - "Answer" label (instead of "Question")
        - Full question text
        - Code snippet if available
        - Options (A, B, C, D) with correct one highlighted in green
        - Hook line at bottom to swipe for explanation
        - Slide indicator
        """
        canvas, draw, accent_color = self._create_base_canvas(subject)
        
        content_x = self.PADDING_X + 30
        content_width = self.WIDTH - (self.PADDING_X + 30) * 2
        
        # Subject header at the top
        subject_display = subject.replace('_', ' ').title()
        subject_header_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 28)
        subject_bbox = draw.textbbox((0, 0), subject_display, font=subject_header_font)
        subject_width = subject_bbox[2] - subject_bbox[0]
        subject_x = (self.WIDTH - subject_width) // 2
        draw.text((subject_x, 60), subject_display, font=subject_header_font, fill=accent_color)
        
        # Calculate total content height for vertical centering
        label_height = 50
        
        # Scenario height if available
        scenario_height = 0
        if question.scenario:
            scenario_text = question.scenario.replace("\\n", " ")
            scenario_lines = self._wrap_text(draw, scenario_text, self.TEXT_FONT, content_width - 40)
            scenario_box_padding = 12
            scenario_height = len(scenario_lines) * 40 + scenario_box_padding * 2 + 15  # lines + padding + gap
        
        # Question text height
        q_lines = self._wrap_text(draw, question.question, self.TEXT_FONT, content_width)
        question_text_height = len(q_lines) * 45 + 20
        
        # Code height if available
        code_height = 0
        if question.code:
            code_lines = question.code.split('\n')[:5]
            code_height = len(code_lines) * 35 + 50
        
        # Options height
        options_height = 0
        if question.options:
            for opt in question.options[:4]:
                opt_lines = self._wrap_text(draw, opt, self.TEXT_FONT, content_width - 40)
                options_height += len(opt_lines) * 40 + 20
        
        # Hook line height
        hook_height = 40
        
        total_content_height = scenario_height + label_height + question_text_height + code_height + options_height + hook_height
        
        # Start Y position (centered)
        y_pos = (self.HEIGHT - total_content_height) // 2
        
        # Scenario if available (docker_k8s, system_design) - COMES FIRST
        if question.scenario:
            scenario_text = question.scenario.replace("\\n", " ")
            scenario_lines = self._wrap_text(draw, scenario_text, self.TEXT_FONT, content_width - 40)
            
            # "Scenario" label badge
            scenario_label_text = "SCENARIO"
            scenario_label_bbox = draw.textbbox((0, 0), scenario_label_text, font=self.LABEL_FONT)
            scenario_label_width = scenario_label_bbox[2] - scenario_label_bbox[0]
            scenario_label_height = scenario_label_bbox[3] - scenario_label_bbox[1]
            
            # Draw scenario label badge above the box
            label_padding_x = 12
            label_padding_y = 6
            draw.rounded_rectangle(
                [content_x - label_padding_x, y_pos - label_padding_y,
                 content_x + scenario_label_width + label_padding_x, y_pos + scenario_label_height + label_padding_y],
                radius=6,
                fill=(20, 28, 45),
                outline=accent_color,
                width=2
            )
            draw.text((content_x, y_pos), scenario_label_text, font=self.LABEL_FONT, fill=accent_color)
            y_pos += scenario_label_height + label_padding_y + 20
            
            # Scenario box with subtle background
            scenario_box_padding = 12
            scenario_box_height = len(scenario_lines) * 40 + scenario_box_padding * 2
            draw.rounded_rectangle(
                [content_x - scenario_box_padding, y_pos - scenario_box_padding,
                 self.WIDTH - content_x + scenario_box_padding, y_pos + scenario_box_height - scenario_box_padding],
                radius=8,
                fill=(20, 28, 45),
                outline=accent_color,
                width=1
            )
            
            # Draw scenario text lines
            y_offset = y_pos + scenario_box_padding
            for line in scenario_lines:
                draw.text((content_x + 5, y_offset), line, font=self.TEXT_FONT, fill=self.TEXT_PRIMARY)
                y_offset += 40
            
            y_pos += scenario_box_height + 15
        
        # "Answer" label with badge background (softer green style)
        label_text = "ANSWER"
        label_bbox = draw.textbbox((0, 0), label_text, font=self.LABEL_FONT)
        label_width = label_bbox[2] - label_bbox[0]
        label_height_actual = label_bbox[3] - label_bbox[1]
        
        # Draw subtle badge with green accent border
        badge_padding_x = 12
        badge_padding_y = 8
        draw.rounded_rectangle(
            [content_x - badge_padding_x, y_pos - badge_padding_y, 
             content_x + label_width + badge_padding_x, y_pos + label_height_actual + badge_padding_y],
            radius=6,
            fill=(15, 35, 25),  # Dark green tint
            outline=self.SUCCESS_COLOR,
            width=2
        )
        draw.text((content_x, y_pos), label_text, font=self.LABEL_FONT, fill=self.SUCCESS_COLOR)
        y_pos += label_height_actual + badge_padding_y + 20
        
        # Question text with subtle background box
        question_box_padding = 15
        question_box_height = len(q_lines) * 45 + question_box_padding * 2
        draw.rounded_rectangle(
            [content_x - question_box_padding, y_pos - question_box_padding,
             self.WIDTH - content_x + question_box_padding, y_pos + question_box_height - question_box_padding],
            radius=10,
            fill=(20, 28, 45)
        )
        
        for line in q_lines:
            draw.text((content_x, y_pos), line, font=self.TEXT_FONT, fill=self.TEXT_PRIMARY)
            y_pos += 45
        
        y_pos += question_box_padding
        
        # Code if available (IDE-style)
        if question.code:
            y_pos += 20
            normalized_lines = normalize_code(question.code)[:5]
            
            y_pos = draw_editor_code_with_ide(
                draw=draw,
                code=normalized_lines,
                subject=subject,
                y_cursor=y_pos,
                width=self.WIDTH,
                padding_x=self.PADDING_X,
                code_font=self.CODE_FONT,
                small_label_font=self.SMALL_FONT,
                code_bg=self.CODE_BG,
                ide_header_bg=self.IDE_HEADER_BG,
                ide_gutter_bg=self.IDE_GUTTER_BG,
                text_color=self.TEXT_COLOR,
                subtle_text=self.SUBTLE_TEXT,
                ide_line_number_color=self.IDE_LINE_NUMBER_COLOR,
                language_map=self.LANGUAGE_MAP,
                ide_gutter_width=self.IDE_GUTTER_WIDTH,
                ide_header_height=self.IDE_HEADER_HEIGHT,
                line_height=35
            )
        
        # Options (A, B, C, D) with correct answer highlighted
        correct_index = None
        if question.correct:
            # Find correct option index (A=0, B=1, C=2, D=3)
            correct_index = ord(question.correct.upper()) - ord('A')
        
        if question.options:
            y_pos += 20
            option_labels = ['A', 'B', 'C', 'D']
            for idx, opt in enumerate(question.options[:4]):
                label = option_labels[idx]
                opt_lines = self._wrap_text(draw, opt, self.TEXT_FONT, content_width - 40)
                
                # Check if this is the correct option
                is_correct = (idx == correct_index)
                
                # Option background - green highlight if correct
                opt_block_height = len(opt_lines) * 40 + 15
                if is_correct:
                    # Green highlighted background with border
                    draw.rounded_rectangle(
                        [content_x - 5, y_pos, self.WIDTH - content_x + 5, y_pos + opt_block_height],
                        radius=8,
                        fill=(20, 45, 30),  # Dark green
                        outline=self.SUCCESS_COLOR,
                        width=3
                    )
                    label_color = self.SUCCESS_COLOR
                    text_color = self.SUCCESS_COLOR
                else:
                    # Normal background for incorrect options
                    draw.rounded_rectangle(
                        [content_x - 5, y_pos, self.WIDTH - content_x + 5, y_pos + opt_block_height],
                        radius=8,
                        fill=self.CODE_BG
                    )
                    label_color = accent_color  # Keep accent color for labels
                    text_color = self.SUBTLE_TEXT  # Dim the text slightly
                
                # Option label (A, B, C, D) - always prominent
                draw.text((content_x + 5, y_pos + 5), f"{label}.", font=self.LABEL_FONT, fill=label_color)
                
                # Option text
                opt_y = y_pos + 8
                for line in opt_lines:
                    draw.text((content_x + 35, opt_y), line, font=self.TEXT_FONT, fill=text_color)
                    opt_y += 40
                
                y_pos += opt_block_height + 12
        
        # Hook line at bottom to encourage swipe
        y_pos += 15
        hook_text = "Swipe to understand why →"
        hook_bbox = draw.textbbox((0, 0), hook_text, font=self.SMALL_FONT)
        hook_width = hook_bbox[2] - hook_bbox[0]
        hook_x = (self.WIDTH - hook_width) // 2
        draw.text((hook_x, y_pos), hook_text, font=self.SMALL_FONT, fill=accent_color)
        
        # Slide indicator
        self._add_slide_indicator(draw, 4)
        
        canvas.save(out_path)
        logger.debug(f"Generated answer slide: {out_path}")

    def generate_explanation_slide(
        self,
        question: Question,
        subject: str,
        out_path: Path
        ) -> None:
        """
        Slide 5: Explanation slide - focused on WHY with clean, centered design.

        Layout (vertically centered):
        - "Explanation" label
        - Correct answer in subtle box (context)
        - Explanation text (larger, readable)
        - No code (already shown in previous slides)
        - Slide indicator
        """
        canvas, draw, accent_color = self._create_base_canvas(subject)
        
        content_x = self.PADDING_X + 30
        content_width = self.WIDTH - (self.PADDING_X + 30) * 2
        
        # Subject header at the top
        subject_display = subject.replace('_', ' ').title()
        subject_header_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 28)
        subject_bbox = draw.textbbox((0, 0), subject_display, font=subject_header_font)
        subject_width = subject_bbox[2] - subject_bbox[0]
        subject_x = (self.WIDTH - subject_width) // 2
        draw.text((subject_x, 60), subject_display, font=subject_header_font, fill=accent_color)
        
        # Calculate content height for vertical centering
        label_height = 50
        
        # Correct answer context height
        answer_context_height = 0
        if question.correct and question.options:
            correct_idx = ord(question.correct.upper()) - ord('A')
            if 0 <= correct_idx < len(question.options):
                correct_text = f"{question.correct}. {question.options[correct_idx]}"
                correct_lines = self._wrap_text(draw, correct_text, self.TEXT_FONT, content_width - 40)
                answer_context_height = len(correct_lines) * 40 + 30
        
        # Explanation text height (use larger TEXT_FONT instead of SMALL_FONT)
        explanation = question.explanation or "Here's why this works."
        exp_lines = self._wrap_text(draw, explanation, self.TEXT_FONT, content_width - 30)
        exp_height = len(exp_lines) * 42 + 40
        
        total_content_height = label_height + answer_context_height + exp_height
        
        # Start Y position (centered)
        y_pos = (self.HEIGHT - total_content_height) // 2
        
        # "Explanation" label with badge background
        label_text = "EXPLANATION"
        label_bbox = draw.textbbox((0, 0), label_text, font=self.LABEL_FONT)
        label_width = label_bbox[2] - label_bbox[0]
        label_height_actual = label_bbox[3] - label_bbox[1]
        
        # Draw badge background
        badge_padding_x = 12
        badge_padding_y = 8
        draw.rounded_rectangle(
            [content_x - badge_padding_x, y_pos - badge_padding_y, 
             content_x + label_width + badge_padding_x, y_pos + label_height_actual + badge_padding_y],
            radius=6,
            fill=(20, 28, 45),
            outline=accent_color,
            width=2
        )
        draw.text((content_x, y_pos), label_text, font=self.LABEL_FONT, fill=accent_color)
        y_pos += label_height_actual + badge_padding_y + 30
        
        # Show correct answer in subtle context box
        if question.correct and question.options:
            correct_idx = ord(question.correct.upper()) - ord('A')
            if 0 <= correct_idx < len(question.options):
                correct_text = f"{question.correct}. {question.options[correct_idx]}"
                correct_lines = self._wrap_text(draw, correct_text, self.TEXT_FONT, content_width - 40)
                
                # Subtle green tinted box
                correct_box_height = len(correct_lines) * 40 + 20
                draw.rounded_rectangle(
                    [content_x - 10, y_pos, self.WIDTH - content_x + 10, y_pos + correct_box_height],
                    radius=10,
                    fill=(15, 35, 25),  # Dark green tint
                    outline=self.SUCCESS_COLOR,
                    width=1
                )
                
                y_pos += 10
                for line in correct_lines:
                    draw.text((content_x + 5, y_pos), line, font=self.TEXT_FONT, fill=self.SUCCESS_COLOR)
                    y_pos += 40
                
                y_pos += 20
        
        # Explanation text - larger and more prominent
        explanation_box_padding = 15
        explanation_box_height = len(exp_lines) * 42 + explanation_box_padding * 2
        
        # Subtle background for explanation
        draw.rounded_rectangle(
            [content_x - explanation_box_padding, y_pos - explanation_box_padding,
             self.WIDTH - content_x + explanation_box_padding, y_pos + explanation_box_height - explanation_box_padding],
            radius=10,
            fill=(20, 28, 45)
        )
        
        for line in exp_lines:
            draw.text((content_x, y_pos), line, font=self.TEXT_FONT, fill=self.TEXT_PRIMARY)
            y_pos += 42
        
        # Slide indicator
        self._add_slide_indicator(draw, 5)
        
        canvas.save(out_path)
        logger.debug(f"Generated explanation slide: {out_path}")
    
    def generate_cta_slide(
        self,
        subject: str,
        out_path: Path
        ) -> None:
        """
        Slide 6: Call-to-Action slide for next challenge.
        
        Layout (vertically & horizontally centered):
        - Logo (larger)
        - "Nice Job!" message (larger)
        - "Next Challenge" button (larger)
        - Follow/Share prompt
        """
        canvas, draw, accent_color = self._create_base_canvas(subject)
        
        content_x = self.PADDING_X + 30
        content_width = self.WIDTH - (self.PADDING_X + 30) * 2
        
        # Larger fonts for CTA
        congrats_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 72)
        button_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 42)
        cta_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 32)
        
        # Calculate total content height for vertical centering
        logo_height = 0
        logo_width_scaled = 0
        logo_height_scaled = 0
        if self.LOGO_PATH.exists():
            logo_width_scaled = int(self.LOGO_WIDTH * 1.8)  # Larger logo
            logo_height_scaled = int(self.LOGO_HEIGHT * 1.8)
            logo_height = logo_height_scaled + 50
        
        # Measure all content
        congrats_bbox = draw.textbbox((0, 0), "Nice Job!", font=congrats_font)
        congrats_height = congrats_bbox[3] - congrats_bbox[1] + 40
        
        divider_height = 40
        
        # Button dimensions
        button_text = "Ready for Next Challenge?"
        button_padding = 20
        button_bbox = draw.textbbox((0, 0), button_text, font=button_font)
        button_height = button_bbox[3] - button_bbox[1] + button_padding * 2
        
        cta_bbox = draw.textbbox((0, 0), "Follow for daily programming challenges", font=cta_font)
        cta_height = cta_bbox[3] - cta_bbox[1]
        
        total_content_height = logo_height + congrats_height + divider_height + button_height + cta_height + 100
        
        # Start Y position (centered)
        y_pos = (self.HEIGHT - total_content_height) // 2
        
        # Logo (centered horizontally, larger)
        if self.LOGO_PATH.exists():
            try:
                logo = Image.open(self.LOGO_PATH).resize((logo_width_scaled, logo_height_scaled))
                logo_x = (self.WIDTH - logo_width_scaled) // 2
                canvas.paste(logo, (logo_x, y_pos), logo if logo.mode == 'RGBA' else None)
                y_pos += logo_height_scaled + 50
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        # "Nice Job!" message (centered, larger)
        congrats_text = "Nice Job!"
        congrats_bbox = draw.textbbox((0, 0), congrats_text, font=congrats_font)
        congrats_width = congrats_bbox[2] - congrats_bbox[0]
        congrats_x = (self.WIDTH - congrats_width) // 2
        draw.text((congrats_x, y_pos), congrats_text, font=congrats_font, fill=self.SUCCESS_COLOR)
        y_pos += congrats_bbox[3] - congrats_bbox[1] + 40
        
        # Divider (centered, wider)
        divider_width = 350
        divider_x = (self.WIDTH - divider_width) // 2
        draw.line(
            [(divider_x, y_pos), (divider_x + divider_width, y_pos)],
            fill=self.DIVIDER_COLOR,
            width=3
        )
        y_pos += 50
        
        # "Next Challenge" button (centered, larger)
        button_bbox = draw.textbbox((0, 0), button_text, font=button_font)
        button_width = button_bbox[2] - button_bbox[0] + button_padding * 2
        button_x = (self.WIDTH - button_width) // 2
        
        draw.rounded_rectangle(
            [button_x, y_pos, button_x + button_width, y_pos + button_height],
            radius=12,
            fill=accent_color
        )
        draw.text((button_x + button_padding, y_pos + button_padding), 
                 button_text, font=button_font, fill=self.BG_COLOR)
        
        y_pos += button_height + 50
        
        # Follow/Share prompt (centered, larger text)
        cta_text = "Follow @ddop for daily programming challenges"
        cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cta_width = cta_bbox[2] - cta_bbox[0]
        cta_x = (self.WIDTH - cta_width) // 2
        
        # Draw text in parts: normal text + highlighted @ddop
        prefix = "Follow "
        suffix = " for daily programming challenges"
        handle = "@ddop"
        
        # Calculate x position for prefix
        prefix_bbox = draw.textbbox((0, 0), prefix, font=cta_font)
        prefix_width = prefix_bbox[2] - prefix_bbox[0]
        
        # Draw prefix
        draw.text((cta_x, y_pos), prefix, font=cta_font, fill=self.SUBTLE_TEXT)
        
        # Draw @ddop in BG_COLOR
        handle_x = cta_x + prefix_width
        draw.text((handle_x, y_pos), handle, font=cta_font, fill=accent_color)
        
        # Draw suffix
        handle_bbox = draw.textbbox((0, 0), handle, font=cta_font)
        handle_width = handle_bbox[2] - handle_bbox[0]
        suffix_x = handle_x + handle_width
        draw.text((suffix_x, y_pos), suffix, font=cta_font, fill=self.SUBTLE_TEXT)
        
        # Slide indicator
        self._add_slide_indicator(draw, 6)
        
        canvas.save(out_path)
        logger.debug(f"Generated CTA slide: {out_path}")
    
    def generate_carousel_slides(
        self,
        question: Question,
        carousel_dir: Path,
        subject: str,
        question_id: str
        ) -> list:
        """
        Generate all 6 carousel slides for a question.
        
        Returns:
            List of paths to generated carousel images
        """
        carousel_dir.mkdir(parents=True, exist_ok=True)
        
        slides = []
        
        # Slide 1: Cover
        slide_1_path = carousel_dir / f"{question_id}_carousel_01_cover.png"
        self.generate_cover_slide(question, subject, slide_1_path)
        slides.append(str(slide_1_path))
        
        # Slide 2: Question
        slide_2_path = carousel_dir / f"{question_id}_carousel_02_question.png"
        self.generate_question_slide(question, subject, slide_2_path)
        slides.append(str(slide_2_path))
        
        # Slide 3: Wait
        slide_3_path = carousel_dir / f"{question_id}_carousel_03_wait.png"
        self.generate_wait_slide(subject, slide_3_path)
        slides.append(str(slide_3_path))
        
        # Slide 4: Answer reveal
        slide_4_path = carousel_dir / f"{question_id}_carousel_04_answer.png"
        self.generate_answer_slide(question, subject, slide_4_path)
        slides.append(str(slide_4_path))
        
        # Slide 5: Explanation
        slide_5_path = carousel_dir / f"{question_id}_carousel_05_explanation.png"
        self.generate_explanation_slide(question, subject, slide_5_path)
        slides.append(str(slide_5_path))
        
        # Slide 6: CTA
        slide_6_path = carousel_dir / f"{question_id}_carousel_06_cta.png"
        self.generate_cta_slide(subject, slide_6_path)
        slides.append(str(slide_6_path))
        
        logger.info(f"Generated 6 carousel slides for {question_id}")
        return slides



# if __name__ == "__main__":#   
#     renderer = CarouselRenderer()
#     #     # Test with a sample question
#     from pybender.generator.schema import Question
#     q = {
#         "question_id": "2026-01-01_191751_q01",
#         "title": "Node Pressure and Eviction Signals",
#         "code": "",
#         "scenario": "Your pod on Node A has gone OOM due to high memory usage. Kubelet logs show eviction signals triggered as memory pressure increases, causing critical application downtime.",
#         "question": "In this situation, what action can alleviate memory pressure?",
#         "options": [
#           "Increase node's memory resources",
#           "Scale down the pod replicas",
#           "Reduce resource limits for pods",
#           "Add more CPU to the node"
#         ],
#         "correct": "A",
#         "explanation": "Increasing memory resources on the node decreases the chances of eviction due to OOM, allowing critical applications to remain stable. Adjusting pod limits could lead to more issues if the base memory isn't sufficient, making it a temporary fix rather than a solution."
#       }

#     q = Question(**q)  
#     subject = "docker_k8s"
#     carousel_dir = Path(f"output_1/{subject}") / "carousels" / "test_carousel"
    
#     slides = renderer.generate_carousel_slides(
#                 question=q,
#                 carousel_dir=carousel_dir,
#                 subject=subject,
#                 question_id=q.question_id,
#             )