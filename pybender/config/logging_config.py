import logging
import os

try:
    from dotenv import load_dotenv
except ImportError:  # Optional dependency
    load_dotenv = None


def setup_logging(level: str | None = None) -> None:
    """Configure root logger for console output.

    - Level comes from arg or LOG_LEVEL env (default INFO)
    - Clears existing handlers to avoid duplicates when re-run
    - Adds a simple console handler
    - Lowers noisy third-party logs
    """
    if load_dotenv:
        # Load .env if present at repo root or current working dir
        load_dotenv()

    resolved_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()

    root = logging.getLogger()
    if root.handlers:
        root.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root.addHandler(handler)
    root.setLevel(resolved_level)

    # Quiet noisy libs
    logging.getLogger("instagrapi").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
