"""Loads externalized prompt templates by name, so prompt text never lives inline in code."""

from functools import lru_cache
from pathlib import Path

_TEMPLATES_DIR = Path(__file__).parent / "templates"


@lru_cache
def load_prompt(name: str) -> str:
    """Return the contents of the `{name}.txt` template under `app/prompts/templates/`."""
    path = _TEMPLATES_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8").strip()
