"""Spacy Implementation test."""
import os
import unittest
from pathlib import Path

from oaklib.datamodels.text_annotator import TextAnnotationConfiguration
from oaklib.implementations.aggregator.aggregator_implementation import AggregatorImplementation
from oaklib.resource import OntologyResource
from oaklib.selector import get_implementation_from_shorthand

from oakx_spacy.spacy_implementation import SpacyImplementation

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
        self.input_dir = Path(__file__).resolve().parents[1] / "tests/input/"
        self.output_dir = Path(__file__).resolve().parents[1] / "tests/output/"
        self.input_file = self.input_dir / "text.txt"
        self.input_tsv = self.input_dir / "test.tsv"
        self.impl.output_dir = self.output_dir
        self.input_words = "Myeloid derived suppressor cells (MDSC) \
            are immature myeloid cells with immunosuppressive activity."

        self.config = TextAnnotationConfiguration()
        impl_1 = SpacyImplementation(OntologyResource(slug="sqlite:obo:envo"))
        impl_2 = SpacyImplementation(OntologyResource(slug="sqlite:obo:pato"))
        self.impl2 = AggregatorImplementation(implementations=[impl_1, impl_2])

    def test_annotate_text(self):
        """Test annotation of text."""
        results = list(self.impl.annotate_text(self.input_words, self.config))
        self.assertEqual(len(results), 10)
        self.assertTrue("C1510444" in [x.object_id for x in results])

    # !FIXME:
    # @unittest.skip("NEED A VALID CONDITION LIKE ABOVE TO WORK")
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

    def test_annotate_text_using_aggregator(self):
        """Test annotation using oaklib's aggregator."""
        object_of_interest = ["NCBITaxon:2116530", "CL:0000000", "PATO:0001501", "CL:0000763"]
        self.config.include_aliases = True
        results = list(self.impl2.annotate_text(self.input_words, self.config))
        for re in results:
            self.assertTrue(re.object_id in object_of_interest)

    def test_annotate_file_using_aggregator(self):
        """Test annotation using oaklib's aggregator."""
        prefixes_of_interest = ["CHEBI", "PATO", "PO", "ENVO", "UBERON", "NCBITaxon", "GO"]
        # self.config.include_aliases = True
        results = list(self.impl2.annotate_file(self.input_tsv, self.config))
        for re in results:
            prefix = re.object_id.split(":")[0]
            self.assertTrue(prefix in prefixes_of_interest)
