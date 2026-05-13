import os
import sys
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from tqdm import tqdm
from dataset.database import HealthDialogueDatabase
from metrics import compute_metrics_for_turn
import argparse
from util import *


# Map retriever name -> (module path, class name). Imports are lazy so that
# users only need to install the dependencies of the retriever they actually use.
RETRIEVER_REGISTRY = {
    "bm25":    ("retrievers.bm25",    "BM25Retriever"),
    "sbert":   ("retrievers.sbert",   "SBERTRetriever"),
    "openai":  ("retrievers.openai",  "OpenAIRetriever"),
    "nvembed": ("retrievers.nvembed", "NVEmbedRetriever"),
    "gte":     ("retrievers.gte",     "GTEEmbedRetriever"),
    "bge":     ("retrievers.bge",     "BGEEmbedRetriever"),
}


def load_retriever(name):
    if name not in RETRIEVER_REGISTRY:
        raise ValueError(
            f"Retriever '{name}' not implemented. Choose from: {sorted(RETRIEVER_REGISTRY)}"
        )
    module_path, class_name = RETRIEVER_REGISTRY[name]
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

K = 10

# ---------------------------
# Main Retrieval + Evaluation
# ---------------------------

def run_retrieval(language: str ,RetrieverClass, retriever_name):
    print(f"🌍 Running retrieval for language: {language}")

    # Load WHO knowledge base
    db = HealthDialogueDatabase(db_path="../../data/who_database.json", load_parallel_data=True)
    snippets = db.get_all_snippet_list_for_language(language)

    # Build corpus: topic + title + content
    corpus = [
        f"{s['data']['topic']} {s['data']['title']} {s['data']['content']}"
        for s in snippets
        if "data" in s and all(k in s["data"] for k in ["topic", "title", "content"])
    ]

    if retriever_name == "openai":
        retriever = RetrieverClass(corpus, language, embedding_model=args.embedding_model)
    else:
        retriever = RetrieverClass(corpus, language)

    retriever.index()

    # tokenized_corpus = [tokenize(doc, language) for doc in corpus]
    # bm25 = BM25Okapi(tokenized_corpus)

    id_to_snippet = {
        f"{s['data']['topic']} {s['data']['title']} {s['data']['content']}": s
        for s in snippets
        if "data" in s and all(k in s["data"] for k in ["topic", "title", "content"])
    }


    # Load language-specific user dialogue file
    lang_folder = language_map.get(language, language)
    if(args.sample == "yes"):
        input_path = f"../../data/{lang_folder}_sample/processed_result.json"
    else:
        input_path = f"../../data/{lang_folder}/dialogue_list_final.json"
    dataset = load_dataset(input_path)

    # if run on the whole dataset (1500 instances), the first 500 is the training set and the rest is the test set
    # so we will need to use the last 1000 instances for evaluation
    if args.sample == "no":
        dataset = dataset[500:]

    results = []

    for dialogue in tqdm(dataset, desc=f"Retrieval + Eval [{language}]"):
        utterances = dialogue["utterance"]
        task_id = dialogue.get("task_id")
        dialogue_result = {
            "task_id": task_id,
            "turns": []
        }

        for i in range(1, len(utterances), 2):  # user turns
            context = utterances[0:i+1]

            dialogue_context = []
            for turn in context:
                if turn["role"] == "user":
                    dialogue_context.append(turn.get("annotated_transcription", ""))
                elif turn["role"] == "assistant":
                    dialogue_context.append(turn.get("generated_text", ""))
            query = " ".join(dialogue_context)


            retrieved = retriever.retrieve(query, top_k=K)

            top_snippets = [r[0] for r in retrieved]

            pred_ids = [
                id_to_snippet[s]["unique_identifier"] or id_to_snippet[s].get("url")
                for s in top_snippets if s in id_to_snippet
            ]

            if i + 1 >= len(utterances): continue
            gold_utt = utterances[i + 1]
            gold_snippets = gold_utt.get("snippet", [])
            # if in_knowledge is false, skip this turn
            if gold_utt.get("in_knowledge", True) == False:
                continue
            # if there are no snippets, skip this turn
            if not gold_snippets:
                continue

            gold_ids = {
                s.get("unique_identifier") or s.get("url")
                for s in gold_snippets
            }

            # out_of_knowledge = gold_utt.get("out_of_knowledge", False)

            metrics = compute_metrics_for_turn(gold_ids, pred_ids)

            dialogue_result["turns"].append({
                "turn_index": i + 1,
                "query": query,
                "gold_ids": list(gold_ids),
                "predicted_ids": list(pred_ids),
                "metrics": metrics
            })

        results.append({
            "task_id": task_id,
            "retrievals": dialogue_result
        })

    # Save query cache for OpenAI retriever
    if retriever_name == "openai":
        retriever.save_cache()

    # Save output
    os.makedirs("../results/outputs/", exist_ok=True)

    # Safe model name for filenames (optional: only add if it's OpenAI retriever)
    model_tag = ""
    if retriever_name == "openai":
        model_tag = f"_{args.embedding_model.replace('-', '_')}"

    output_base = f"../results/outputs/{retriever_name}{model_tag}"

    # save the full results if not sampled
    if args.sample == "no":
        save_results(results, f"{output_base}_results_{language}.json")
        print(f"✅ Saved {retriever_name} retrieval results for '{language}' with model '{model_tag}'.")
    
        # save the summary results
        summary = aggregate_metrics(results)
        save_results(summary, f"{output_base}_eval_summary_{language}.json")

    if args.sample == "yes":
        save_results(results, f"{output_base}_sample_results_{language}.json")
        print(f"✅ Saved {retriever_name} retrieval results for '{language}' with model '{model_tag}' (sampled).")

        # save the summary results
        summary = aggregate_metrics(results)
        save_results(summary, f"{output_base}_sample_eval_summary_{language}.json")

    print("📊 Aggregated Metrics:")
    for k, v in summary.items():
        print(f"{k}: {100 * v:.4f}")


# ---------------------------
# CLI Entry Point
# ---------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default="eng", help="Language code (e.g. eng, ara, spa)")
    parser.add_argument("--retriever", type=str, default="bm25",
                        choices=sorted(RETRIEVER_REGISTRY), help="Retrieval method")
    parser.add_argument("--embedding_model", type=str, default="text-embedding-3-small",
                        help="OpenAI embedding model ID")
    parser.add_argument("--sample", type=str, default="yes",
                        help="Whether to use a sample of the dataset (yes/no)")
    args = parser.parse_args()

    retriever_cls = load_retriever(args.retriever)
    run_retrieval(language=args.language, RetrieverClass=retriever_cls, retriever_name=args.retriever)