# oakx-spacy

[Spacy](https://spacy.io) + [SciSpacy](https://scispacy.apps.allenai.org) plugin for OAK.

**ALPHA**

## Usage

### Non-developers:
Create a preferred virtual environment (`conda`, `poetry`, `venv` etc.). Install `oakx-spacy` using `pip install`.
```
pip install oakx-spacy
```

Next, desired models (Spacy and/or SciSpacy) need to be downloaded/installed. Following is the list of models available.

#### Spacy models
English pipelines optimized for CPU.
In order to install any of the below run `python -m spacy download en_core_web_xxx`

1. `en_core_web_sm`: Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
2. `en_core_web_md`: Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
3. `en_core_web_lg`: Components: tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer.
4. `en_core_web_trf`: Components: transformer, tagger, parser, ner, attribute_ruler, lemmatizer.

#### SciSpacy models
In order to install any of the below use the corresponding line in [`pyproject.toml`](https://github.com/hrshdhgd/oakx-spacy/blob/main/pyproject.toml#L35-L65)

For example, if [CRAFT corpus](https://github.com/UCDenver-ccp/CRAFT) trained model is desired, do the following:
```
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_ner_craft_md-0.5.1.tar.gz
```
Available models:

1. `en_ner_craft_md`: A spaCy NER model trained on the CRAFT corpus.
2. `en_ner_jnlpba_md`: A spaCy NER model trained on the JNLPBA corpus.
3. `en_ner_bc5cdr_md`: A spaCy NER model trained on the BC5CDR corpus.
4. `en_ner_bionlp13cg_md`: A spaCy NER model trained on the BIONLP13CG corpus.
5. `en_core_sci_scibert`: A full spaCy pipeline for biomedical data with a ~785k vocabulary and allenai/scibert-base as the transformer model.
6. `en_core_sci_sm`: A full spaCy pipeline for biomedical data.
7. `en_core_sci_md`: A full spaCy pipeline for biomedical data with a larger vocabulary and 50k word vectors.
8. `en_core_sci_lg`: A full spaCy pipeline for biomedical data with a larger vocabulary and 600k word vectors.

#### SciSpacy linkers
These come preinstalled with `scispacy` package itself. Available linkers are:
1. `umls`: Links to the Unified Medical Language System, levels 0,1,2 and 9. This has ~3M concepts.
2. `mesh`: Links to the Medical Subject Headings. This contains a smaller set of higher quality entities, which are used for indexing in Pubmed. MeSH contains ~30k entities. NOTE: The MeSH KB is derived directly from MeSH itself, and as such uses different unique identifiers than the other KBs.
3. `rxnorm`: Links to the RxNorm ontology. RxNorm contains ~100k concepts focused on normalized names for clinical drugs. It is comprised of several other drug vocabularies commonly used in pharmacy management and drug interaction, including First Databank, Micromedex, and the Gold Standard Drug Database.
4. `go`: Links to the Gene Ontology. The Gene Ontology contains ~67k concepts focused on the functions of genes.
5. `hpo`: Links to the Human Phenotype Ontology. The Human Phenotype Ontology contains 16k concepts focused on phenotypic abnormalities encountered in human disease.

### Developers:

#### Clone the repository
```
git clone https://github.com/hrshdhgd/oakx-spacy.git
```

#### Install `poetry`
```
pip install poetry
```

#### SciSpacy models
In [`pyproject.toml`](https://github.com/hrshdhgd/oakx-spacy/blob/main/pyproject.toml#L35-L65), uncomment the 2 lines corresponding to the models desired. For example, if the desired model is the CRAFT corpus, uncomment the following:

```
[tool.poetry.dependencies.en_ner_craft_md]
url = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_ner_craft_md-0.5.1.tar.gz"
```

#### Install dependencies
```
poetry install
```

#### Spacy models
Instructions similar to non-developers. Just make sure to prepend the command by `poetry run`

The default model is set to `en_ner_craft_md` and default linker to `umls`.

## How it works
The input argument can be expressed as `spacy:linker-name` e.g. `spacy:mesh`.
There are two possible inputs to this plugin:
1. A `.txt` file [`runoak -i spacy: annotate --text-file text.txt`]
2. Words that need to be annotated.[`runoak -i spacy: Myeloid derived suppressor cells (MDSC) are immature myeloid cells with immunosuppressive activity.`]
# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [oakx-plugin-cookiecutter](https://github.com/INCATools/oakx-plugin-cookiecutter) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).