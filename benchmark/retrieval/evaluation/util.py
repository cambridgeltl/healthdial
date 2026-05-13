import json
from collections import defaultdict


language_map = {
    "eng": "english",
    "ara": "arabic",
    "esp": "spanish",
    "chn": "chinese"
}


# ---------------------------
# Helper Functions
# ---------------------------

def load_dataset(path):
    with open(path, 'r') as f:
        return json.load(f)




def save_results(results, output_path):
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


def aggregate_metrics(full_results):
    agg = defaultdict(list)

    for dialogue in full_results:
        for turn in dialogue['retrievals']["turns"]:
            metrics = turn["metrics"]
            for key, value in metrics.items():
                agg[key].append(value)

    summary = {}
    for key, values in agg.items():
        summary[key] = sum(values) / len(values) if values else 0.0

    return summary

