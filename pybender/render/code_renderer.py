"""
Shared code rendering utilities for consistent IDE-style code display.
"""
from PIL import ImageDraw, ImageFont
from pybender.render.text_utils import wrap_code_line


def draw_editor_code_with_ide(
    draw: ImageDraw.ImageDraw,
    code: list,
    subject: str,
    y_cursor: int,
    width: int,
    padding_x: int,
    code_font: ImageFont.FreeTypeFont,
    small_label_font: ImageFont.FreeTypeFont,
    code_bg: tuple,
    ide_header_bg: tuple,
    ide_gutter_bg: tuple,
    text_color: tuple,
    subtle_text: tuple,
    ide_line_number_color: tuple,
    language_map: dict,
    ide_gutter_width: int,
    ide_header_height: int,
    line_height: int = 48
) -> int:
    """
    Draw code with IDE-style header bar and line numbers.
    
    Args:
        draw: PIL ImageDraw object
        code: List of normalized code lines
        subject: Programming language/subject
        y_cursor: Starting Y position
        width: Canvas width
        padding_x: Horizontal padding
        code_font: Font for code text
        small_label_font: Font for line numbers and badge
        code_bg: Background color for code block
        ide_header_bg: Background color for IDE header
        ide_gutter_bg: Background color for line number gutter
        text_color: Color for code text
        subtle_text: Color for subtle elements
        ide_line_number_color: Color for line numbers
        language_map: Mapping of subject to language display name
        ide_gutter_width: Width of line number gutter
        ide_header_height: Height of IDE header
        line_height: Height of each code line (default 48)
        
    Returns:
        Updated y_cursor position after drawing
    """
    max_width = width - (padding_x * 2) - 40 - ide_gutter_width

    # Wrap code lines and track which source line each wrapped line belongs to
    wrapped_with_line_map = []  # List of (wrapped_line, source_line_num, is_first_of_source)
    for src_line_idx, src_line in enumerate(code, start=1):
        wrapped = wrap_code_line(draw, src_line, code_font, max_width)
        for wrap_idx, wline in enumerate(wrapped):
            is_first = (wrap_idx == 0)  # Only the first wrapped line gets the line number
            wrapped_with_line_map.append((wline, src_line_idx, is_first))

    wrapped_lines = [item[0] for item in wrapped_with_line_map]
    code_block_height = len(wrapped_lines) * line_height + 30

    # Draw unified IDE window (header + code as one block)
    total_height = ide_header_height + code_block_height
    draw.rounded_rectangle(
        [
            padding_x,
            y_cursor,
            width - padding_x,
            y_cursor + total_height,
        ],
        radius=18,
        fill=code_bg,
    )

    # Draw header section on top
    draw.rectangle(
        [
            padding_x,
            y_cursor,
            width - padding_x,
            y_cursor + ide_header_height,
        ],
        fill=ide_header_bg,
    )

    # Re-apply rounded corners to header top
    draw.rounded_rectangle(
        [
            padding_x,
            y_cursor,
            width - padding_x,
            y_cursor + ide_header_height,
        ],
        radius=18,
        fill=ide_header_bg,
        corners=(True, True, False, False)  # Only round top corners
    )

    # Draw window control dots in header (macOS/VS Code style)
    dot_y = y_cursor + ide_header_height // 2
    dot_radius = 5
    dot_spacing = 16
    start_x = padding_x + 12
    
    # Close (red)
    draw.ellipse(
        [start_x, dot_y - dot_radius, start_x + dot_radius * 2, dot_y + dot_radius],
        fill=(255, 95, 86)
    )
    # Minimize (yellow)
    draw.ellipse(
        [start_x + dot_spacing, dot_y - dot_radius, start_x + dot_spacing + dot_radius * 2, dot_y + dot_radius],
        fill=(255, 189, 46)
    )
    # Maximize (green)
    draw.ellipse(
        [start_x + dot_spacing * 2, dot_y - dot_radius, start_x + dot_spacing * 2 + dot_radius * 2, dot_y + dot_radius],
        fill=(40, 201, 64)
    )

    # Draw language badge in header (vertically centered)
    language = language_map.get(subject, subject.title())
    badge_text = f"  daily dose of programming  "
    
    # Get text bounding box for vertical centering
    bbox = draw.textbbox((0, 0), badge_text, font=small_label_font)
    text_height = bbox[3] - bbox[1]
    text_width = draw.textlength(badge_text, font=small_label_font)
    
    # Calculate dots area width (3 dots + spacing on left side)
    dots_area_width = 12 + (dot_radius * 2) + dot_spacing + (dot_radius * 2) + dot_spacing + (dot_radius * 2) + 12
    
    # Center text horizontally, then shift LEFT by half the dots width to compensate
    badge_x = (width - text_width) // 2 - (dots_area_width // 2)
    
    # Center text vertically in header
    badge_y = y_cursor + (ide_header_height - text_height) // 2
    
    draw.text(
        (badge_x, badge_y),
        badge_text,
        font=code_font,
        fill=subtle_text,
    )

    # Move cursor to code section
    code_y_start = y_cursor + ide_header_height

    # Draw gutter background
    draw.rectangle(
        [
            padding_x,
            code_y_start,
            padding_x + ide_gutter_width,
            code_y_start + code_block_height,
        ],
        fill=ide_gutter_bg,
    )

    # Draw gutter separator line
    draw.line(
        [
            padding_x + ide_gutter_width,
            code_y_start,
            padding_x + ide_gutter_width,
            code_y_start + code_block_height,
        ],
        fill=(25, 32, 47),
        width=5
    )

    # Draw line numbers and code
    text_x = padding_x + ide_gutter_width + 12
    text_y = code_y_start + 15

    for wline, src_line_num, is_first in wrapped_with_line_map:
        # Draw line number only for first wrapped line of each source line
        if is_first:
            draw.text(
                (padding_x + 8, text_y),
                str(src_line_num),
                font=small_label_font,
                fill=ide_line_number_color,
            )

        # Draw code
        draw.text(
            (text_x, text_y),
            wline,
            font=code_font,
            fill=text_color,
        )
        
        text_y += line_height

    return y_cursor + total_height + 20