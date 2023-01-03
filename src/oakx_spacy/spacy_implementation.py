"""Spacy Implementation."""
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable

import pystow
import spacy
from oaklib.datamodels.text_annotator import TextAnnotation, TextAnnotationConfiguration
from oaklib.interfaces import TextAnnotatorInterface
from oaklib.interfaces.obograph_interface import OboGraphInterface
from oaklib.selector import get_implementation_from_shorthand
from scispacy.abbreviation import AbbreviationDetector  # noqa
from scispacy.linking import EntityLinker  # noqa

__all__ = [
    "SpacyImplementation",
]

OX_SPACY_MODULE = pystow.module("oxpacy")
SERIALIZED_DIR = OX_SPACY_MODULE.join("serialized")
OUT_DIR = OX_SPACY_MODULE.join("output")
OUT_FILE = "spacyOutput.tsv"
SCI_SPACY_LINKERS = ["umls", "mesh", "go", "hpo", "rxnorm"]
MODELS = [
    "en_ner_craft_md",
    "en_ner_jnlpba_md",
    "en_ner_bc5cdr_md",
    "en_ner_bionlp13cg_md",
    "en_core_sci_scibert",
    "en_core_sci_sm",
    "en_core_sci_lg",
    "en_core_web_sm",
    "en_core_web_md",
    "en_core_web_lg",
    "en_core_web_trf"
]

"""
Available SciSpacy models
#* In order to install any of the below uncomment the corresponding line in `pyproject.toml`
1. en_ner_craft_md: A spaCy NER model trained on the CRAFT corpus.
2. en_ner_jnlpba_md: A spaCy NER model trained on the JNLPBA corpus.
3. en_ner_bc5cdr_md: A spaCy NER model trained on the BC5CDR corpus.
4. en_ner_bionlp13cg_md: A spaCy NER model trained on the BIONLP13CG corpus.
5. en_core_sci_scibert: A full spaCy pipeline for biomedical data with
                        a ~785k vocabulary and allenai/scibert-base as
                        the transformer model.
6. en_core_sci_sm: A full spaCy pipeline for biomedical data.
7. en_core_sci_md: A full spaCy pipeline for biomedical data with a
                   larger vocabulary and 50k word vectors.
8. en_core_sci_lg: A full spaCy pipeline for biomedical data
                   with a larger vocabulary and 600k word vectors.

Avaliable Spacy Models: English pipelines optimized for CPU.
#* In order to install any of the below run `python -m spacy download en_core_web_xxx`
1. en_core_web_sm: Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
2. en_core_web_md: Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
3. en_core_web_lg: Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
4. en_core_web_trf: Components: transformer, tagger, parser, ner, attribute_ruler, lemmatizer.
"""
DEFAULT_MODEL = "en_ner_craft_md"

"""
Available linkers:
1. umls: Links to the Unified Medical Language System,
        levels 0,1,2 and 9. This has ~3M concepts.
2. mesh: Links to the Medical Subject Headings.
        This contains a smaller set of higher quality entities,
        which are used for indexing in Pubmed. MeSH contains ~30k entities.
        NOTE: The MeSH KB is derived directly from MeSH itself,
        and as such uses different unique identifiers than the other KBs.
3. rxnorm: Links to the RxNorm ontology.
        RxNorm contains ~100k concepts focused on normalized names for clinical drugs.
        It is comprised of several other drug vocabularies commonly used in
        pharmacy management and drug interaction,
        including First Databank, Micromedex, and the Gold Standard Drug Database.
4. go: Links to the Gene Ontology. The Gene Ontology contains ~67k concepts
       focused on the functions of genes.
5. hpo: Links to the Human Phenotype Ontology.
        The Human Phenotype Ontology contains 16k concepts focused on phenotypic
        abnormalities encountered in human disease.
"""
DEFAULT_LINKER = "umls"
# ! CLI command:
#   runoak -i spacy: annotate --text-file tests/input/text.txt --model en_ner_craft_md


@dataclass
class SpacyImplementation(TextAnnotatorInterface, OboGraphInterface):
    """Spacy Implementation."""

    def __post_init__(self):
        """Post-instantiation the SpacyImplementation object."""
        if self.resource.slug:
            slug = self.resource.slug
            if slug in SCI_SPACY_LINKERS:
                self.entity_linker = slug
            else:
                self.oi = get_implementation_from_shorthand(slug)
        self.output_dir = OUT_DIR

    def annotate_file(
        self,
        text_file: Path,
        configuration: TextAnnotationConfiguration,
    ) -> Iterable[TextAnnotation]:
        """Annotate text from a file.

        :param text: Text to be annotated.
        :param configuration: TextAnnotationConfiguration , defaults to None
        :yield: Annotated result
        """
        if isinstance(text_file, TextIOWrapper):
            for line in text_file.readlines():  # type: ignore
                yield from self.annotate_text(line, configuration)
        else:
            for line in text_file.read_text():  # type: ignore
                yield from self.annotate_text(line, configuration)

    def annotate_text(
        self, text: str, configuration: TextAnnotationConfiguration
    ) -> Iterable[TextAnnotation]:
        """Annotate text from a file.

        :param text: Text to be annotated.
        :param configuration: TextAnnotationConfiguration , defaults to None
        :yield: Annotated result
        """
        if not configuration:
            configuration = TextAnnotationConfiguration()

        if not hasattr(self, "nlp"):
            self._set_model_and_linker(configuration)

        doc = self.nlp(text.strip())

        for entities in doc.ents:
            for entity in entities.ents:
                for id, confidence in entity._.kb_ents:
                    linker_object = self.linker.kb.cui_to_entity[id]
                    keys = [
                        item
                        for item in dir(linker_object)
                        if not item.startswith("_") and item not in ["count", "index"]
                    ]
                    linker_dict = {k: linker_object.__getattribute__(k) for k in keys}
                    if str(entity) in str(doc._.abbreviations):
                        abrv = [item for item in doc._.abbreviations if str(item) == str(entity)][0]
                        text = entities.text + " [" + str(abrv._.long_form) + "]"
                    else:
                        text = entities.text
                    yield TextAnnotation(
                        subject_text_id=id,
                        subject_label=text,
                        subject_start=entities.start,
                        subject_end=entities.end,
                        confidence=confidence,
                        subject_source=entity.sent,
                        info=linker_dict,
                    )

    def _set_model_and_linker(self, configuration: TextAnnotationConfiguration) -> None:
        if not hasattr(self, "entity_linker"):
            self.entity_linker = DEFAULT_LINKER

        if hasattr(configuration, "model") and configuration.model is not None:
            self.model = configuration.model
            if configuration.model in MODELS:
                self.model = configuration.model
            else:
                raise (
                    ValueError(
                        f"Model provided "
                        f"'{configuration.model}' is invalid. "
                        f"Choose one of the following: {MODELS}"
                        f" OR verify if the desired model is installed."
                    )
                )
        else:
            self.model = DEFAULT_MODEL

        self.nlp = spacy.load(self.model)
        self.nlp.add_pipe("abbreviation_detector")
        self.nlp.add_pipe(
            "scispacy_linker",
            config={"resolve_abbreviations": True, "linker_name": self.entity_linker},
        )
        self.linker = self.nlp.get_pipe("scispacy_linker")
