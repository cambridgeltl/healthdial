import os
import json
from typing import Any

MODEL_SHORT_TO_NAME = {
    "phi": "microsoft/Phi-4-multimodal-instruct",
    "whisper": "whisper-1",
    "gpt4omini": "gpt-4o-mini-transcribe",
}


def load_data(folder_name: str) -> list[dict[str, Any]]:
    file_name = os.path.join(folder_name, "dialogue_list_final.json")
    with open(file_name, encoding="utf-8") as f:
        data = json.load(f)
    data = data[500:]
    return data
