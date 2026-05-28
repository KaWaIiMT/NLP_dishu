
# Research Paper Plan: EarthScript vs. Natural Language

This document outlines the plan for a research paper analyzing EarthScript, a visual language, against natural languages using linguistic, classic NLP, and Transformer-based approaches.

## 1. Project Goals

- Analyze the linguistic nature of EarthScript.
- Compare EarthScript's linguistic properties with natural languages (Classical Chinese, Modern Chinese, 16-language Wiki).
- Investigate the potential of EarthScript as a universal language.
- Apply a multi-faceted analytical approach: linguistic perspectives, classic NLP, and LLM/Transformer models.

## 2. Datasets

- **EarthScript Datasets:**
  - Annotated JSON files (provided by user):
    - Base/Sentence annotations
    - Colloquial version annotations
  - Visual data for EarthScript symbols.
- **Natural Language Corpora:**
  - Classical Chinese: Siku Quanshu database
  - Modern Chinese: Famous literary works, news corpora, novels
  - 16-language Wiki sentence subset (30k sentences per language)

## 3. Annotation Format (EarthScript JSON)

- **Core Textual Annotations:**
  - `literal_gloss`: Direct word/phrase translation.
  - `free_translation`: Fluent group translation.
  - `pragmatic_meaning`: Contextual intended meaning.
  - `event_description`: Event/scenario summary of the group.
  - `context_note`: Research notes, ambiguities, justifications.
- **Single-Value Annotations:**
  - `semantic_role_core`: Core semantic role (Agent, Patient, Experiencer, etc.).
  - `dependency_to_head`: Dependency relation to the head element.
  - `discourse_relation`: Discourse relation with the preceding segment.
  - `primary_speech_act`: Primary speech act.
  - `reference_type`: Type of reference.
- **Multi-Value Annotations:**
  - `pos_like_category`: Part-of-speech like categories.
  - `morphological_like_features`: Morphological-like features.
  - `semantic_primitives`: Semantic primitives.
  - `visual_cues`: Visual cues.
  - `communicative_functions`: Communicative functions.
  - `sources_of_ambiguity`: Sources of ambiguity.
- **Multi-Text Annotations:**
  - `wsd_candidates`: Word Sense Disambiguation candidates.
  - `possible_translations`: Various natural language translations.
  - `frame_or_metaphor_mapping`: Frame or metaphor mapping.
  - `collocational_associations`: Associated words.
  - `cross_linguistic_equivalents`: Cross-linguistic equivalents.
- **Scale Annotations:**
  - `cognitive_linguistic_metrics`: Cognitive-linguistic metrics.
  - `syntactic_semantic_fitness`: Syntactic-semantic fitness.
  - `confidence_consistency_evaluation`: Confidence and consistency evaluation.

## 4. Methodology

### 4.1. Corpus Preparation

- **Sampling:** Fixed sentence count (e.g., 30k) per language/corpus.
- **Tokenization:** Composite tokenization (Literal Gloss + Semantic Role).
- **Data Cleaning & Preprocessing:** Standard NLP preprocessing.

### 4.2. Linguistic & Classic NLP Analysis

- **Lexical Analysis:** Word frequency (Zipf's Law), Information Entropy.
- **Syntactic Analysis:** Dependency Parsing, Semantic Role Labeling.
- **Stylistic Analysis:** Comparative analysis of features like sentence length, word choice, complexity.

### 4.3. LLM & Transformer-based Analysis

- **LLM (Gemini API):**
  - Stylistic classification of corpora.
  - Translation consistency evaluation.
  - Text generation quality assessment.
- **Small Transformer Model (Optional):**
  - Objective: Translation Language Modeling (TLM).
  - Training: On EarthScript-to-natural language pairs.
  - Analysis: Attention map visualization and interpretation (syntactic, semantic, co-occurrence, style dimensions).

## 5. Research Paper Structure

1.  **Introduction:**
    - Background: Visual languages, natural language analysis.
    - Problem Statement: Linguistic nature of EarthScript vs. natural languages.
    - Research Questions.
    - Significance of the study.
    - Paper structure overview.
2.  **Related Work:**
    - Visual language research.
    - Computational linguistics & stylistics.
    - NLP methods for language comparison.
    - Transformer and LLM applications in linguistics.
3.  **Datasets and Annotation:**
    - Description of all corpora.
    - Detailed explanation of the EarthScript annotation format.
    - Corpus sampling strategy.
    - Tokenization method.
4.  **Macro-level Analysis (Classic NLP & Corpus Statistics):**
    - Zipf's Law analysis.
    - Information Entropy.
    - Corpus length and complexity metrics.
    - Preliminary stylistic comparisons.
5.  **Micro-level Analysis (Detailed Linguistic & LLM-based):**
    - In-depth analysis of semantic roles, dependencies, speech acts.
    - LLM-based stylistic classification and translation evaluation.
    - (Optional) Transformer model analysis: attention maps, TLM performance.
6.  **Discussion:**
    - Synthesis of findings from macro and micro analyses.
    - Comparison of EarthScript's linguistic properties with natural languages.
    - Implications for EarthScript's potential as a universal language.
    - Limitations of the study.
7.  **Conclusion:**
    - Summary of key findings.
    - Future research directions.

## 6. Tasks

- **Task 1: Prepare EarthScript and Natural Language Corpora**
  - Description: Download, organize, and preprocess all specified datasets. Ensure correct sampling and initial cleaning.
- **Task 2: Implement EarthScript Annotation Schema**
  - Description: Adapt or implement tools/scripts to work with the provided EarthScript JSON annotation format. Focus on parsing and extracting relevant fields.
- **Task 3: Develop Classic NLP Analysis Pipeline**
  - Description: Implement scripts for Zipf's Law, Information Entropy, Dependency Parsing, and Semantic Role Labeling. Apply to all corpora.
- **Task 4: Configure and Run LLM (Gemini API) Analysis**
  - Description: Set up API access, design prompts for stylistic classification, translation consistency, and text generation quality. Process all corpora.
- **Task 5: (Optional) Develop and Train Small Transformer Model**
  - Description: Prepare data for TLM, implement a small Transformer, train it, and analyze attention maps.
- **Task 6: Synthesize Analysis Results and Draft Paper Sections**
  - Description: Combine findings from all analytical methods. Draft sections 4, 5, and 6 of the research paper.
- **Task 7: Refine Paper and Finalize**
  - Description: Review and edit the entire paper, ensuring consistency, clarity, and adherence to academic standards. Finalize all sections including Introduction, Related Work, and Conclusion.

## 7. Implementation Notes

- **Programming Language:** Python (preferred).
- **Libraries:** NLTK, spaCy, Transformers, Scikit-learn, Pandas, NumPy, Gemini API client.
- **LLM Choice:** Gemini API (primary), with an option for training a small Transformer if necessary.
- **Computing Resources:** Local machine or cloud (4090 available, but Gemini API preferred for simplicity).
- **Collaboration:** Output all discussion and findings into the `research_plan.md` file.
