# HEALTHDIAL

**A Multilingual and Multi-Parallel Spoken Dialogue Dataset for Knowledge-Grounded Information Seeking**

HEALTHDIAL is a large-scale, multilingual, multi-parallel spoken dialogue dataset for developing and evaluating retrieval-augmented generation (RAG)-based spoken dialogue systems.

- **6,000 information-seeking dialogues** (1,500 per language) across **Arabic, Chinese, English, and Spanish**.
- **163 hours of user speech** recorded by native speakers of diverse dialects, plus **208 hours of system speech**.
- **12,045 unique WHO knowledge snippets** (6,472 fully parallel across all four languages) grounding the dialogues.
- Speaker-level **demographic and sociolinguistic annotations** (gender, age, region of origin, primary language, education level).

The dataset is hosted on HuggingFace at [`cambridgeltl/HealthDial`](https://huggingface.co/datasets/cambridgeltl/HealthDial). This repository hosts the code released alongside the paper.

---

## What is in this repository

| Directory | Purpose |
|---|---|
| [`benchmark/`](./benchmark/) | Baseline code for the four benchmark tasks: ASR, TTS, retrieval-turn classification, knowledge retrieval (text-to-text and speech-to-text), and knowledge filtering. Includes the `HealthDialogueDatabase` loader and a HuggingFace download helper. |
| [`annotation_tool/`](./annotation_tool/) | Web platform used to collect the human-authored user utterances (Figure 8 in the paper). React client + Flask API + audio recording / Whisper transcription pipeline. |
| [`human_eval_tool/`](./human_eval_tool/) | TAM2-based human-evaluation platform (Figure 12). React participant interface + Flask backend + MongoDB + a dummy Socket.IO dialogue server for local testing. |

Each subdirectory has its own README with installation and usage instructions.

---

## Quick start

To reproduce the benchmark numbers in the paper:

```bash
git clone https://github.com/cambridgeltl/healthdial.git
cd healthdial/benchmark

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Authenticate once for HuggingFace if needed:
huggingface-cli login

# Pull the dataset (audio + dialogue JSONs):
python download_hf.py --output-dir data

# Run a benchmark, e.g. BM25 on English:
cd retrieval/evaluation
python run_retrieval.py --language eng --retriever bm25 --sample no
```

See [`benchmark/README.md`](./benchmark/README.md) for the full list of supported benchmarks and per-task instructions.

To collect your own dialogues with the same annotation interface, see [`annotation_tool/README.md`](./annotation_tool/README.md). To run a TAM2-style user study against your own dialogue system, see [`human_eval_tool/README.md`](./human_eval_tool/README.md).

---

## Citation

If you use HEALTHDIAL in your work, please cite:

```bibtex
@inproceedings{hu2025healthdial,
  title     = {{Dial HealthDial for Advice}: A Multilingual and Multi-Parallel Spoken Dialogue Dataset for Knowledge-Grounded Information Seeking},
  author    = {Hu, Songbo and Liu, Yinhong and Zhou, Ej and Razumovskaia, Evgeniia and Wang, Xiaobin and Fraser, Alexander and Vuli{\'c}, Ivan and Korhonen, Anna},
  year      = {2025},
}
```

---

## License & ethical use

- **Code** in this repository (all three sub-directories) is released under the [MIT License](./LICENSE).
- **Audio data** on HuggingFace is released under a separate, **non-commercial data use agreement** that prohibits voice cloning and re-identification of annotators. See the [dataset page](https://huggingface.co/datasets/cambridgeltl/HealthDial) for full terms.
- HEALTHDIAL is released as a **language resource for research**, *not* a clinical tool. The knowledge snippets come from the WHO website but have not been validated by healthcare professionals. Do not deploy this in a clinical setting without expert review.

---

## Acknowledgements

This work is supported by the Cambridge–LMU Strategic Partnership grant, the UKRI Frontier Research Grant EP/Y031350/1 EQUATE (Anna Korhonen), the Cambridge International Scholarship (Songbo Hu), and a Royal Society University Research Fellowship (Ivan Vulić, no. 221137).
