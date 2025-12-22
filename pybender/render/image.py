from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from pybender.generator.schema import Question

# Canvas
WIDTH, HEIGHT = 1080, 1080
PADDING_X = 60
PADDING_Y = 50

# Colors
BG_COLOR = "#0F172A"      # dark slate
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

    # ---- Title ----
    draw.text(
        (PADDING_X, y),
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
        y += 50

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
