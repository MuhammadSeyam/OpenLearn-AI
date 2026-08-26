"""Dataset loaders: one explicit function per dataset, no shared interface."""

from ocrbench.datasets.bce import load_bce
from ocrbench.datasets.custom import load_custom
from ocrbench.datasets.misraj import load_misraj

__all__ = [
    "load_misraj",
    "load_bce",
    "load_custom",
]
