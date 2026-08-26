"""Engines: the protocol plus one module per engine, lazily imported."""

from ocrbench.engines.base import Engine
from ocrbench.engines.docling import DoclingEngine

__all__ = [
    "Engine",
    "DoclingEngine",
]
