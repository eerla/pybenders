from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from pybender.generator.schema import Question

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


# create new function to create a eye catching beautifully animated CTA image 
VIDEO_W, VIDEO_H = 1080, 1920


def render_cta_image() -> None:
    """
    Render a reusable Call-To-Action image (dark theme).
    Saved once and reused for all reels.
    """
    out_path = Path("pybender/assets/backgrounds/cta.png")
    if out_path.exists():
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # Colors (Dark Theme)
    # --------------------------------------------------
    BG_COLOR = (9, 12, 24)          # page background
    CARD_COLOR = (11, 18, 32)       # CTA card
    ACCENT = (76, 201, 240)         # blue accent
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (160, 174, 192)

    # --------------------------------------------------
    # Canvas
    # --------------------------------------------------
    img = Image.new("RGB", (VIDEO_W, VIDEO_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------
    # Card Geometry
    # --------------------------------------------------
    card_w, card_h = 920, 720
    card_x = (VIDEO_W - card_w) // 2
    card_y = (VIDEO_H - card_h) // 2
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
        fill=CARD_COLOR,
    )

    # --------------------------------------------------
    # Fonts (adjust paths as needed)
    # --------------------------------------------------
    FONT_DIR = Path("pybender/assets/fonts")

    title_font = ImageFont.truetype(
        str(FONT_DIR / "Inter-Bold.ttf"), 72
    )
    body_font = ImageFont.truetype(
        str(FONT_DIR / "Inter-SemiBold.ttf"), 50
    )
    follow_font = ImageFont.truetype(
        str(FONT_DIR / "Inter-Regular.ttf"), 44
    )

    # --------------------------------------------------
    # Text Content
    # --------------------------------------------------
    title_text = "What's Your Answer?"
    body_text = "Drop A, B, C, or D below!\n\nAnswer drops tomorrow"
    follow_text = "Follow for daily Python challenges"

    # --------------------------------------------------
    # Text Positions
    # --------------------------------------------------
    center_x = VIDEO_W // 2

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
        ACCENT,
    )

    draw_centered_text(
        body_text,
        body_font,
        card_y + 260,
        TEXT_PRIMARY,
    )

    draw_centered_text(
        follow_text,
        follow_font,
        card_y + 520,
        TEXT_SECONDARY,
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    img.save(out_path, format="PNG")
    print(f"CTA image rendered at: {out_path}")


# Canvas
WIDTH, HEIGHT = 1080, 1080
PADDING_X = 60
PADDING_Y = 50

# Colors (match CTA theme)
BG_COLOR = (9, 12, 24)
CARD_COLOR = (11, 18, 32)
CODE_BG = (15, 23, 42)
TEXT_COLOR = (226, 232, 240)
SUBTLE_TEXT = (148, 163, 184)
ACCENT_COLOR = (76, 201, 240)

# Fonts
FONT_DIR = Path("pybender/assets/fonts")

TITLE_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-SemiBold.ttf"), 48)
TEXT_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 38)
CODE_FONT = ImageFont.truetype(str(FONT_DIR / "JetBrainsMono-Regular.ttf"), 36)
HEADER_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 28)


def render_question_image(q: Question, out_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------
    # Header (branding)
    # --------------------------------------------------
    header_text = "Daily Dose of Python"
    hw = draw.textbbox((0, 0), header_text, font=HEADER_FONT)[2]
    draw.text(
        ((WIDTH - hw) // 2, 20),
        header_text,
        font=HEADER_FONT,
        fill=SUBTLE_TEXT
    )

    # --------------------------------------------------
    # Main Card
    # --------------------------------------------------
    card_x, card_y = 40, 80
    card_w, card_h = WIDTH - 80, HEIGHT - 120
    radius = 28

    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        fill=CARD_COLOR
    )

    y = card_y + 40
    content_x = card_x + 40
    max_width = card_w - 80

    # --------------------------------------------------
    # Title
    # --------------------------------------------------
    title_bbox = draw.textbbox((0, 0), q.title, font=TITLE_FONT)
    title_x = content_x + (max_width - title_bbox[2]) // 2
    draw.text((title_x, y), q.title, font=TITLE_FONT, fill=ACCENT_COLOR)
    y += 70

    # --------------------------------------------------
    # Code Block
    # --------------------------------------------------
    code_lines = q.code.split("\n")
    line_height = 44
    block_padding = 20
    block_height = len(code_lines) * line_height + block_padding * 2

    # First, calculate wrapped lines to determine actual block height
    all_wrapped_lines = []
    for raw_line in code_lines:
        wrapped = wrap_code_line(
            draw,
            raw_line,
            CODE_FONT,
            max_width - 40  # Account for padding inside code block
        )
        all_wrapped_lines.extend(wrapped)
    
    # Recalculate block height based on actual wrapped line count
    block_height = len(all_wrapped_lines) * line_height + block_padding * 2

    # Code container
    draw.rounded_rectangle(
        [
            content_x,
            y,
            content_x + max_width,
            y + block_height
        ],
        radius=18,
        fill=CODE_BG
    )

    # Accent bar
    draw.rectangle(
        [content_x, y, content_x + 6, y + block_height],
        fill=ACCENT_COLOR
    )

    cy = y + block_padding
    for line in all_wrapped_lines:
        draw.text(
            (content_x + 20, cy),
            line,
            font=CODE_FONT,
            fill=TEXT_COLOR
        )
        cy += line_height

    y = cy + block_padding

    y += 20

    # --------------------------------------------------
    # Question Text
    # --------------------------------------------------
    for line in wrap_text(draw, q.question, TEXT_FONT, max_width):
        draw.text((content_x, y), line, font=TEXT_FONT, fill=TEXT_COLOR)
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
            font=TEXT_FONT,
            fill=TEXT_COLOR
        )
        y += 46

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)



CORRECT_BG = (20, 45, 70)
SUCCESS_COLOR = (72, 187, 120)
BADGE_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-SemiBold.ttf"), 28)


def render_answer_image(q: Question, out_path: Path) -> None:
    """
    Render answer-reveal image highlighting the correct option.
    """

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------
    # Header
    # --------------------------------------------------
    header = "Answer Revealed"
    hw = draw.textbbox((0, 0), header, font=HEADER_FONT)[2]
    draw.text(
        ((WIDTH - hw) // 2, 18),
        header,
        font=HEADER_FONT,
        fill=SUBTLE_TEXT
    )

    # --------------------------------------------------
    # Main Card
    # --------------------------------------------------
    card_x, card_y = 40, 70
    card_w, card_h = WIDTH - 80, HEIGHT - 110

    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=28,
        fill=CARD_COLOR
    )

    content_x = card_x + 40
    max_width = card_w - 80
    y = card_y + 30

    # --------------------------------------------------
    # Title
    # --------------------------------------------------
    title_bbox = draw.textbbox((0, 0), q.title, font=TITLE_FONT)
    draw.text(
        (content_x + (max_width - title_bbox[2]) // 2, y),
        q.title,
        font=TITLE_FONT,
        fill=ACCENT_COLOR
    )
    y += 60

    # --------------------------------------------------
    # Code Block
    # --------------------------------------------------
    code_lines = q.code.split("\n")
    line_height = 44
    block_padding = 20
    block_height = len(code_lines) * line_height + block_padding * 2

    # First, calculate wrapped lines to determine actual block height
    all_wrapped_lines = []
    for raw_line in code_lines:
        wrapped = wrap_code_line(
            draw,
            raw_line,
            CODE_FONT,
            max_width - 40  # Account for padding inside code block
        )
        all_wrapped_lines.extend(wrapped)
    
    # Recalculate block height based on actual wrapped line count
    block_height = len(all_wrapped_lines) * line_height + block_padding * 2

    # Code container
    draw.rounded_rectangle(
        [
            content_x,
            y,
            content_x + max_width,
            y + block_height
        ],
        radius=18,
        fill=CODE_BG
    )

    # Accent bar
    draw.rectangle(
        [content_x, y, content_x + 6, y + block_height],
        fill=ACCENT_COLOR
    )

    cy = y + block_padding
    for line in all_wrapped_lines:
        draw.text(
            (content_x + 20, cy),
            line,
            font=CODE_FONT,
            fill=TEXT_COLOR
        )
        cy += line_height

    y = cy + block_padding

    y += 20

    # --------------------------------------------------
    # Options (highlight correct)
    # --------------------------------------------------
    correct_label = q.correct.upper()
    option_h = 52

    for label, option in zip(["A", "B", "C", "D"], q.options):
        is_correct = label == correct_label

        if is_correct:
            # Highlight background
            draw.rounded_rectangle(
                [content_x, y - 6, content_x + max_width, y + option_h],
                radius=14,
                fill=CORRECT_BG
            )
            draw.rectangle(
                [content_x, y - 6, content_x + 6, y + option_h],
                fill=SUCCESS_COLOR
            )

        text_color = SUCCESS_COLOR if is_correct else TEXT_COLOR
        prefix = f"{label}. " if is_correct else f"{label}. "

        draw.text(
            (content_x + 18, y),
            f"{prefix}{option}",
            font=TEXT_FONT,
            fill=text_color
        )

        y += option_h + 12

    # --------------------------------------------------
    # Explanation (optional but powerful)
    # --------------------------------------------------
    if q.explanation:
        y += 10
        draw.line(
            [(content_x, y), (content_x + max_width, y)],
            fill=ACCENT_COLOR,
            width=2
        )
        y += 18

        for line in wrap_text(draw, q.explanation, TEXT_FONT, max_width):
            draw.text(
                (content_x, y),
                line,
                font=TEXT_FONT,
                fill=SUBTLE_TEXT
            )
            y += 44

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
