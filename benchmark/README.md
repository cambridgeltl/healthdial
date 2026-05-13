# HEALTHDIAL — Benchmark Code

Baseline code for the HEALTHDIAL benchmarks reported in [the paper](https://github.com/cambridgeltl/healthdial). This directory contains the data-loading utilities and reproduction scripts for the four task families:

- **ASR** (whisper, phi-4-multimodal)
- **TTS** (gpt-4o-mini-tts) + Mel-Cepstral Distortion evaluation
- **Retrieval-turn classification** (XLM-R, Llama-3.1-8B-Inst)
- **Knowledge retrieval** — text-to-text (bm25, sbert, openai, gte, nvembed, bge) and speech-to-text (clap, speecht5)
- **Knowledge filtering** (Llama-3.1, GPT-4 family)

The dataset itself (audio + dialogue JSONs + knowledge base) is hosted on HuggingFace at [`cambridgeltl/HealthDial`](https://huggingface.co/datasets/cambridgeltl/HealthDial). The annotation interface used to record the speech lives in [`../annotation_tool`](../annotation_tool/); the TAM2 human-evaluation platform lives in [`../human_eval_tool`](../human_eval_tool/).

---

## Layout

```
.
├── dataset/                 # Knowledge-base loader (HealthDialogueDatabase)
├── asr/                     # ASR experiments (whisper, phi-4-multimodal)
├── tts/                     # TTS generation + evaluation (gpt-4o-mini-tts)
├── classification/          # Retrieval-turn classification (XLM-R, Llama-3.1)
├── retrieval/               # Text-to-text + speech-to-text retrieval
│   ├── retrievers/          #   bm25, sbert, openai, gte, nvembed, bge, clap, speecht5
│   └── evaluation/          #   run_retrieval.py, run_speech_retrieval.py, metrics, util
├── filtering/               # LLM-based knowledge filtering
├── download_hf.py           # Pulls audio archives from HuggingFace
├── example.py / example.ipynb  # Minimal usage example
├── requirements.txt
└── LICENSE
```

---

## Installation

```bash
git clone https://github.com/cambridgeltl/healthdial.git
cd healthdial/benchmark

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Some experiments require optional dependencies — see the comments in `requirements.txt`. For the Phi-4-MM ASR experiment, install `asr/phi_requirement.txt` in addition.

---

## Downloading the data

The dataset is hosted on HuggingFace at [`cambridgeltl/HealthDial`](https://huggingface.co/datasets/cambridgeltl/HealthDial). Use the helper script:

```bash
# Authenticate once (only needed for gated/private repos):
huggingface-cli login

# Download all four languages into ./data/
python download_hf.py --output-dir data

# Or pick specific languages:
python download_hf.py --languages english arabic --output-dir data
```

After extraction, the layout should look like:

```
data/
├── who_database.json                # knowledge snippets (12,045 entries)
├── english/
│   ├── dialogue_list_final.json
│   ├── user_list_final.json
│   ├── audio/                       # user-recorded speech
│   └── system_audio/                # TTS-generated system speech
├── arabic/  …
├── chinese/ …
└── spanish/ …
```

---

## Quick start

```python
from dataset.database import HealthDialogueDatabase

db = HealthDialogueDatabase()  # loads data/who_database.json by default
print(db.support_language_list)                              # ['eng', 'ara', 'chn', 'esp']
print(len(db.get_all_snippet_list_for_language("eng")))      # number of English snippets
print(db.query_with_parallel_id_with("fact-sheets/detail/yaws::7")["eng"])
```

See `example.ipynb` for a longer walkthrough including dialogue iteration and parallel-snippet alignment.

---

## Running the benchmarks

All scripts assume the data is in `./data/` (override with the relevant flag where applicable). Set `OPENAI_API_KEY` in your environment before running anything that talks to OpenAI.

### 1. ASR — Word/Character Error Rate (Table 2, Table 6)

```bash
cd asr

# Inference (writes <model>_asr_result fields back into the JSON)
python asr_inference.py --folder ../data/english --model_name whisper --stage inference
python asr_inference.py --folder ../data/english --model_name phi     --stage inference

# Evaluation (WER, CER)
python asr_inference.py --folder ../data/english --model_name whisper --stage evaluation
```

Supported `--model_name` values: `whisper`, `phi`, `gpt4omini`.

### 2. TTS — MCD + CER-via-ASR (Table 2, Table 6)

```bash
cd tts

# Generate audio for the test split
python tts_generation.py --folder ../data/english

# Transcribe generated audio with Whisper-large-v2
python create_transcriptions.py --language english

# Compute Mel Cepstral Distortion
python tts_evaluation.py --language english
```

### 3. Retrieval-turn classification (Table 2, Table 8)

```bash
cd classification

# Fine-tune XLM-R on the training split
python run_classification.py --language eng

# Few-shot classification with Llama-3.1-8B-Instruct
python run_classification_llama.py --language eng --full_dataset True
```

### 4. Text-to-text knowledge retrieval (Table 2, Table 7)

```bash
cd retrieval/evaluation

# BM25
python run_retrieval.py --language eng --retriever bm25 --sample no

# Sentence-Transformers (MiniLM-L12-v2)
python run_retrieval.py --language eng --retriever sbert --sample no

# OpenAI text-embedding-3-large
python run_retrieval.py --language eng --retriever openai --embedding_model text-embedding-3-large --sample no

# Other text encoders
python run_retrieval.py --language eng --retriever gte     --sample no
python run_retrieval.py --language eng --retriever nvembed --sample no
```

Results are written to `retrieval/results/outputs/`.

### 5. Speech-to-text retrieval (Table 2, Table 7)

```bash
cd retrieval/evaluation

# CLAP
python run_speech_retrieval.py --language eng --retriever clap     --audio_root ../../data --sample no

# SpeechT5
python run_speech_retrieval.py --language eng --retriever speecht5 --audio_root ../../data --sample no
```

You can also point `HEALTHDIAL_AUDIO_ROOT` at a non-default location.

### 6. Knowledge filtering (Table 2, Table 3, Table 8, Figure 3)

```bash
cd filtering

python knowledge_filtering_huggingface.py \
    --language eng \
    --top_k 5 \
    --num_icl_example 10 \
    --full_dataset True
```

---

For citation, license, and ethical-use information, see the [top-level README](../README.md) and [LICENSE](../LICENSE).
