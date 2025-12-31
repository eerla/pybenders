import json
import random
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
        self.CODE_BLOCK_PADDING = 20
        self.CODE_LINE_HEIGHT = 48
        self.CODE_INNER_PADDING_X = 24
        self.CODE_MAX_WIDTH = self.WIDTH - (self.PADDING_X * 2) - 40
        # Colors (match CTA theme)
        self.BG_COLOR = (9, 12, 24) # 
        self.CARD_COLOR = (11, 18, 32)
        self.CODE_BG = (15, 23, 42)
        self.TEXT_COLOR = (226, 232, 240)
        self.SUBTLE_TEXT = (148, 163, 184)
        self.ACCENT_COLOR = (76, 201, 240)
        self.CORRECT_BG = (20, 45, 70)
        self.SUCCESS_COLOR = (72, 187, 120)
        self.TEXT_PRIMARY = (255, 255, 255)
        self.TEXT_SECONDARY = (160, 174, 192)
        self.DIVIDER_COLOR = (30, 41, 59)  # subtle line
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
        
        self.base_dir = Path("output")
        # self.base_dir = Path(r"G:\My Drive\output")  # Change to google drive path
        # Fonts
        self.FONT_DIR = Path("pybender/assets/fonts")
        self.INTER_FONT_DIR = self.FONT_DIR / "Inter-4.1" / "extras" / "ttf"
        self.JETBRAINS_MONO_FONT_DIR = self.FONT_DIR / "JetBrainsMono-2.304" / "fonts" / "ttf"
        self.TITLE_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 48)
        self.TEXT_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 38)
        self.CODE_FONT = ImageFont.truetype(str(self.JETBRAINS_MONO_FONT_DIR / "JetBrainsMono-Regular.ttf"), 38)
        self.HEADER_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 44)
        self.FOOTER_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 36)
        self.TABLE_HEADER_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 36)
        self.TABLE_CELL_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 36)
        self.BADGE_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 36)
        self.SMALL_LABEL_FONT = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 38)
        # self.REGEX_FONT = ImageFont.truetype(str(self.JETBRAINS_MONO_FONT_DIR / "FiraCode-Regular.ttf"), 48)

        # Logo config
        self.LOGO_PATH = Path("pybender/assets/backgrounds/ddop1.PNG")
        self.LOGO_HEIGHT = 40  # 40x120 pixels
        self.LOGO_WIDTH = 60  # 40x120 pixels
        self.LOGO_PADDING = 20  # 20px from edges

        # IDE-style code config
        self.WRITE_METADATA = False  # Set to True to write metadata.json
        self.USE_STATIC_QUESTIONS = False  # Set to True to use static questions from output/questions.json
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

    # ---------- SCENARIO (STYLED) ----------
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
        lines = self.wrap_text_with_prefix(
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

    # ---------- SQL RESULT TABLE ----------
    def _draw_sql_result_table(self, canvas, table: dict | None): # not used currently
        if not table:
            return

        columns = table.get("columns", [])
        rows = table.get("rows", [])

        if not columns or not rows:
            return

        font_header = self.TABLE_HEADER_FONT
        font_cell = self.TABLE_CELL_FONT

        cell_padding_x = 18
        cell_padding_y = 12
        row_height = 52

        # Calculate column widths
        col_widths = []
        for col_idx, col in enumerate(columns):
            max_text_width = self.draw.textlength(col, font=font_header)
            for row in rows:
                cell_text = str(row[col_idx])
                max_text_width = max(
                    max_text_width,
                    self.draw.textlength(cell_text, font=font_cell),
                )
            col_widths.append(max_text_width + cell_padding_x * 2)

        table_width = sum(col_widths)
        x = (self.WIDTH - table_width) // 2
        y = self.y_cursor

        # Background
        total_height = row_height * (len(rows) + 1)
        self.draw.rounded_rectangle(
            [x, y, x + table_width, y + total_height],
            radius=16,
            fill=self.CODE_BG,
        )

        # Accent bar
        self.draw.rectangle(
            [x, y, x + 6, y + total_height],
            fill=self.ACCENT_COLOR,
        )

        # Header row
        cx = x
        for idx, col in enumerate(columns):
            self.draw.text(
                (cx + cell_padding_x, y + cell_padding_y),
                col,
                font=font_header,
                fill=self.TEXT_COLOR,
            )
            cx += col_widths[idx]

        # Divider
        y += row_height
        self.draw.line(
            [x, y, x + table_width, y],
            fill=self.DIVIDER_COLOR,
            width=2,
        )

        # Data rows
        for row in rows:
            cx = x
            for idx, cell in enumerate(row):
                self.draw.text(
                    (cx + cell_padding_x, y + cell_padding_y),
                    str(cell),
                    font=font_cell,
                    fill=self.TEXT_COLOR,
                )
                cx += col_widths[idx]
            y += row_height

        self.y_cursor += total_height + 28

    # ---------- REGEX MATCH ---------- not used currently
    def _draw_regex_match( 
        self,
        canvas,
        pattern: str,
        input_text: str,
        match_text: str,
    ):
        font_label = self.SMALL_LABEL_FONT
        font_code = self.CODE_FONT

        block_padding = 20
        line_height = 48
        max_width = self.WIDTH - (self.PADDING_X * 2) - 40

        def draw_block(label, content, color):
            nonlocal max_width

            # Label
            self.draw.text(
                (self.PADDING_X, self.y_cursor),
                label,
                font=font_label,
                fill=color,
            )
            self.y_cursor += 30

            # Wrapped content
            lines = self.wrap_text(self.draw, content, font_code, max_width)
            block_height = line_height * len(lines) + block_padding * 2

            # Background
            self.draw.rounded_rectangle(
                [
                    self.PADDING_X,
                    self.y_cursor,
                    self.WIDTH - self.PADDING_X,
                    self.y_cursor + block_height,
                ],
                radius=16,
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
                fill=color,
            )

            y = self.y_cursor + block_padding
            for line in lines:
                self.draw.text(
                    (self.PADDING_X + 24, y),
                    line,
                    font=font_code,
                    fill=self.TEXT_COLOR,
                )
                y += line_height

            self.y_cursor += block_height + 24

        draw_block("Pattern", pattern, "#F7C948")
        draw_block("Input", input_text, "#5DA9E9")
        draw_block("Match", match_text, "#4ADE80")

    # ---------- CODE (IDE STYLE) ----------
    def _draw_editor_code_with_ide(self, canvas, code: str, subject: str):
        """
        Draw code with IDE-style header bar and line numbers.
        Line numbers sync with source lines, not wrapped display lines.
        Only shows line number on first wrapped line of each source line.
        """
        font = self.CODE_FONT
        line_height = 48
        max_width = self.WIDTH - (self.PADDING_X * 2) - 40 - self.IDE_GUTTER_WIDTH

        # Wrap code lines and track which source line each wrapped line belongs to
        wrapped_with_line_map = []  # List of (wrapped_line, source_line_num, is_first_of_source)
        for src_line_idx, src_line in enumerate(code, start=1):
            wrapped = self.wrap_code_line(self.draw, src_line, font, max_width)
            for wrap_idx, wline in enumerate(wrapped):
                is_first = (wrap_idx == 0)  # Only the first wrapped line gets the line number
                wrapped_with_line_map.append((wline, src_line_idx, is_first))

        wrapped_lines = [item[0] for item in wrapped_with_line_map]
        code_block_height = len(wrapped_lines) * line_height + 30

        # Draw unified IDE window (header + code as one block)
        total_height = self.IDE_HEADER_HEIGHT + code_block_height
        self.draw.rounded_rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.WIDTH - self.PADDING_X,
                self.y_cursor + total_height,
            ],
            radius=18,
            fill=self.CODE_BG,
        )

        # Draw header section on top
        self.draw.rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.WIDTH - self.PADDING_X,
                self.y_cursor + self.IDE_HEADER_HEIGHT,
            ],
            fill=self.IDE_HEADER_BG,
        )

        # Re-apply rounded corners to header top
        self.draw.rounded_rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.WIDTH - self.PADDING_X,
                self.y_cursor + self.IDE_HEADER_HEIGHT,
            ],
            radius=18,
            fill=self.IDE_HEADER_BG,
            corners=(True, True, False, False)  # Only round top corners
        )

        # Draw window control dots in header (macOS/VS Code style)
        dot_y = self.y_cursor + self.IDE_HEADER_HEIGHT // 2
        dot_radius = 5
        dot_spacing = 16
        start_x = self.PADDING_X + 12
        
        # Close (red)
        self.draw.ellipse(
            [start_x, dot_y - dot_radius, start_x + dot_radius * 2, dot_y + dot_radius],
            fill=(255, 95, 86)
        )
        # Minimize (yellow)
        self.draw.ellipse(
            [start_x + dot_spacing, dot_y - dot_radius, start_x + dot_spacing + dot_radius * 2, dot_y + dot_radius],
            fill=(255, 189, 46)
        )
        # Maximize (green)
        self.draw.ellipse(
            [start_x + dot_spacing * 2, dot_y - dot_radius, start_x + dot_spacing * 2 + dot_radius * 2, dot_y + dot_radius],
            fill=(40, 201, 64)
        )

        # Draw language badge in header (vertically centered)
        language = self.LANGUAGE_MAP.get(subject, subject.title())
        badge_text = f"  daily dose of programming  "
        
        # Get text bounding box for vertical centering
        bbox = self.draw.textbbox((0, 0), badge_text, font=self.SMALL_LABEL_FONT)
        text_height = bbox[3] - bbox[1]
        text_width = self.draw.textlength(badge_text, font=self.SMALL_LABEL_FONT)
        
        # Calculate dots area width (3 dots + spacing on left side)
        dots_area_width = 12 + (dot_radius * 2) + dot_spacing + (dot_radius * 2) + dot_spacing + (dot_radius * 2) + 12
        
        # Center text horizontally, then shift LEFT by half the dots width to compensate
        badge_x = (self.WIDTH - text_width) // 2 - (dots_area_width // 2)
        
        # Center text vertically in header
        badge_y = self.y_cursor + (self.IDE_HEADER_HEIGHT - text_height) // 2
        
        self.draw.text(
            (badge_x, badge_y),
            badge_text,
            font=self.CODE_FONT,
            fill=self.SUBTLE_TEXT,
        )

        # Move cursor to code section
        code_y_start = self.y_cursor + self.IDE_HEADER_HEIGHT

        # Draw gutter background
        self.draw.rectangle(
            [
                self.PADDING_X,
                code_y_start,
                self.PADDING_X + self.IDE_GUTTER_WIDTH,
                code_y_start + code_block_height,
            ],
            fill=self.IDE_GUTTER_BG,
        )

        # Draw gutter separator line
        self.draw.line(
            [
                self.PADDING_X + self.IDE_GUTTER_WIDTH,
                code_y_start,
                self.PADDING_X + self.IDE_GUTTER_WIDTH,
                code_y_start + code_block_height,
            ],
            fill=(25, 32, 47),
            width=5
        )

        # Draw line numbers and code
        text_x = self.PADDING_X + self.IDE_GUTTER_WIDTH + 12
        text_y = code_y_start + 15

        for wline, src_line_num, is_first in wrapped_with_line_map:
            # Draw line number only for first wrapped line of each source line
            if is_first:
                self.draw.text(
                    (self.PADDING_X + 8, text_y),
                    str(src_line_num),
                    font=self.SMALL_LABEL_FONT,
                    fill=self.IDE_LINE_NUMBER_COLOR,
                )

            # Draw code
            self.draw.text(
                (text_x, text_y),
                wline,
                font=font,
                fill=self.TEXT_COLOR,
            )
            
            text_y += line_height

        self.y_cursor += total_height + 20
    
    # ---------- CODE ----------
    def _draw_editor_code(self, canvas, code: str):
        font = self.CODE_FONT
        line_height = 48
        max_width = self.WIDTH - (self.PADDING_X * 2) - 40

        # -------- Measure total height first --------
        wrapped_lines = []
        for line in code:
            wrapped = self.wrap_code_line(self.draw, line, font, max_width)
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
            wrapped = self.wrap_code_line(self.draw, line, font, max_width)
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


    def _draw_inline_badge(self, text: str, color: str): # not used currently
        font = self.BADGE_FONT
        padding = 12
        text_w = self.draw.textlength(text, font=font)
        box_w = text_w + padding * 2
        box_h = 36

        self.draw.rounded_rectangle(
            [
                self.PADDING_X,
                self.y_cursor,
                self.PADDING_X + box_w,
                self.y_cursor + box_h,
            ],
            radius=12,
            fill=color,
        )

        self.draw.text(
            (self.PADDING_X + padding, self.y_cursor + 6),
            text,
            font=font,
            fill="#000000",
        )

        self.y_cursor += box_h + 12

    def _draw_code(self, canvas, code, code_style: str | None, subject: str | None = None):
        if code_style is None:
            return

        # Normalize code first (fix \t and escaped \n)
        code = self._normalize_code(code)

        if code_style == "terminal": # linux - terminal commands -fixed
            self._draw_terminal_code(canvas, code)
        
        # TODO: implement other code styles later
        # elif code_style == "query_result": # sql - queries + result table 
        #     self._draw_editor_code(canvas, content.get("query", ""))
        #     self._draw_sql_result_table(canvas, content.get("result_table", ""))
        # elif code_style == "regex_highlight": # regex - patterns
        #     self._draw_regex_match(
        #         canvas,
        #         pattern=content.get("pattern", ""),
        #         input_text=content.get("input", ""),
        #         match=content.get("match", ""),
        #     )   # stub for now
        elif code_style == "editor":
            # Use IDE-style if enabled and subject provided
            if self.IDE_CODE_STYLE and subject:
                self._draw_editor_code_with_ide(canvas, code, subject)
            else:
                self._draw_editor_code(canvas, code)
        else:
            # default editor style - all programming languages + system design + docker_k8s
            if self.IDE_CODE_STYLE and subject:
                self._draw_editor_code_with_ide(canvas, code, subject)
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
        options_to_display = options if mode != RenderMode.ANSWER else [options[correct_idx]]
        start_idx = 0 if mode != RenderMode.ANSWER else correct_idx

        for display_idx, opt in enumerate(options_to_display):
            idx = start_idx + display_idx if mode == RenderMode.ANSWER else display_idx
            
            # Normalize escaped newlines
            opt = opt.replace("\\n", "\n")
            raw_lines = opt.split("\n")
            wrapped = []

            for line in raw_lines:
                wrapped.extend(
                    self.wrap_text(draw, line, font, max_width - 60)
                )

            block_height = len(wrapped) * line_height + padding * 2

            # Determine colors based on mode
            is_correct = (idx == correct_idx)
            
            if mode == RenderMode.QUESTION:
                # All options same styling
                bg = self.CARD_COLOR
                accent = self.ACCENT_COLOR
            elif mode == RenderMode.SINGLE:
                # Highlight correct answer in green
                bg = self.CORRECT_BG if is_correct else self.CARD_COLOR
                accent = self.SUCCESS_COLOR if is_correct else self.ACCENT_COLOR
            else:  # RenderMode.ANSWER
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
            print(f"Warning: Could not load logo: {e}")
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
    def wrap_text_with_prefix(draw, text, font, max_width, prefix_width):
        """
        Wrap text where the first line has reduced available width due to a prefix.
        Subsequent lines use the full max_width.
        """
        if not text:
            return [""]

        words = text.split(" ")
        lines = []
        current = ""

        # First line accounts for the prefix width
        line_limit = max_width - (prefix_width or 0)

        for word in words:
            test = current + (" " if current else "") + word
            if draw.textlength(test, font=font) <= line_limit:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
                # After the first break, use full width for subsequent lines
                line_limit = max_width

        if current:
            lines.append(current)

        return lines

    @staticmethod
    def _normalize_code(code: str) -> list[str]:
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
            scenario_lines = self.wrap_text_with_prefix(
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
            code_lines = self._normalize_code(question.code)
            wrapped_lines = []
            for line in code_lines:
                wrapped_lines.extend(self.wrap_code_line(self.draw, line, self.CODE_FONT, self.WIDTH - 120 - 40))
            code_height = len(wrapped_lines) * 48 + 40 + 40  # line_height + padding + gap

        # Question height
        question_lines = self.wrap_text_with_prefix(
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
                    wrapped.extend(self.wrap_text(self.draw, line, self.TEXT_FONT, self.WIDTH - 120 - 60))
                block_height = len(wrapped) * 50 + 36  # line_height + padding
                options_height += block_height + 14  # option_gap
        
        # Explanation height
        explanation_height = 0
        if layout_profile.has_explanation and mode in (RenderMode.ANSWER, RenderMode.SINGLE):
            explanation_lines = self.wrap_text(self.draw, question.explanation, self.TEXT_FONT, self.WIDTH - 120)
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
        print(f"image saved to: {out_path}")

    def render_day1_cta_image(self, subject: str) -> None:
        """
        Render a reusable Call-To-Action image (dark theme).
        Saved once and reused for all reels.
        """
        out_path = self.base_dir / subject / "images" / "cta" / "day1.png"
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
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=radius,
            fill=self.CARD_COLOR,
        )

        # --------------------------------------------------
        # Fonts 
        # --------------------------------------------------
        title_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Bold.ttf"), 72)
        body_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-SemiBold.ttf"), 50)
        follow_font = ImageFont.truetype(str(self.INTER_FONT_DIR / "Inter-Regular.ttf"), 44)

        # --------------------------------------------------
        # Text Content
        # --------------------------------------------------
        title_text = "What's Your Answer?"
        body_text = "Drop A, B, C, or D below!\n\nAnswer drops tomorrow"
        follow_text = f"Follow for daily {subject.replace('_', ' ').title()} challenges"

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
            self.SUBJECT_ACCENTS.get(subject, self.ACCENT_COLOR),
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
        out_path = self.base_dir / subject / "images" / "cta" / "day2.png"
        if out_path.exists():
            print(f"!!! {out_path} exists! remove that to recreate with new changes !!!")
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
        print(f"Day 2 CTA image saved → {out_path}")


    def render_welcome_image(self, subject: str) -> None:
        """
        Render a welcome image: 'Welcome to Daily Dose of Python'
        """
        out_path =  self.base_dir / subject / "images" / "welcome" / "welcome.png"
        if out_path.exists():
            print(f"!!! {out_path} exists! remove that to recreate with new changes !!!")
            return

        overlay_path = Path(f"pybender/assets/backgrounds/{subject}_img_new.png")
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
        print(f"Welcome image saved → {out_path}")

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
        if self.USE_STATIC_QUESTIONS:
            print("Using static questions from output/questions.json")
            with open("output/questions.json", "r") as f:
                questions_data = json.load(f)
                topic, content_type = "docker_k8s", "qa"
                # topic, content_type = "javascript", "code_output"
                questions = [Question(**q) for q in questions_data]
        else:
            qg = QuestionGenerator()
            questions, topic, content_type = qg.generate_questions(questions_per_run, subject=subject)  # get from LLM
        
        

        # Assign stable question IDs
        for idx, q in enumerate(questions, start=1):
            q.question_id = f"{RUN_ID}_q{idx:02d}"

        # --------------------------------------------------
        # Output directories (type-based)
        # --------------------------------------------------
        base_img_dir = self.base_dir / "test" / "images"
        question_dir = base_img_dir / "questions"
        answer_dir = base_img_dir / "answers"
        single_dir = base_img_dir / "singles"

        run_dir = self.base_dir / subject / "runs"

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

            layout_profile = resolve_layout_profile(content_type)
            
            question_img_out_path = question_dir / f"{q.question_id}_question.png"
            answer_img_out_path = answer_dir / f"{q.question_id}_answer.png"
            single_img_out_path = single_dir / f"{q.question_id}_single.png"

            # Render all three standard images (scenario included inline for QUESTION/SINGLE when applicable)
            self.render_image(q, question_img_out_path, layout_profile, subject, RenderMode.QUESTION)
            self.render_image(q, answer_img_out_path, layout_profile, subject, RenderMode.ANSWER)
            self.render_image(q, single_img_out_path, layout_profile, subject, RenderMode.SINGLE)

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
        metadata_path = run_dir / f"{RUN_ID}_metadata.json"
        if self.WRITE_METADATA:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            print(f"Metadata written to {metadata_path}")
        # TODO: create separate welcome pages per subject
        # self.render_day1_cta_image(subject)
        # self.render_day2_cta_image(subject)
        # self.render_welcome_image(subject)
        print("Image rendering process completed successfully")
        return metadata_path

if __name__ == "__main__":
    renderer = ImageRenderer()
    subjects = ["docker_k8s", "system_design"]
    # subjects = [
    #     "python", "sql", "regex", "system_design", 
    #     "linux"
    #     ,"docker_k8s", "javascript", "rust", "golang"
    # ]
    import time
    for subject in subjects:
        # renderer.render_welcome_image(subject)
        # renderer.render_day1_cta_image(subject)
        # renderer.render_day2_cta_image(subject)
        renderer.main(1, subject=subject)
        time.sleep(2)