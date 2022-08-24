### Details: https://spacy.io/models/ja#ja_core_news_sm

Japanese pipeline optimized for CPU. Components: tok2vec, morphologizer, parser, senter, ner, attribute_ruler.

| Feature | Description |
| --- | --- |
| **Name** | `ja_core_news_sm` |
| **Version** | `3.2.0` |
| **spaCy** | `>=3.2.0,<3.3.0` |
| **Default Pipeline** | `tok2vec`, `morphologizer`, `parser`, `attribute_ruler`, `ner` |
| **Components** | `tok2vec`, `morphologizer`, `parser`, `senter`, `attribute_ruler`, `ner` |
| **Vectors** | 0 keys, 0 unique vectors (0 dimensions) |
| **Sources** | [UD Japanese GSD v2.8](https://github.com/UniversalDependencies/UD_Japanese-GSD) (Omura, Mai; Miyao, Yusuke; Kanayama, Hiroshi; Matsuda, Hiroshi; Wakasa, Aya; Yamashita, Kayo; Asahara, Masayuki; Tanaka, Takaaki; Murawaki, Yugo; Matsumoto, Yuji; Mori, Shinsuke; Uematsu, Sumire; McDonald, Ryan; Nivre, Joakim; Zeman, Daniel)<br />[UD Japanese GSD v2.8 NER](https://github.com/megagonlabs/UD_Japanese-GSD) (Megagon Labs Tokyo) |
| **License** | `CC BY-SA 4.0` |
| **Author** | [Explosion](https://explosion.ai) |

### Label Scheme

<details>

<summary>View label scheme (66 labels for 4 components)</summary>

| Component | Labels |
| --- | --- |
| **`morphologizer`** | `POS=NOUN`, `POS=ADP`, `POS=VERB`, `POS=SCONJ`, `POS=AUX`, `POS=PUNCT`, `POS=PART`, `POS=DET`, `POS=NUM`, `POS=ADV`, `POS=PRON`, `POS=ADJ`, `POS=PROPN`, `POS=CCONJ`, `POS=SYM`, `POS=NOUN\|Polarity=Neg`, `POS=AUX\|Polarity=Neg`, `POS=INTJ`, `POS=SCONJ\|Polarity=Neg` |
| **`parser`** | `ROOT`, `acl`, `advcl`, `advmod`, `amod`, `aux`, `case`, `cc`, `ccomp`, `compound`, `cop`, `csubj`, `dep`, `det`, `dislocated`, `fixed`, `mark`, `nmod`, `nsubj`, `nummod`, `obj`, `obl`, `punct` |
| **`senter`** | `I`, `S` |
| **`ner`** | `CARDINAL`, `DATE`, `EVENT`, `FAC`, `GPE`, `LANGUAGE`, `LAW`, `LOC`, `MONEY`, `MOVEMENT`, `NORP`, `ORDINAL`, `ORG`, `PERCENT`, `PERSON`, `PET_NAME`, `PHONE`, `PRODUCT`, `QUANTITY`, `TIME`, `TITLE_AFFIX`, `WORK_OF_ART` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `TOKEN_ACC` | 99.69 |
| `TOKEN_P` | 97.65 |
| `TOKEN_R` | 97.90 |
| `TOKEN_F` | 97.77 |
| `POS_ACC` | 96.25 |
| `MORPH_ACC` | 0.40 |
| `MORPH_MICRO_P` | 34.01 |
| `MORPH_MICRO_R` | 98.04 |
| `MORPH_MICRO_F` | 50.51 |
| `SENTS_P` | 98.24 |
| `SENTS_R` | 98.82 |
| `SENTS_F` | 98.53 |
| `DEP_UAS` | 92.20 |
| `DEP_LAS` | 90.69 |
| `TAG_ACC` | 97.16 |
| `LEMMA_ACC` | 96.59 |
| `ENTS_P` | 67.67 |
| `ENTS_R` | 56.35 |
| `ENTS_F` | 61.50 |