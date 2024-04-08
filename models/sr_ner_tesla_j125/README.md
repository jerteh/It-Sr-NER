sr_ner_tesla_j125 is a spaCy model meticulously fine-tuned for Named Entity Recognition in Serbian language texts. This advanced model incorporates a transformer layer based on XLM-R-BERTić, enhancing its analytical capabilities. It is proficient in identifying 7 distinct categories of entities: PERS (persons), ROLE (professions), DEMO (demonyms), ORG (organizations), LOC (locations), WORK (artworks), and EVENT (events). Detailed information about these categories is available in the accompanying table. The development of this model has been made possible through the support of the Science Fund of the Republic of Serbia, under grant #7276, for the project 'Text Embeddings - Serbian Language Applications - TESLA'.

| Feature | Description |
| --- | --- |
| **Name** | `sr_ner_tesla_j125` |
| **Version** | `1.0.0` |
| **spaCy** | `>=3.7.2,<3.8.0` |
| **Default Pipeline** | `transformer`, `ner` |
| **Components** | `transformer`, `ner` |
| **Vectors** | 0 keys, 0 unique vectors (0 dimensions) |
| **Sources** | n/a |
| **License** | `CC BY-SA 3.0` |
| **Author** | [Milica Ikonić Nešić, Saša Petalinkar, Mihailo Škorić, Ranka Stanković](https://tesla.rgf.bg.ac.rs/) |

### Label Scheme

<details>

<summary>View label scheme (7 labels for 1 components)</summary>

| Component | Labels |
| --- | --- |
| **`ner`** | `DEMO`, `EVENT`, `LOC`, `ORG`, `PERS`, `ROLE`, `WORK` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `ENTS_F` | 95.20 |
| `ENTS_P` | 94.90 |
| `ENTS_R` | 95.50 |
| `TRANSFORMER_LOSS` | 159576.78 |
| `NER_LOSS` | 169201.76 |