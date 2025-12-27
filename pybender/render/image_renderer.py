    # # def render_question_image(self, q: Question, out_path: Path, subject: str) -> None:
    # #     print("Rendering question image...")
    # #     img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
    # #     draw = ImageDraw.Draw(img)

    # #     # --------------------------------------------------
    # #     # Main Card
    # #     # --------------------------------------------------
    # #     card_x, card_y = 40, 80
    # #     card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120
    # #     radius = 28

    # #     draw.rounded_rectangle(
    # #         [card_x, card_y, card_x + card_w, card_y + card_h],
    # #         radius=radius,
    # #         fill=self.CARD_COLOR
    # #     )

    # #     y = card_y + 40
    # #     content_x = card_x + 40
    # #     max_width = card_w - 80

    # #     # --------------------------------------------------
    # #     # Calculate total content height first
    # #     # --------------------------------------------------
    # #     # Header
    # #     header_text = f"Daily Dose of {subject.capitalize()}"
    # #     header_height = 60

    # #     # Title
    # #     title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
    # #     title_height = 70

    # #     # Code block
    # #     code_lines = q.code.split("\n")
    # #     line_height = 44
    # #     block_padding = 20
    # #     all_wrapped_lines = []
    # #     for raw_line in code_lines:
    # #         wrapped = self.wrap_code_line(
    # #             draw,
    # #             raw_line,
    # #             self.CODE_FONT,
    # #             max_width - 40
    # #         )
    # #         all_wrapped_lines.extend(wrapped)
    # #     code_block_height = len(all_wrapped_lines) * line_height + block_padding * 2
    # #     code_section_height = code_block_height + 40

    # #     # Question text
    # #     question_lines = self.wrap_text(draw, q.question, self.TEXT_FONT, max_width)
    # #     question_height = len(question_lines) * 48 + 20

    # #     # Options
    # #     options_height = 4 * 46

    # #     # Total content height
    # #     total_content_height = header_height + title_height + code_section_height + question_height + options_height
    # #     card_content_height = card_h - 80  # Account for top and bottom padding

    # #     # Calculate starting y position to center vertically
    # #     y = card_y + (card_content_height - total_content_height) // 2

    # #     # --------------------------------------------------
    # #     # Header
    # #     # --------------------------------------------------
    # #     hw = draw.textbbox((0, 0), header_text, font=self.HEADER_FONT)[2]
    # #     draw.text(
    # #         (content_x + (max_width - hw) // 2, y),
    # #         header_text,
    # #         font=self.HEADER_FONT,
    # #         fill=self.SUBTLE_TEXT
    # #     )
    # #     y += header_height

    # #     # --------------------------------------------------
    # #     # Title
    # #     # --------------------------------------------------
    # #     title_x = content_x + (max_width - title_bbox[2]) // 2
    # #     draw.text((title_x, y), q.title, font=self.TITLE_FONT, fill=self.ACCENT_COLOR)
    # #     y += title_height

    # #     # --------------------------------------------------
    # #     # Code Block
    # #     # --------------------------------------------------
    # #     draw.rounded_rectangle(
    # #         [
    # #             content_x,
    # #             y,
    # #             content_x + max_width,
    # #             y + code_block_height
    # #         ],
    # #         radius=18,
    # #         fill=self.CODE_BG
    # #     )

    # #     draw.rectangle(
    # #         [content_x, y, content_x + 6, y + code_block_height],
    # #         fill=self.ACCENT_COLOR
    # #     )

    # #     cy = y + block_padding
    # #     for line in all_wrapped_lines:
    # #         draw.text(
    # #             (content_x + 20, cy),
    # #             line,
    # #             font=self.CODE_FONT,
    # #             fill=self.TEXT_COLOR
    # #         )
    # #         cy += line_height

    # #     y += code_section_height

    # #     # --------------------------------------------------
    # #     # Question Text
    # #     # --------------------------------------------------
    # #     for line in question_lines:
    # #         draw.text((content_x, y), line, font=self.TEXT_FONT, fill=self.TEXT_COLOR)
    # #         y += 48
    # #     y += 20

    # #     # --------------------------------------------------
    # #     # Options
    # #     # --------------------------------------------------
    # #     for label, option in zip(["A", "B", "C", "D"], q.options):
    # #         option_text = f"{label}. {option}"
    # #         draw.text(
    # #             (content_x, y),
    # #             option_text,
    # #             font=self.TEXT_FONT,
    # #             fill=self.TEXT_COLOR
    # #         )
    # #         y += 56

    # #     # --------------------------------------------------
    # #     # Save
    # #     # --------------------------------------------------
    # #     out_path.parent.mkdir(parents=True, exist_ok=True)
    # #     img.save(out_path)
    # #     print(f"question image saved to: {out_path}")


    # # def render_answer_image(self, q: Question, out_path: Path, subject: str) -> None:
    # #     """
    # #     Render answer-reveal image highlighting the correct option.
    # #     """
    # #     print("Rendering answer image...")
    # #     img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
    # #     draw = ImageDraw.Draw(img)

    # #     # --------------------------------------------------
    # #     # Main Card
    # #     # --------------------------------------------------
    # #     card_x, card_y = 40, 80
    # #     card_w, card_h = self.WIDTH - 80, self.HEIGHT - 120
    # #     radius = 28

    # #     draw.rounded_rectangle(
    # #         [card_x, card_y, card_x + card_w, card_y + card_h],
    # #         radius=radius,
    # #         fill=self.CARD_COLOR
    # #     )

    # #     content_x = card_x + 40
    # #     max_width = card_w - 80

    # #     # --------------------------------------------------
    # #     # Calculate total content height first
    # #     # --------------------------------------------------
    # #     # Answer label
    # #     answer_label_height = 70
        
    # #     # Title
    # #     title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
    # #     title_height = 80

    # #     # Code block
    # #     code_lines = q.code.split("\n")
    # #     line_height = 44
    # #     block_padding = 20
    # #     all_wrapped_lines = []
    # #     for raw_line in code_lines:
    # #         wrapped = self.wrap_code_line(
    # #             draw,
    # #             raw_line,
    # #             self.CODE_FONT,
    # #             max_width - 40
    # #         )
    # #         all_wrapped_lines.extend(wrapped)
    # #     code_block_height = len(all_wrapped_lines) * line_height + block_padding * 2
    # #     code_section_height = code_block_height + 40

    # #     # Answer option
    # #     option_h = 60
    # #     answer_section_height = option_h + 32

    # #     # Explanation
    # #     explanation_height = 0
    # #     if q.explanation:
    # #         explanation_lines = self.wrap_text(draw, q.explanation, self.TEXT_FONT, max_width)
    # #         explanation_height = 28 + 60 + (len(explanation_lines) * 50)  # divider + label + content

    # #     # Total content height
    # #     total_content_height = answer_label_height + title_height + code_section_height + answer_section_height + explanation_height
    # #     card_content_height = card_h - 80  # Account for top and bottom padding

    # #     # Calculate starting y position to center vertically
    # #     y = card_y + (card_content_height - total_content_height) // 2

    # #     # --------------------------------------------------
    # #     # Answer Label
    # #     # --------------------------------------------------
    # #     answer_text = f"{subject.capitalize()} Answer"
    # #     aw = draw.textbbox((0, 0), answer_text, font=self.HEADER_FONT)[2]
    # #     draw.text(
    # #         (content_x + (max_width - aw) // 2, y),
    # #         answer_text,
    # #         font=self.HEADER_FONT,
    # #         fill=self.SUBTLE_TEXT
    # #     )
    # #     y += answer_label_height

    # #     # --------------------------------------------------
    # #     # Title
    # #     # --------------------------------------------------
    # #     title_x = content_x + (max_width - title_bbox[2]) // 2
    # #     draw.text((title_x, y), q.title, font=self.TITLE_FONT, fill=self.ACCENT_COLOR)
    # #     y += title_height

    # #     # --------------------------------------------------
    # #     # Code Block
    # #     # --------------------------------------------------
    # #     draw.rounded_rectangle(
    # #         [
    # #             content_x,
    # #             y,
    # #             content_x + max_width,
    # #             y + code_block_height
    # #         ],
    # #         radius=18,
    # #         fill=self.CODE_BG
    # #     )

    # #     draw.rectangle(
    # #         [content_x, y, content_x + 6, y + code_block_height],
    # #         fill=self.ACCENT_COLOR
    # #     )

    # #     cy = y + block_padding
    # #     for line in all_wrapped_lines:
    # #         draw.text(
    # #             (content_x + 20, cy),
    # #             line,
    # #             font=self.CODE_FONT,
    # #             fill=self.TEXT_COLOR
    # #         )
    # #         cy += line_height

    # #     y += code_section_height

    # #     # --------------------------------------------------
    # #     # Answer Option (highlight correct)
    # #     # --------------------------------------------------
    # #     correct_label = q.correct.upper()
    # #     option = q.options[ord(correct_label) - ord("A")]
        
    # #     # Highlight background
    # #     draw.rounded_rectangle(
    # #         [content_x, y - 6, content_x + max_width, y + option_h],
    # #         radius=14,
    # #         fill=self.CORRECT_BG
    # #     )
    # #     draw.rectangle(
    # #         [content_x, y - 6, content_x + 6, y + option_h],
    # #         fill=self.SUCCESS_COLOR
    # #     )

    # #     draw.text(
    # #         (content_x + 18, y),
    # #         f"{correct_label}. {option}",
    # #         font=self.TEXT_FONT,
    # #         fill=self.SUCCESS_COLOR
    # #     )

    # #     y += answer_section_height

    # #     # --------------------------------------------------
    # #     # Explanation (optional but powerful)
    # #     # --------------------------------------------------
    # #     if q.explanation:
    # #         draw.line(
    # #             [(content_x, y), (content_x + max_width, y)],
    # #             fill=self.ACCENT_COLOR,
    # #             width=2
    # #         )
    # #         y += 18

    # #         explanation_label = "Explanation: "
    # #         explanation_content = q.explanation
            
    # #         # Draw "Explanation:" in accent color
    # #         draw.text(
    # #             (content_x, y),
    # #             explanation_label,
    # #             font=self.TEXT_FONT,
    # #             fill=self.ACCENT_COLOR
    # #         )
    # #         y += 60
            
    # #         # Draw the explanation text
    # #         for line in self.wrap_text(draw, explanation_content, self.TEXT_FONT, max_width):
    # #             draw.text(
    # #                 (content_x, y),
    # #                 line,
    # #                 font=self.TEXT_FONT,
    # #                 fill=self.SUBTLE_TEXT
    # #             )
    # #             y += 50

    # #     # --------------------------------------------------
    # #     # Save
    # #     # --------------------------------------------------
    # #     out_path.parent.mkdir(parents=True, exist_ok=True)
    # #     img.save(out_path)
    # #     print(f"answer image saved to: {out_path}")


    # def render_single_post_image(self, q: Question, out_path: Path, subject: str) -> None:
    #     """
    #     Render a single-post image with question + answer together.
    #     Output: pybenders/output/images/singles/<slug>.png
    #     """
    #     print("Rendering single post image...")

    #     img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BG_COLOR)
    #     draw = ImageDraw.Draw(img)

    #     # --------------------------------------------------
    #     # Main Card
    #     # --------------------------------------------------
    #     card_x, card_y = 40, 70
    #     card_w, card_h = self.WIDTH - 80, self.HEIGHT - 110

    #     draw.rounded_rectangle(
    #         [card_x, card_y, card_x + card_w, card_y + card_h],
    #         radius=28,
    #         fill=self.CARD_COLOR
    #     )

    #     content_x = card_x + 40
    #     max_width = card_w - 80
    #     y = card_y + 30

    #     # --------------------------------------------------
    #     # Header (Brand) - moved inside card
    #     # --------------------------------------------------
    #     header = f"Daily Dose of {subject.capitalize()}"
    #     hw = draw.textbbox((0, 0), header, font=self.HEADER_FONT)[2]
    #     draw.text(
    #         (content_x + (max_width - hw) // 2, y),
    #         header,
    #         font=self.HEADER_FONT,
    #         fill=self.SUBTLE_TEXT
    #     )
    #     y += 50

    #     # --------------------------------------------------
    #     # Title
    #     # --------------------------------------------------
    #     title_bbox = draw.textbbox((0, 0), q.title, font=self.TITLE_FONT)
    #     draw.text(
    #         (content_x + (max_width - title_bbox[2]) // 2, y),
    #         q.title,
    #         font=self.TITLE_FONT,
    #         fill=self.ACCENT_COLOR
    #     )
    #     y += 80

    #     # --------------------------------------------------
    #     # Code Block
    #     # --------------------------------------------------
    #     code_lines = q.code.split("\n")
    #     line_height = 42
    #     block_padding = 20

    #     wrapped_lines = []
    #     for raw in code_lines:
    #         wrapped_lines.extend(
    #             self.wrap_code_line(draw, raw, self.CODE_FONT, max_width - 40)
    #         )

    #     block_height = len(wrapped_lines) * line_height + block_padding * 2

    #     draw.rounded_rectangle(
    #         [content_x, y, content_x + max_width, y + block_height],
    #         radius=18,
    #         fill=self.CODE_BG
    #     )

    #     draw.rectangle(
    #         [content_x, y, content_x + 6, y + block_height],
    #         fill=self.ACCENT_COLOR
    #     )

    #     cy = y + block_padding
    #     for line in wrapped_lines:
    #         draw.text(
    #             (content_x + 20, cy),
    #             line,
    #             font=self.CODE_FONT,
    #             fill=self.TEXT_COLOR
    #         )
    #         cy += line_height

    #     y = cy + 30

    #     # --------------------------------------------------
    #     # Question Text
    #     # --------------------------------------------------
    #     question_lines = self.wrap_text(draw, q.question, self.TEXT_FONT, max_width)
    #     for line in question_lines:
    #         draw.text((content_x, y), line, font=self.TEXT_FONT, fill=self.TEXT_COLOR)
    #         y += 48
    #     y += 20

    #     # --------------------------------------------------
    #     # All Options
    #     # --------------------------------------------------
    #     for label, option in zip(["A", "B", "C", "D"], q.options):
    #         option_text = f"{label}. {option}"
    #         draw.text(
    #             (content_x, y),
    #             option_text,
    #             font=self.TEXT_FONT,
    #             fill=self.TEXT_COLOR
    #         )
    #         y += 56

    #     y += 20
    #     # --------------------------------------------------
    #     # Correct Answer Highlight
    #     # --------------------------------------------------
    #     correct_label = q.correct.upper()
    #     correct_option = q.options[ord(correct_label) - ord("A")]

    #     answer_height = 80
    #     draw.rounded_rectangle(
    #         [content_x, y, content_x + max_width, y + answer_height],
    #         radius=18,
    #         fill=self.CORRECT_BG
    #     )
    #     draw.rectangle(
    #         [content_x, y, content_x + 6, y + answer_height],
    #         fill=self.SUCCESS_COLOR
    #     )

    #     draw.text(
    #         (content_x + 20, y + 18),
    #         f"{correct_label}. {correct_option}",
    #         font=self.TEXT_FONT,
    #         fill=self.SUCCESS_COLOR
    #     )

    #     y += answer_height + 24

    #     # --------------------------------------------------
    #     # Explanation (optional but powerful) 
    #     # --------------------------------------------------
    #     if q.explanation:
    #         y += 10
    #         draw.line(
    #             [(content_x, y), (content_x + max_width, y)],
    #             fill=self.ACCENT_COLOR,
    #             width=2
    #         )
    #         y += 18

    #         explanation_label = "Explanation: "
    #         explanation_content = q.explanation
            
    #         # Draw "Explanation:" in accent color
    #         label_width = draw.textbbox((0, 0), explanation_label, font=self.TEXT_FONT)[2]
    #         draw.text(
    #             (content_x, y),
    #             explanation_label,
    #             font=self.TEXT_FONT,
    #             fill=self.ACCENT_COLOR
    #         )
    #         y += 60
            
    #         # Draw the explanation text starting from the next line
    #         for line in self.wrap_text(draw, explanation_content, self.TEXT_FONT, max_width):
    #             draw.text(
    #             (content_x, y),
    #             line,
    #             font=self.TEXT_FONT,
    #             fill=self.SUBTLE_TEXT
    #             )
    #             y += 50

    #     # --------------------------------------------------
    #     # Save
    #     # --------------------------------------------------
    #     img.save(out_path)
    #     print(f"Single post image saved → {out_path}")
