"""Spacy Implementation."""
from dataclasses import dataclass

from oaklib.interfaces import BasicOntologyInterface


@dataclass
class SpacyImplementation(BasicOntologyInterface):
    """Spacy Implementation."""

    def __post_init__(self):
        """Initialize the SpacyImplementation class."""
        pass
