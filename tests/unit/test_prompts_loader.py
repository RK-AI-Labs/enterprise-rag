"""Unit tests for the prompt template loader."""

import pytest

from app.prompts.loader import load_prompt

_TEMPLATE_NAMES = ["system", "retriever", "answer", "critique", "evaluation"]


@pytest.mark.parametrize("name", _TEMPLATE_NAMES)
def test_load_prompt_returns_nonempty_text(name: str) -> None:
    """Each documented template should load as non-empty, whitespace-stripped text."""
    prompt = load_prompt(name)

    assert prompt
    assert prompt == prompt.strip()


def test_load_prompt_raises_for_unknown_template() -> None:
    """Requesting a template that doesn't exist should raise `FileNotFoundError`."""
    with pytest.raises(FileNotFoundError):
        load_prompt("does-not-exist")
