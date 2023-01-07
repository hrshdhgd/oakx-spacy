"""Spacy Implementation test."""
import unittest
from pathlib import Path

from oaklib.datamodels.text_annotator import TextAnnotationConfiguration
from oaklib.selector import get_implementation_from_shorthand


class TestSpacyImplementation(unittest.TestCase):
    """SpacyImplementation test."""

    def setUp(self) -> None:
        """Set up implementation."""
        self.impl = get_implementation_from_shorthand("spacy:")
        self.input_file = Path(__file__).resolve().parents[1] / "tests/input/text.txt"
        self.impl.output_dir = Path(__file__).resolve().parents[1] / "tests/output/"
        self.input_words = "Myeloid derived suppressor cells (MDSC) \
            are immature myeloid cells with immunosuppressive activity."
        self.config = TextAnnotationConfiguration()

    # !FIXME:
    # @unittest.skipIf(
    #     os.getenv("GITHUB_ENV"),
    #     "Avoid: Got SIGTERM, handling it as a KeyboardInterrupt",
    # )
    @unittest.skip("NEED A VALID CONDITION LIKE ABOEVE TO WORK")
    def test_annotate_file(self):
        """Test annotation of a file."""
        results = list(self.impl.annotate_file(self.input_file, self.config))
        self.assertEqual(len(results), 15)
        self.assertTrue("C0439106" in [x.subject_text_id for x in results])

    def test_annotate_text(self):
        """Test annotation of text."""
        results = list(self.impl.annotate_text(self.input_words, self.config))
        self.assertEqual(len(results), 10)
        self.assertTrue("C0027022" in [x.subject_text_id for x in results])
