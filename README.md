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

### Using SciSpacy.
The input argument can be expressed as `spacy:linker-name` e.g. `spacy:mesh`.
There are two possible inputs to this plugin:
1. A `.txt` file [`runoak -i spacy: annotate --text-file text.txt`]
2. Words that need to be annotated.[`runoak -i spacy: annotate Myeloid derived suppressor cells \(MDSC\) are immature myeloid cells with immunosuppressive activity.`] should yield:
```
confidence: 0.9999999403953552
info: JsonObj(aliases=['t cell suppressor', 'suppressor cell', 'T suppressor cell',
  'suppressor cells', 'Suppressor cell', 'suppressor T lymphocyte', 'cells suppressor
  t', 'Suppressor cells', 'Suppressor cell (cell)'], canonical_name='Suppressor T
  Lymphocyte', concept_id='C0038856', definition='subpopulation of CD8+ T-lymphocytes
  which suppress antibody production or inhibit cellular immune responses.', types=['T025'])
subject_end: 30
subject_label: suppressor cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 15
subject_text_id: C0038856

---
confidence: 0.9177235960960388
info: JsonObj(aliases=['nTregs', 'CD4+CD25+ regulatory T cells', 'T-regulatory cell',
  'CD4+CD25+ T lymphocyte', 'Tr cell', 'regulatory T cell', 'CD4+CD25+ T Lymphocyte',
  'T reg', 'suppressor T cell', 'CD4+ CD25+ Regulatory T Cells', 'T lymphocyte positive
  for both CD4 antigen and CD25 antigen', 'T lymphocyte positive for both CD4 antigen
  and CD25 antigen (cell)'], canonical_name='CD4+ CD25+ Regulatory T Cells', concept_id='C1267822',
  definition='Regulatory T cells that express CD4 and CD25 (interleukin 2 receptor)
  antigens, with immunomodulating activity. CD4+CD25+ T regulatory cells (Tregs),
  a subset of CD4+ T cells expressing high levels of CD25 and the transcription factor
  Foxp3, are essential in maintaining immunologic homeostasis, preventing autoimmunity
  by suppressing self-reactive T cells; CD4+CD25+ Tregs may induce tolerance to allogeneic
  organ transplants such as hematopoetic stem cell transplants (HSCTs).', types=['T025'])
subject_end: 30
subject_label: suppressor cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 15
subject_text_id: C1267822

---
confidence: 0.9177235960960388
info: JsonObj(aliases=['Suppressor-Effector T-Lymphocyte', 'Suppressor effector T
  lymphocyte', 'T Suppressor Cell', 'Suppressor T Lymphocyte', 'Suppressor-Effector
  T-Cells', 'Suppressor-Effector T-Lymphocytes'], canonical_name='Suppressor effector
  T lymphocyte', concept_id='C2355611', definition='T-lymphocytes that respond to
  signals from suppressor-inducer T-cells by inhibiting either cell-mediated immunity
  or antibody production by B-cells.', types=['T025'])
subject_end: 30
subject_label: suppressor cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 15
subject_text_id: C2355611

---
confidence: 0.8558955192565918
info: JsonObj(aliases=['Suppressor', 'Suppressor Device'], canonical_name='Suppressor
  Device', concept_id='C1710252', definition='An electrical device designed to reduce
  or eliminate unwanted currents.', types=['T073'])
subject_end: 30
subject_label: suppressor cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 15
subject_text_id: C1710252

---
confidence: 0.7574830651283264
info: JsonObj(aliases=['Second-Site Suppressor Genes', 'Suppressor Genes, Second-Site',
  'gene suppressor', 'Suppressor gene', 'Second Site Suppressor Genes', 'Second-Site
  Suppressor Gene', 'Suppressor Gene', 'Genes, Second Site Suppressor', 'Gene, Second-Site
  Suppressor', 'Genes, Second-Site Suppressor', 'suppressor gene', 'Suppressor gene
  (substance)', 'Gene, Suppressor', 'Suppressor Genes', 'Suppressor Gene, Second-Site'],
  canonical_name='Genes, Suppressor', concept_id='C0017372', definition='Genes that
  have a suppressor allele or suppressor mutation (SUPPRESSION, GENETIC) which cancels
  the effect of a previous mutation, enabling the wild-type phenotype to be maintained
  or partially restored. For example, amber suppressors cancel the effect of an AMBER
  NONSENSE MUTATION.', types=['T028'])
subject_end: 30
subject_label: suppressor cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 15
subject_text_id: C0017372

---
confidence: 1.0
info: JsonObj(aliases=['Bone Marrow Myeloid Stem Cell', 'Cell, Myeloid Stem', 'Cells,
  Myeloid Stem', 'stem cells myeloid', 'Myeloid Stem Cells', 'Myeloid Progenitor Cell',
  'Myeloid cell', 'Progenitor Cells, Myeloid', 'Stem Cell, Myeloid', 'Myeloid Progenitor
  Cells', 'Stem Cells, Myeloid', 'Cells, Myeloid Progenitor', 'Progenitor Cell, Myeloid',
  'myeloid stem cell', 'Myeloid Stem Cell', 'Cell, Myeloid Progenitor', 'Myeloid stem
  cell'], canonical_name='Myeloid Progenitor Cells', concept_id='C0596993', definition='A
  hematopoietic stem cell found in the bone marrow that is committed to form erythrocytes,
  megakaryocytes, and all leukocytes except lymphocytes.', types=['T025'])
subject_end: 64
subject_label: myeloid cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 52
subject_text_id: C0596993

---
confidence: 1.0
info: JsonObj(aliases=['Cells, Myeloid', 'Myeloid Cells', 'myeloid cell', 'myeloid
  cells', 'Myeloid Cell', 'Cell, Myeloid'], canonical_name='Myeloid Cells', concept_id='C0887899',
  definition='The classes of BONE MARROW-derived blood cells in the monocytic series
  (MONOCYTES and their precursors) and granulocytic series (GRANULOCYTES and their
  precursors).', types=['T025'])
subject_end: 64
subject_label: myeloid cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 52
subject_text_id: C0887899

---
confidence: 0.8978284001350403
info: JsonObj(aliases=['Myeloid Stem Cell', 'Myeloid Colony Forming Unit', 'CFU-GEMM',
  'Common Myeloid Progenitor Cell'], canonical_name='Myeloid Stem Cell', concept_id='C4761416',
  definition='A stem cell derived from the hematopoietic stem cell that generates
  myeloid cells (granulocyte, erythrocyte, monocyte, megakaryocyte).', types=['T025'])
subject_end: 64
subject_label: myeloid cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 52
subject_text_id: C4761416

---
confidence: 0.8651273250579834
info: JsonObj(aliases=['myelogenous', 'Myeloid', 'myeloid', 'Myelogenous', 'Myeloid
  (qualifier value)'], canonical_name='Myeloid', concept_id='C0439677', definition='Having
  to do with or resembling the bone marrow. May also refer to certain types of hematopoietic
  (blood-forming) cells found in the bone marrow. Sometimes used as a synonym for
  myelogenous; for example, acute myeloid leukemia and acute myelogenous leukemia
  are the same disease.', types=['T080'])
subject_end: 64
subject_label: myeloid cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 52
subject_text_id: C0439677

---
confidence: 0.8391554355621338
info: JsonObj(aliases=['Myeloid Cell Leukemia Sequence 1', 'Myeloid Cell Leukemia
  Sequence 1 Protein', 'Induced Myeloid Leukemia Cell Differentiation Protein Mcl-1',
  'Myeloid Cell Factor-1', 'Myeloid Cell Factor 1', 'Induced Myeloid Leukemia Cell
  Differentiation Protein Mcl 1', 'Factor-1, Myeloid Cell', 'Cell Factor-1, Myeloid'],
  canonical_name='Myeloid Cell Leukemia Sequence 1 Protein', concept_id='C1510444',
  definition='A member of the myeloid leukemia factor (MLF) protein family with multiple
  alternatively spliced transcript variants encoding different protein isoforms. In
  hematopoietic cells, it is located mainly in the nucleus, and in non-hematopoietic
  cells, primarily in the cytoplasm with a punctate nuclear localization. MLF1 plays
  a role in cell cycle differentiation.', types=['T116', 'T123'])
subject_end: 64
subject_label: myeloid cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 52
subject_text_id: C1510444
```

### Using an ontology
The input argument can be expressed as `spacy:sqlite:obo:name-of-ontology` e.g. `spacy:sqlite:obo:bero`.
1. A `.txt` file [`runoak -i spacy:sqlite:obo:bero annotate --text-file tests/input/text.txt`]
2. Words that need to be annotated.[`runoak -i spacy:sqlite:obo:bero annotate Myeloid derived suppressor cells \(MDSC\) are immature myeloid cells with immunosuppressive activity.`] should yield:
```
subject_end: 30
subject_label: Myeloid-Derived Suppressor Cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 0
subject_text_id: NCIT:C129908

---
subject_end: 64
subject_label: Immature Myeloid Cell
subject_source: myeloid derive suppressor cell ( mdsc ) be immature myeloid cell with
  immunosuppressive activity .
subject_start: 43
subject_text_id: NCIT:C113503
```
# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [oakx-plugin-cookiecutter](https://github.com/INCATools/oakx-plugin-cookiecutter) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).