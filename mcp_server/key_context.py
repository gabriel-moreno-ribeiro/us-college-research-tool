"""
Per-request API key context (BYOK).

Keys arrive via HTTP headers and live only for the duration of the request.
Uses contextvars for async safety.
"""
from __future__ import annotations
import contextvars

_scorecard_key: contextvars.ContextVar[str | None] = contextvars.ContextVar("scorecard_key", default=None)
_semantic_scholar_key: contextvars.ContextVar[str | None] = contextvars.ContextVar("semantic_scholar_key", default=None)


def set_keys(scorecard: str | None = None, semantic_scholar: str | None = None) -> None:
    if scorecard:
        _scorecard_key.set(scorecard)
    if semantic_scholar:
        _semantic_scholar_key.set(semantic_scholar)


def get_scorecard_key() -> str | None:
    return _scorecard_key.get()


def get_semantic_scholar_key() -> str | None:
    return _semantic_scholar_key.get()


def clear_keys() -> None:
    _scorecard_key.set(None)
    _semantic_scholar_key.set(None)
