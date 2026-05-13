import json
from collections import defaultdict
from datasets import Dataset, DatasetDict

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


def load_data(language: str):
    print(f"🌍 Loading dataset for language: {language}")

    # Load language-specific user dialogue file
    lang_folder = language_map.get(language, language)

    input_path = f"../data/{lang_folder}/dialogue_list_final.json"

    full_dataset = load_dataset(input_path)

    train_dialogues = full_dataset[:400]
    val_dialogues = full_dataset[400:500]
    test_dialogues = full_dataset[500:1500]

    def process(dialogues):
        data = []
        for dialogue in dialogues:
            utterances = dialogue["utterance"]
            if not utterances:
                continue

            for i in range(len(utterances)):
                if utterances[i]["role"] != "assistant":
                    continue

                # First assistant-only turn
                if i == 0:
                    data.append({
                        "text": "",
                        "need_retrieval": utterances[i].get("need_retrieval", False)
                    })

                # Second assistant turn — context is (u1)
                elif i == 2 and utterances[i-1]["role"] == "user":
                    a1 = utterances[i-2]
                    u1 = utterances[i-1]
                    a1_text = a1.get("generated_text", "").strip()
                    u1_text = u1.get("annotated_transcription", "").strip()
                    data.append({
                        "text": f"system: {a1_text} user: {u1_text}",
                        "need_retrieval": utterances[i].get("need_retrieval", False)
                    })

                # Third and later assistant turns — context is (u1, a1, u2)
                elif i >= 4 and utterances[i-3]["role"] == "user" and utterances[i-2]["role"] == "assistant" and utterances[i-1]["role"] == "user":
                    u1 = utterances[i-3]
                    a1 = utterances[i-2]
                    u2 = utterances[i-1]

                    u1_text = u1.get("annotated_transcription", "").strip()
                    a1_text = a1.get("generated_text", "").strip()
                    u2_text = u2.get("annotated_transcription", "").strip()

                    data.append({
                        "text": f"user: {u1_text} system: {a1_text} user: {u2_text}",
                        "need_retrieval": utterances[i].get("need_retrieval", False)
                    })

        return Dataset.from_list(data)

    # Process each split independently
    return DatasetDict({
        "train": process(train_dialogues),
        "validation": process(val_dialogues),
        "test": process(test_dialogues)
    })

