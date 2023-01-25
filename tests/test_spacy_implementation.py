"""Spacy Implementation test."""
import os
import unittest
from pathlib import Path

from oaklib.datamodels.text_annotator import TextAnnotationConfiguration
from oaklib.selector import get_implementation_from_shorthand

# Scan environment variables
for name, _ in os.environ.items():
    if "GITHUB" in name:
        CI_FLAG = False
        break
    else:
        CI_FLAG = True


class TestSpacyImplementation(unittest.TestCase):
    """SpacyImplementation test."""

    def setUp(self) -> None:
        """Set up implementation."""
        self.impl = get_implementation_from_shorthand("spacy:")
        self.input_file = Path(__file__).resolve().parents[1] / "tests/input/text.txt"
        self.input_tsv = Path(__file__).resolve().parents[1] / "tests/input/test.tsv"
        self.impl.output_dir = Path(__file__).resolve().parents[1] / "tests/output/"
        self.input_words = "Myeloid derived suppressor cells (MDSC) \
            are immature myeloid cells with immunosuppressive activity."

        self.config = TextAnnotationConfiguration()

    def test_annotate_text(self):
        """Test annotation of text."""
        results = list(self.impl.annotate_text(self.input_words, self.config))
        self.assertEqual(len(results), 10)
        self.assertTrue("C1510444" in [x.object_id for x in results])

    @unittest.skipIf(
        CI_FLAG is not None,
        "Avoid: Got SIGTERM, handling it as a KeyboardInterrupt",
    )
    def test_annotate_file_txt(self):
        """Test annotation of a file."""
        results = list(self.impl.annotate_file(self.input_file, self.config))
        self.assertEqual(len(results), 30)
        self.assertTrue("C1323350" in [x.object_id for x in results])

    @unittest.skipIf(
        CI_FLAG is not None,
        "Avoid: Got SIGTERM, handling it as a KeyboardInterrupt",
    )
    def test_annotate_file_tsv(self):
        """Test annotation of a file."""
        results = list(self.impl.annotate_file(self.input_tsv, self.config))
        self.assertEqual(len(results), 15)
        self.assertTrue("C4163697" in [x.object_id for x in results])
