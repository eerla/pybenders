# pybenders/generator/prompt_loader.py
from pathlib import Path

def load_prompt(name: str) -> str:
    return Path(f"pybender/prompts/{name}").read_text()
