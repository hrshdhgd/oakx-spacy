"""Test SpacyImplementation."""
import unittest

from oaklib.implementations import get_implementation_resolver
from oaklib.selector import get_resource_from_shorthand

from oakx_spacy.spacy_implementation import SpacyImplementation
from tests import TEST_OWL


class TestSpacyImplementation(unittest.TestCase):
    """Test SpacyImplementation."""

    def test_plugin(self):
        """Test plugin."""
        implementation_resolver = get_implementation_resolver()
        resolved = implementation_resolver.lookup("spacy")
        self.assertEqual(resolved, SpacyImplementation)

        slug = f"spacy:{TEST_OWL}"
        r = get_resource_from_shorthand(slug)
        self.assertEqual(r.implementation_class, SpacyImplementation)
