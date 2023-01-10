"""Spacy Implementation."""

import csv
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, List

import pystow
import spacy
from oaklib.datamodels.text_annotator import TextAnnotation, TextAnnotationConfiguration
from oaklib.interfaces import TextAnnotatorInterface
from oaklib.interfaces.obograph_interface import OboGraphInterface
from oaklib.selector import get_implementation_from_shorthand
from scispacy.abbreviation import AbbreviationDetector  # noqa
from scispacy.linking import EntityLinker  # noqa
from spacy.pipeline import entityruler  # noqa
from spacy.tokens import Span

__all__ = [
    "SpacyImplementation",
]

OX_SPACY_MODULE = pystow.module("oxpacy")
SERIALIZED_DIR = OX_SPACY_MODULE.join("serialized")
PIPELINE = OX_SPACY_MODULE.join("pipeline")
OUT_FILE = "spacyOutput.tsv"
TERMS_PICKLE = "terms.pickle"
PHRASE_MATCHER_FILENAME = "phrase_matcher.pickle"
PATTERNS_FILENAME = "patterns.jsonl"

# REGEX_TO_FILTER_OUT = r"(\[|\]|\(|\)|)+"
TERMS_PATH = SERIALIZED_DIR / TERMS_PICKLE
CONFIG_FILE = PIPELINE / "config.cfg"

PROJECT_DIR = Path(__file__).resolve().parents[2]
STOPWORDS_PATH = PROJECT_DIR / "stopwords.txt"
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
    "en_core_web_trf",
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
#   OR
#   runoak -i spacy:sqlite:obo:bero annotate --text-file tests/input/text.txt


@dataclass
class SpacyImplementation(TextAnnotatorInterface, OboGraphInterface):
    """Spacy Implementation."""

    def __post_init__(self):
        """Post-instantiation the SpacyImplementation object."""
        if self.resource.slug:
            slug = self.resource.slug
            if slug in SCI_SPACY_LINKERS:
                self.entity_linker = slug
                self.outfile = Path(f"{slug}_linked_{OUT_FILE}")
            else:
                self.oi = get_implementation_from_shorthand(slug)
                self.phrase_matcher_attr = "LOWER"
                patterns_fn = slug.split(":")[-1]
                patterns = f"{patterns_fn}_{PATTERNS_FILENAME}"
                self.patterns_path = SERIALIZED_DIR / patterns
                self.outfile = Path(f"{patterns_fn}_based_{OUT_FILE}")
        else:
            slug = DEFAULT_LINKER
            self.entity_linker = slug
            self.outfile = Path(f"{slug}_linked_{OUT_FILE}")

        self.stopwords = STOPWORDS_PATH.read_text().splitlines()
        if (self.outfile).is_file():
            self.outfile.unlink()

    def _clean_string_and_lemma(self, string):
        return " ".join([token.lemma_ for token in self.nlp(string)])
        # tmp_str = re.sub(REGEX_TO_FILTER_OUT, '', string)
        # return " ".join([token.lemma_ for token in self.nlp(tmp_str.replace('-'," "))])

    def _prepare_output(self, entity: Span) -> dict:
        info = {}
        output_dict = {
            "subject_id": entity.ent_id_,
            "subject_label": entity.label_,
            "start": entity.start_char,
            "end": entity.end_char,
            "sentence": entity.sent,
        }
        for _, item in enumerate(self.oi.alias_map_by_curie(entity.ent_id_).items()):
            if len(item) > 0:
                if "alias" not in info:
                    info["alias_map"] = {item[0]: item[1]}
                else:
                    info["alias_map"].update({item[0]: item[1]})

        for _, item in enumerate(self.oi.synonym_map_for_curies(entity.ent_id_).items()):
            if len(item) > 0:
                if "synonym" not in info:
                    info["synonym_map"] = {item[0]: item[1]}
                else:
                    info["synonym_map"].update({item[0]: item[1]})

        output_dict.update(info)
        return output_dict

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
            self._setup_nlp_pipeline(configuration)

        doc = self.nlp(self._clean_string_and_lemma(text))
        fieldnames = [
            "subject_id",
            "subject_label",
            "start",
            "end",
            "sentence",
            "alias_map",
            "synonym_map",
        ]

        if hasattr(self, "oi"):
            for entity in doc.ents:
                if entity.ent_id_ and entity.text not in self.stopwords:
                    info = {}
                    output_dict = self._prepare_output(entity)
                    for k in [
                        key for key in output_dict.keys() if key in ["alias_map", "synonym_map"]
                    ]:
                        info[k] = output_dict[k]
                    self.write_output(output_dict, fieldnames)

                    yield TextAnnotation(
                        subject_text_id=entity.ent_id_,
                        subject_label=entity.label_,
                        subject_start=entity.start_char,
                        subject_end=entity.end_char,
                        subject_source=entity.sent,
                        info=info,
                    )
        else:
            fieldnames = [
                "subject_id",
                "subject_label",
                "start",
                "end",
                "confidence",
                "sentence",
                "concept_id",
                "aliases",
                "canonical_name",
                "definition",
                "types",
            ]
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
                            abrv = [
                                item for item in doc._.abbreviations if str(item) == str(entity)
                            ][0]
                            text = entities.text + " [" + str(abrv._.long_form) + "]"
                        else:
                            text = entities.text
                        output_dict = {
                            "subject_id": id,
                            "subject_label": text,
                            "start": entities.start_char,
                            "end": entities.end_char,
                            "sentence": entity.sent,
                            "confidence": confidence,
                        }
                        output_dict.update(linker_dict)
                        self.write_output(output_dict, fieldnames)

                        yield TextAnnotation(
                            subject_text_id=id,
                            subject_label=text,
                            subject_start=entities.start_char,
                            subject_end=entities.end_char,
                            confidence=confidence,
                            subject_source=entity.sent,
                            info=linker_dict,
                        )

    def _setup_nlp_pipeline(self, configuration: TextAnnotationConfiguration) -> None:
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

        if hasattr(self, "oi"):
            # Use ontology terms.
            self._add_patterns()
        else:
            self.nlp.add_pipe("abbreviation_detector")
            # Use SciSpacy.
            if not hasattr(self, "entity_linker"):
                self.entity_linker = DEFAULT_LINKER
            self.nlp.add_pipe(
                "scispacy_linker",
                config={"resolve_abbreviations": True, "linker_name": self.entity_linker},
            )
            self.linker = self.nlp.get_pipe("scispacy_linker")

    def _get_pattern_list(self, phrase, raw_phrase, curie) -> List[dict]:
        split_tokens = phrase.split()

        token_dict = {
            "label": raw_phrase,
            "pattern": [{self.phrase_matcher_attr: token.lower()} for token in split_tokens],
            "id": curie,
        }

        phrase_dict = {
            "label": raw_phrase,
            "pattern": [{self.phrase_matcher_attr: phrase.lower()}],
            "id": curie,
        }

        return [token_dict, phrase_dict]

    def _add_patterns(self):
        if not self.patterns_path.is_file():
            # EntityRuler
            # source: https://spacy.io/usage/rule-based-matching#entityruler-usage
            self.list_of_pattern_dicts = []
            for curie in self.oi.entities(owl_type="owl:Class"):
                # Split phrases into individual tokens
                # if curie.startswith("<"):
                #     prefix = curie.split("_")[0].replace("<", "") + "_"
                # else:
                #     prefix = curie.split(":")[0]

                raw_phrase = str(self.oi.label(curie))
                phrase = self._clean_string_and_lemma(raw_phrase)
                # split_tokens = phrase.split()

                self.list_of_pattern_dicts.extend(
                    self._get_pattern_list(raw_phrase=raw_phrase, phrase=phrase, curie=curie)
                )
                if "-" in phrase:
                    phrase = phrase.replace("-", " ")
                    self.list_of_pattern_dicts.extend(
                        self._get_pattern_list(raw_phrase=raw_phrase, phrase=phrase, curie=curie)
                    )
                if "," in phrase and phrase.count(",") == 1 and not curie.startswith("CHEBI"):
                    multi_phrase = phrase.split(",")
                    for phr in multi_phrase:
                        self.list_of_pattern_dicts.extend(
                            self._get_pattern_list(raw_phrase=raw_phrase, phrase=phr, curie=curie)
                        )

            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            with self.nlp.select_pipes(enable="tagger"):
                ruler.add_patterns(self.list_of_pattern_dicts)

            ruler.to_disk(self.patterns_path)
            self.nlp.to_disk(PIPELINE)

        else:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner").from_disk(self.patterns_path)

    def write_output(self, output_dict: dict, fieldnames: list[str]):
        if (self.outfile).is_file():
            with open(self.outfile, "a", newline="") as o:
                writer = csv.DictWriter(o, delimiter="\t", fieldnames=fieldnames)
                writer.writerow(output_dict)
        else:
            with open(self.outfile, "w", newline="") as o:
                writer = csv.DictWriter(o, delimiter="\t", fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(output_dict)
