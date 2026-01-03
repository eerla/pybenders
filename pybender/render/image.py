import json
import logging
from datetime import datetime
from pathlib import Path

from pybender.config.logging_config import setup_logging
from pybender.generator.question_gen import QuestionGenerator
from pybender.generator.schema import Question, MindBenderQuestion, PsychologyCard
from pybender.render.layout_resolver import resolve_layout_profile
from pybender.render.render_mode import RenderMode
from pybender.render.text_utils import slugify

logger = logging.getLogger(__name__)


def _ensure_logging_configured() -> None:
    if not logging.getLogger().handlers:
        setup_logging()

class ImageRenderer:
    """
    Wrapper class for image rendering functions.
    """
    def __init__(self):
        _ensure_logging_configured()
        self.MODEL = "gpt-4o-mini"
        # Output and assets
        self.BASE_DIR = Path("output_1")
        # self.BASE_DIR = Path(r"G:\My Drive\output")  # Change to google drive path
        self.WRITE_METADATA = True  # Set to True to write metadata.json
        self.USE_STATIC_QUESTIONS = False  # Set to True to use static questions from output/questions.json
        self.GENERATE_NEW_QIDS = True  # Set to True to assign new question IDs

    # ---------- SHARED HELPERS ----------
    def _new_run_context(self) -> tuple[str, str, str]:
        run_date = datetime.now().strftime("%Y-%m-%d")
        run_timestamp = datetime.now().strftime("%H%M%S")
        run_id = f"{run_date}_{run_timestamp}"
        return run_date, run_timestamp, run_id

    def _ensure_output_dirs(self, subject: str) -> tuple[Path, Path, Path, Path]:
        base_img_dir = self.BASE_DIR / subject / "images"
        reel_dir = base_img_dir / "reel"
        carousel_dir = base_img_dir / "carousels"
        run_dir = self.BASE_DIR / subject / "runs"

        for d in [reel_dir, carousel_dir, run_dir]:
            d.mkdir(parents=True, exist_ok=True)

        return base_img_dir, reel_dir, carousel_dir, run_dir

    def _assign_qids(self, items, run_id: str, force: bool = False):
        if not (force or self.GENERATE_NEW_QIDS):
            return items
        for idx, q in enumerate(items, start=1):
            q.question_id = f"{run_id}_q{idx:02d}"
        return items

    def _write_metadata(self, run_dir: Path, run_id: str, metadata: dict) -> Path:
        metadata_path = run_dir / f"{run_id}_metadata.json"
        if self.WRITE_METADATA:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            logger.info("Metadata written to %s", metadata_path)
        return metadata_path

    # ---------- RENDERING FUNCTIONS ----------
    def _render_mind_benders(self, questions_per_run: int, subject: str) -> Path:
        """Handle brain teaser rendering with colorful themes for both reel and carousel formats."""
        from pybender.render.mind_bender_renderer import MindBenderRenderer
        
        # --------------------------------------------------
        # Run context
        # --------------------------------------------------
        RUN_DATE, RUN_TIMESTAMP, RUN_ID = self._new_run_context()
        logger.info("Starting mind_benders run: %s", RUN_ID)
        
        # --------------------------------------------------
        # Output directories
        # --------------------------------------------------
        base_img_dir, reel_dir, carousel_dir, run_dir = self._ensure_output_dirs(subject)
    
        # --------------------------------------------------
        # Generate puzzle questions
        # --------------------------------------------------
        if self.USE_STATIC_QUESTIONS:
            logger.info("Using static questions from output/questions.json")
            with open("output/questions.json", "r") as f:
                questions_data = json.load(f)
                topic, content_type = "mind_benders", "puzzle"
                # topic, content_type = "javascript", "code_output"
                questions = [MindBenderQuestion(**q) for q in questions_data]
        else:
            logger.info(f"Generating {questions_per_run} brain teaser puzzles for subject '{subject}' from LLM...")
            qg = QuestionGenerator()
            questions, topic, content_type = qg.generate_questions(questions_per_run, subject=subject)
        
        # Convert to MindBenderQuestion objects
        mind_bender_questions = []
        for q_dict in questions:
            if isinstance(q_dict, dict):
                mb_q = MindBenderQuestion(**q_dict)
            else:
                mb_q = q_dict
            mind_bender_questions.append(mb_q)

        if self.GENERATE_NEW_QIDS:
            mind_bender_questions = self._assign_qids(mind_bender_questions, RUN_ID)
        
        # --------------------------------------------------
        # Initialize renderer and select theme
        # --------------------------------------------------
        renderer = MindBenderRenderer()
        theme = renderer.select_random_theme()
        logger.info(f"🎨 Using theme: {theme['name']}")

        # --------------------------------------------------
        # Metadata setup
        # --------------------------------------------------
        metadata = {
            "run_id": RUN_ID,
            "run_date": RUN_DATE,
            "run_timestamp": RUN_TIMESTAMP,
            "subject": subject,
            "content_type": content_type,
            "theme": theme["name"],
            "generator": {
                "model": self.MODEL,
                "topic": topic if topic else "DEFAULT"
            },
            "questions": []
        }
        
        # --------------------------------------------------
        # Render puzzle cards for each question in both formats
        # --------------------------------------------------
        logger.info("Rendering brain teaser images (reel + carousel)...")
        
        for q in mind_bender_questions:
            q_slug = slugify(q.title)
            question_dict = q.model_dump() if hasattr(q, 'model_dump') else q.dict()
            
            # ==========================================
            # WELCOME COVER - Per question with category
            # ==========================================
            reel_welcome_img = reel_dir / f"{q.question_id}_welcome.png"
            carousel_welcome_img = carousel_dir / f"{q.question_id}_welcome.png"
            
            renderer.render_welcome_cover(theme, reel_welcome_img, size=renderer.REEL_SIZE, category=q.category)
            renderer.render_welcome_cover(theme, carousel_welcome_img, size=renderer.CAROUSEL_SIZE, category=q.category)
            
            logger.info(f"✅ Rendered WELCOME covers: {q.title} ({q.category})")
            
            # ==========================================
            # CTA PER QUESTION (reel + carousel)
            # ==========================================
            reel_cta_img = reel_dir / f"{q.question_id}_cta.png"
            carousel_cta_img = carousel_dir / f"{q.question_id}_cta.png"
            renderer.render_theme_cta(theme, reel_cta_img, carousel_cta_img)
            
            # ==========================================
            # REEL FORMAT (1080x1920) - in reel/ directory
            # ==========================================
            reel_question_img = reel_dir / f"{q.question_id}_question.png"
            reel_hint_img = reel_dir / f"{q.question_id}_hint.png"
            reel_answer_img = reel_dir / f"{q.question_id}_answer.png"
            
            renderer.render_puzzle_card(question_dict, theme, reel_question_img, size=renderer.REEL_SIZE)
            renderer.render_hint_card(question_dict, theme, reel_hint_img, size=renderer.REEL_SIZE)
            renderer.render_answer_card(question_dict, theme, reel_answer_img, size=renderer.REEL_SIZE)
            
            logger.info(f"✅ Rendered (REEL): {q.title}")
            
            # ==========================================
            # CAROUSEL FORMAT (1080x1080) - in carousels/ directory
            # ==========================================
            carousel_question_img = carousel_dir / f"{q.question_id}_question.png"
            carousel_hint_img = carousel_dir / f"{q.question_id}_hint.png"
            carousel_answer_img = carousel_dir / f"{q.question_id}_answer.png"
            
            renderer.render_puzzle_card(question_dict, theme, carousel_question_img, size=renderer.CAROUSEL_SIZE)
            renderer.render_hint_card(question_dict, theme, carousel_hint_img, size=renderer.CAROUSEL_SIZE)
            renderer.render_answer_card(question_dict, theme, carousel_answer_img, size=renderer.CAROUSEL_SIZE)
            
            logger.info(f"✅ Rendered (CAROUSEL): {q.title}")
            
            # Add to metadata
            metadata["questions"].append({
                "question_id": q.question_id,
                "title": q.title,
                "category": q.category,
                "slug": q_slug,
                "content": question_dict,
                "assets": {
                    "reel": {
                        "welcome_image": str(reel_welcome_img),
                        "cta_image": str(reel_cta_img),
                        "question_image": str(reel_question_img),
                        "hint_image": str(reel_hint_img),
                        "answer_image": str(reel_answer_img)
                    },
                    "carousel": {
                        "welcome_image": str(carousel_welcome_img),
                        "cta_image": str(carousel_cta_img),
                        "question_image": str(carousel_question_img),
                        "hint_image": str(carousel_hint_img),
                        "answer_image": str(carousel_answer_img)
                    }
                }
            })
        
        logger.info("All mind_bender images rendered successfully (reel + carousel)")
        
        
        # --------------------------------------------------
        # Write metadata.json
        # --------------------------------------------------
        if self.WRITE_METADATA:
            metadata_path = self._write_metadata(run_dir, RUN_ID, metadata)
        
        logger.info("Mind bender rendering process completed successfully")
        return metadata_path

    def _render_psychology_cards(self, questions_per_run: int, subject: str) -> Path:
        from pybender.render.psychology_renderer import PsychologyRenderer

        # --------------------------------------------------
        # Run context
        # --------------------------------------------------
        RUN_DATE, RUN_TIMESTAMP, RUN_ID = self._new_run_context()
        logger.info(f"Starting {subject} run: {RUN_ID}")

        # --------------------------------------------------
        # Output directories
        # --------------------------------------------------
        base_img_dir, reel_dir, carousel_dir, run_dir = self._ensure_output_dirs(subject)
    
        # --------------------------------------------------
        # Generate puzzle questions
        # --------------------------------------------------
        if self.USE_STATIC_QUESTIONS:
            logger.info("Using static questions from output/questions.json")
            with open("output/questions.json", "r") as f:
                questions_data = json.load(f)
                topic, content_type = "psychology", "wisdom_card"
                # topic, content_type = "javascript", "code_output"
                questions = [PsychologyCard(**q) for q in questions_data]
        else:
            logger.info(f"Generating {questions_per_run} psychology statements for subject '{subject}' from LLM...")
            qg = QuestionGenerator()
            questions, topic, content_type = qg.generate_questions(questions_per_run, subject=subject)
        
        # Convert to PsychologyCard objects
        psychology_statements = []
        for q_dict in questions:
            if isinstance(q_dict, dict):
                pc = PsychologyCard(**q_dict)
            else:
                pc = q_dict
            psychology_statements.append(pc)

        # Assign stable question IDs
        if self.GENERATE_NEW_QIDS:
            questions = self._assign_qids(psychology_statements, RUN_ID)
        
        # --------------------------------------------------
        # Initialize renderer and select theme
        # --------------------------------------------------
        renderer = PsychologyRenderer()
        theme = renderer.select_random_theme()
        logger.info(f"🎨 Using theme: {theme['name']}")

        # --------------------------------------------------
        # Metadata setup
        # --------------------------------------------------
        metadata = {
            "run_id": RUN_ID,
            "run_date": RUN_DATE,
            "run_timestamp": RUN_TIMESTAMP,
            "subject": subject,
            "content_type": content_type,
            "theme": theme["name"],
            "generator": {
                "model": self.MODEL,
                "topic": topic if topic else "DEFAULT"
            },
            "questions": []
        }
        
        # --------------------------------------------------
        # Render psychology cards for each question in both formats
        # --------------------------------------------------
        logger.info("Rendering psychology images (reel + carousel)...")
        
        for q in questions:
            q_slug = slugify(q.title)
            question_dict = q.model_dump() if hasattr(q, 'model_dump') else q.dict()
            
            # ==========================================
            # Card 1: WELCOME COVER - Per question with category
            # ==========================================
            reel_welcome_img = reel_dir / f"{q.question_id}_1_welcome.png"
            carousel_welcome_img = carousel_dir / f"{q.question_id}_1_welcome.png"
            
            renderer.render_welcome_card(theme, reel_welcome_img, size=renderer.REEL_SIZE, category=q.category)
            renderer.render_welcome_card(theme, carousel_welcome_img, size=renderer.CAROUSEL_SIZE, category=q.category)
            
            logger.info(f"✅ Rendered WELCOME card: {q.title} ({q.category})")
            
            # ==========================================
            # Card 2: STATEMENT CARD (reel + carousel)
            # ==========================================
            reel_statement_img = reel_dir / f"{q.question_id}_2_statement.png"
            carousel_statement_img = carousel_dir / f"{q.question_id}_2_statement.png"
            
            renderer.render_statement_card(question_dict, theme, reel_statement_img, size=renderer.REEL_SIZE)
            renderer.render_statement_card(question_dict, theme, carousel_statement_img, size=renderer.CAROUSEL_SIZE)
            
            logger.info(f"✅ Rendered STATEMENT card: {q.title}")
            
            # ==========================================
            # Card 3: EXPLANATION CARD (reel + carousel)
            # ==========================================
            reel_explanation_img = reel_dir / f"{q.question_id}_3_explanation.png"
            carousel_explanation_img = carousel_dir / f"{q.question_id}_3_explanation.png"
            
            renderer.render_explanation_card(question_dict, theme, reel_explanation_img, size=renderer.REEL_SIZE)
            renderer.render_explanation_card(question_dict, theme, carousel_explanation_img, size=renderer.CAROUSEL_SIZE)
            
            logger.info(f"✅ Rendered EXPLANATION card: {q.title}")
            
            # ==========================================
            # Card 4: EXAMPLE CARD (reel + carousel)
            # ==========================================
            reel_example_img = reel_dir / f"{q.question_id}_4_example.png"
            carousel_example_img = carousel_dir / f"{q.question_id}_4_example.png"
            
            renderer.render_example_card(question_dict, theme, reel_example_img, size=renderer.REEL_SIZE)
            renderer.render_example_card(question_dict, theme, carousel_example_img, size=renderer.CAROUSEL_SIZE)
            
            logger.info(f"✅ Rendered EXAMPLE card: {q.title}")
            
            # ==========================================
            # Card 5: APPLICATION CARD (reel + carousel)
            # ==========================================
            reel_application_img = reel_dir / f"{q.question_id}_5_application.png"
            carousel_application_img = carousel_dir / f"{q.question_id}_5_application.png"
            
            renderer.render_application_card(question_dict, theme, reel_application_img, size=renderer.REEL_SIZE)
            renderer.render_application_card(question_dict, theme, carousel_application_img, size=renderer.CAROUSEL_SIZE)
            
            logger.info(f"✅ Rendered APPLICATION card: {q.title}")
            
            # ==========================================
            # Card 6: CTA CARD (reel + carousel)
            # ==========================================
            reel_cta_img = reel_dir / f"{q.question_id}_6_cta.png"
            carousel_cta_img = carousel_dir / f"{q.question_id}_6_cta.png"
            
            renderer.render_cta_card(theme, reel_cta_img, carousel_cta_img)
            
            logger.info(f"✅ Rendered CTA card: {q.title}")
            
            # Add to metadata
            metadata["questions"].append({
                "question_id": q.question_id,
                "title": q.title,
                "category": q.category,
                "slug": q_slug,
                "content": question_dict,
                "assets": {
                    "reel": {
                        "welcome_image": str(reel_welcome_img),
                        "statement_image": str(reel_statement_img),
                        "explanation_image": str(reel_explanation_img),
                        "example_image": str(reel_example_img),
                        "application_image": str(reel_application_img),
                        "cta_image": str(reel_cta_img)
                    },
                    "carousel": {
                        "welcome_image": str(carousel_welcome_img),
                        "statement_image": str(carousel_statement_img),
                        "explanation_image": str(carousel_explanation_img),
                        "example_image": str(carousel_example_img),
                        "application_image": str(carousel_application_img),
                        "cta_image": str(carousel_cta_img)
                    }
                }
            })
        
        logger.info("All psychology images rendered successfully (reel + carousel)")
        
        
        # --------------------------------------------------
        # Write metadata.json
        # --------------------------------------------------
        if self.WRITE_METADATA:
            metadata_path = self._write_metadata(run_dir, RUN_ID, metadata)
        
        logger.info("Mind bender rendering process completed successfully")
        return metadata_path

    def _render_technical_content(self, questions_per_run: int, subject: str) -> Path:
        from pybender.render.tech_content_renderer import TechContentRenderer
        from pybender.render.tech_content_carousel_renderer import TechContentCarouselRenderer
        # --------------------------------------------------
        # Run context
        # --------------------------------------------------
        run_date, run_timestamp, run_id = self._new_run_context()
        topic = None
        logger.info("Starting run: %s", run_id)

        # --------------------------------------------------
        # Output directories (unified structure)
        # --------------------------------------------------
        base_img_dir, reel_dir, carousel_dir, run_dir = self._ensure_output_dirs(subject)
        welcome_img_path = base_img_dir / "welcome.png"
        cta_img_path = base_img_dir / "cta.png"

        renderer = TechContentRenderer()
        assets_base = Path("pybender/assets/backgrounds")
        transition_dir = assets_base / "transitions"

        renderer.render_transition_sequence(subject=subject, transition_dir=transition_dir)
        renderer.render_cta_image(subject=subject, out_path=cta_img_path)
        renderer.render_welcome_image(subject=subject, out_path=welcome_img_path)
        # --------------------------------------------------
        # Generate questions
        # --------------------------------------------------
        if self.USE_STATIC_QUESTIONS:
            logger.info("Using static questions from output/questions.json")
            with open("output/questions.json", "r") as f:
                questions_data = json.load(f)
                topic, content_type = "python", "code_output"
                questions = [Question(**q) for q in questions_data]
        else:
            qg = QuestionGenerator()
            questions, topic, content_type = qg.generate_questions(questions_per_run, subject=subject)

        # Assign stable question IDs (always for technical content)
        if self.GENERATE_NEW_QIDS:
            questions = self._assign_qids(questions, run_id, force=True)

        metadata = {
            "run_id": run_id,
            "run_date": run_date,
            "run_timestamp": run_timestamp,
            "subject": subject,
            "content_type": content_type,
            "generator": {
                "model": self.MODEL,
                "topic": topic if topic else "DEFAULT",
            },
            "questions": [],
        }   

        # --------------------------------------------------
        # Render assets
        # --------------------------------------------------
        logger.info("Rendering images...")

        carousel_renderer = TechContentCarouselRenderer()

        for q in questions:
            q_slug = slugify(q.title)

            layout_profile = resolve_layout_profile(content_type)

            # REEL FORMAT (1080x1920)
            reel_question_img = reel_dir / f"{q.question_id}_question.png"
            reel_answer_img = reel_dir / f"{q.question_id}_answer.png"

            # Render images to reel format (scenario included inline for QUESTION/SINGLE when applicable)
            renderer.render_image(q, reel_question_img, layout_profile, subject, RenderMode.QUESTION)
            renderer.render_image(q, reel_answer_img, layout_profile, subject, RenderMode.ANSWER)

            logger.info("✅ Rendered (REEL): %s", q.title)

            # CAROUSEL FORMAT (1080x1080)
            carousel_images = carousel_renderer.generate_carousel_slides(
                question=q,
                carousel_dir=carousel_dir,
                subject=subject,
                question_id=q.question_id,
            )

            metadata["questions"].append(
                {
                    "question_id": q.question_id,
                    "title": q.title,
                    "slug": q_slug,
                    "content": q.model_dump(),
                    "assets": {
                        "reel": {
                            "question_image": str(reel_question_img),
                            "answer_image": str(reel_answer_img),
                        },
                        "carousel_images": carousel_images,
                    },
                }
            )

        logger.info("All images rendered successfully")

        # --------------------------------------------------
        # Write metadata.json (single source of truth)
        # --------------------------------------------------
        metadata_path = run_dir / f"{run_id}_metadata.json"
        if self.WRITE_METADATA:
            metadata_path = self._write_metadata(run_dir, run_id, metadata)

        logger.info("Image rendering process completed successfully")
        return metadata_path


    def main(self, questions_per_run: int, subject: str = "python") -> Path:
        """
        Main entry point for rendering pipeline.
        Routes to specialized renderers based on subject type.
        """
        logger.info("Starting rendering pipeline for subject: %s", subject)

        # Route to appropriate renderer
        if subject == "mind_benders":
            return self._render_mind_benders(questions_per_run, subject)
        elif subject == "psychology":
            return self._render_psychology_cards(questions_per_run, subject)
        else:
            return self._render_technical_content(questions_per_run, subject)

if __name__ == "__main__":
    renderer = ImageRenderer()
    subjects = [
        "python", "sql", "regex", "system_design", 
        "linux", "mind_benders", "psychology"
        ,"docker_k8s", "javascript", "rust", "golang"
        ]

    import sys
    import time
    subject = sys.argv[1] 

    if subject and subject in subjects:
        renderer.main(1, subject=subject)
        time.sleep(2)
        sys.exit(0)

    else:
        for subject in subjects:
            try:
                renderer.main(1, subject=subject)
                time.sleep(2)
            except Exception as e:
                logger.exception("Error rendering for subject %s", subject)