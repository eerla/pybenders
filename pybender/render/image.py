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
CORRECT_BG = (20, 45, 70)
SUCCESS_COLOR = (72, 187, 120)
# Fonts
FONT_DIR = Path("pybender/assets/fonts")

TITLE_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-SemiBold.ttf"), 48)
TEXT_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 38)
CODE_FONT = ImageFont.truetype(str(FONT_DIR / "JetBrainsMono-Regular.ttf"), 36)
HEADER_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 28)



def render_day1_cta_image() -> None:
    """
    Render a reusable Call-To-Action image (dark theme).
    Saved once and reused for all reels.
    """
    out_path = Path("output/images/cta/day1.png")
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
    # Explanation (optional but powerful) -- adding new slide specific to explanation
    # --------------------------------------------------
    # if q.explanation:
    #     y += 10
    #     draw.line(
    #         [(content_x, y), (content_x + max_width, y)],
    #         fill=ACCENT_COLOR,
    #         width=2
    #     )
    #     y += 18

    #     for line in wrap_text(draw, q.explanation, TEXT_FONT, max_width):
    #         draw.text(
    #             (content_x, y),
    #             line,
    #             font=TEXT_FONT,
    #             fill=SUBTLE_TEXT
    #         )
    #         y += 44

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def render_single_post_image(q: Question) -> None:
    """
    Render a single-post image with question + answer together.
    Output: pybenders/output/images/singles/<slug>.png
    """
    MAX_EXPLANATION_HEIGHT = 160
    EXPL_LINE_HEIGHT = 40
    out_path = Path("output/images/singles") / f"{q.title.lower().replace(' ', '_')}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------
    # Header (Brand)
    # --------------------------------------------------
    header = "Daily Python Internals"
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
    line_height = 42
    block_padding = 20

    wrapped_lines = []
    for raw in code_lines:
        wrapped_lines.extend(
            wrap_code_line(draw, raw, CODE_FONT, max_width - 40)
        )

    block_height = len(wrapped_lines) * line_height + block_padding * 2

    draw.rounded_rectangle(
        [content_x, y, content_x + max_width, y + block_height],
        radius=18,
        fill=CODE_BG
    )

    draw.rectangle(
        [content_x, y, content_x + 6, y + block_height],
        fill=ACCENT_COLOR
    )

    cy = y + block_padding
    for line in wrapped_lines:
        draw.text(
            (content_x + 20, cy),
            line,
            font=CODE_FONT,
            fill=TEXT_COLOR
        )
        cy += line_height

    y = cy + 30

    # --------------------------------------------------
    # Correct Answer Highlight
    # --------------------------------------------------
    correct_label = q.correct.upper()
    correct_option = q.options[ord(correct_label) - ord("A")]

    answer_height = 70
    draw.rounded_rectangle(
        [content_x, y, content_x + max_width, y + answer_height],
        radius=18,
        fill=CORRECT_BG
    )
    draw.rectangle(
        [content_x, y, content_x + 6, y + answer_height],
        fill=SUCCESS_COLOR
    )

    draw.text(
        (content_x + 20, y + 18),
        f"Correct Answer: {correct_option}",
        font=TEXT_FONT,
        fill=SUCCESS_COLOR
    )

    y += answer_height + 24

    # --------------------------------------------------
    # Explanation (Capped)
    # --------------------------------------------------
    if q.explanation:
        draw.line(
            [(content_x, y), (content_x + max_width, y)],
            fill=ACCENT_COLOR,
            width=2
        )
        y += 16

        wrapped = wrap_text(draw, q.explanation, TEXT_FONT, max_width)

        max_lines = MAX_EXPLANATION_HEIGHT // EXPL_LINE_HEIGHT
        if len(wrapped) > max_lines:
            wrapped = wrapped[: max_lines - 1] + ["… Full explanation in caption"]

        for line in wrapped:
            draw.text(
                (content_x, y),
                line,
                font=TEXT_FONT,
                fill=SUBTLE_TEXT
            )
            y += EXPL_LINE_HEIGHT

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    img.save(out_path)
    print(f"Single post image saved → {out_path}")


def render_day2_cta_image() -> None:
    """
    Render a reusable Call-To-Action image (dark theme).
    Saved once and reused for all reels.
    """
    out_path = Path("output/images/cta/day2.png")
    if out_path.exists():
        print(f"!!! {out_path} exists! remove that to recreate with new changes !!!")
        return

    TITLE_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-SemiBold.ttf"), 84)
    TEXT_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 48)
    SUBTLE_FONT = ImageFont.truetype(str(FONT_DIR / "Inter-Regular.ttf"), 42)

    img = Image.new("RGB", (VIDEO_W, VIDEO_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------
    # CTA Card
    # --------------------------------------------------
    card_w, card_h = 920, 640
    card_x = (VIDEO_W - card_w) // 2
    card_y = (VIDEO_H - card_h) // 2

    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=32,
        fill=CARD_COLOR
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
        fill=ACCENT_COLOR
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
            fill=TEXT_COLOR
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
        fill=SUBTLE_TEXT
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Day 2 CTA image saved → {out_path}")


def render_explanation_image(q: Question, out_path: Path) -> None:
    """
    Render a dark-themed explanation image for reels/posts.
    """

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------
    # Header
    # --------------------------------------------------
    header = "Explanation"
    hw = draw.textbbox((0, 0), header, font=HEADER_FONT)[2]
    draw.text(
        ((WIDTH - hw) // 2, 20),
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
    # Title (Question Title)
    # --------------------------------------------------
    title_bbox = draw.textbbox((0, 0), q.title, font=TITLE_FONT)
    draw.text(
        (content_x + (max_width - title_bbox[2]) // 2, y),
        q.title,
        font=TITLE_FONT,
        fill=ACCENT_COLOR
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
                wrap_code_line(
                    draw,
                    raw_line,
                    CODE_FONT,
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
            fill=CODE_BG
        )

        draw.rectangle(
            [content_x, y, content_x + 6, y + block_height],
            fill=ACCENT_COLOR
        )

        cy = y + padding
        for line in wrapped_lines:
            draw.text(
                (content_x + 20, cy),
                line,
                font=CODE_FONT,
                fill=TEXT_COLOR
            )
            cy += line_height

        y = cy + padding + 20

    # --------------------------------------------------
    # Explanation Text
    # --------------------------------------------------
    if q.explanation:
        for line in wrap_text(draw, q.explanation, TEXT_FONT, max_width):
            draw.text(
                (content_x, y),
                line,
                font=TEXT_FONT,
                fill=TEXT_COLOR
            )
            y += 46

    # --------------------------------------------------
    # Footer (subtle CTA)
    # --------------------------------------------------
    footer = "Follow for daily Python challenges"
    fw = draw.textbbox((0, 0), footer, font=HEADER_FONT)[2]
    draw.text(
        (content_x + (max_width - fw) // 2, HEIGHT - 70),
        footer,
        font=HEADER_FONT,
        fill=SUBTLE_TEXT
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
