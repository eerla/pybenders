from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from pybender.generator.schema import Question

# Canvas
WIDTH, HEIGHT = 1080, 1080
PADDING_X = 60
PADDING_Y = 50

# Colors
# BG_COLOR = "#0F172A"      # dark slate
BG_COLOR = (9, 12, 24) 
TEXT_COLOR = "#E5E7EB"    # light gray
ACCENT_COLOR = "#38BDF8"  # cyan

# Fonts
FONT_DIR = Path("pybender/assets/fonts")

TITLE_FONT = ImageFont.truetype(
    str(FONT_DIR / "Inter-SemiBold.ttf"), 48
)
CODE_FONT = ImageFont.truetype(
    str(FONT_DIR / "JetBrainsMono-Regular.ttf"), 40
)
TEXT_FONT = ImageFont.truetype(
    str(FONT_DIR / "Inter-Regular.ttf"), 40
)


def render_question_image(q: Question, out_path: Path) -> None:
    """
    Render a single Question into a 1080x1080 Instagram-ready PNG.
    """

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    y = PADDING_Y

    # ---- Header ----
    header_text = "Daily Dose of Python"
    header_color = "#94A3B8"
    header_bbox = draw.textbbox((0, 0), header_text, font=TITLE_FONT)
    header_width = header_bbox[2] - header_bbox[0]
    header_x = (WIDTH - header_width) // 2
    draw.text(
        (header_x, y),
        header_text,
        font=TITLE_FONT,
        fill=header_color  # slate gray - subtle header color for dark theme
    )
    y += 60

    # ---- Title ----
    title_bbox = draw.textbbox((0, 0), q.title, font=TITLE_FONT)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2
    draw.text(
        (title_x, y),
        q.title,
        font=TITLE_FONT,
        fill=ACCENT_COLOR
    )
    y += 80

    # ---- Code Snippet ----
    MAX_TEXT_WIDTH = WIDTH - (2 * PADDING_X)

    for raw_line in q.code.split("\n"):
        wrapped = wrap_code_line(
            draw,
            raw_line,
            CODE_FONT,
            MAX_TEXT_WIDTH
        )

        for line in wrapped:
            draw.text(
                (PADDING_X, y),
                line,
                font=CODE_FONT,
                fill=TEXT_COLOR
            )
            y += 48



    y += 30

    # Separator line
    draw.line(
        [(PADDING_X, y), (WIDTH - PADDING_X, y)],
        fill=ACCENT_COLOR,
        width=2
    )
    y += 30

    # ---- Question Text ----
    for line in wrap_text(draw, q.question, TEXT_FONT, MAX_TEXT_WIDTH):
        draw.text((PADDING_X, y), line, font=TEXT_FONT, fill=TEXT_COLOR)
        y += 80


    # ---- Options ----
    for label, option in zip(["A", "B", "C", "D"], q.options):
        draw.text(
            (PADDING_X, y),
            f"{label}. {option}",
            font=TEXT_FONT,
            fill=TEXT_COLOR
        )
        y += 55

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)



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

