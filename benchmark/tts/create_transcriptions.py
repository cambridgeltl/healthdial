from datasets import Audio, load_dataset, Dataset
import argparse

import json
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import torch
from evaluate import load
import os

parser = argparse.ArgumentParser(description="Command line arguments")
parser.add_argument(
    "-l", "--language", type=str, help="Folder where the data is stored"
)
args = parser.parse_args()

language_name = args.language

language_dir = f"data/{language_name}/generated_audio"
filenames = [os.path.join(language_dir, file) for file in os.listdir(f"data/{language_name}/generated_audio")]

dataset = Dataset.from_dict({"audio": filenames}).cast_column("audio", Audio(sampling_rate=16000))

processor = WhisperProcessor.from_pretrained("openai/whisper-large-v2")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v2").to("cuda")
forced_decoder_ids = processor.get_decoder_prompt_ids(language=language_name, task="transcribe")


def map_to_pred(batch):
    audio = batch["audio"]
    input_features = processor(audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt").input_features

    with torch.no_grad():
        predicted_ids = model.generate(input_features.to("cuda"), forced_decoder_ids=forced_decoder_ids)[0]
    transcription = processor.decode(predicted_ids, skip_special_tokens=True)
    batch["prediction"] = processor.tokenizer._normalize(transcription)
    return batch


result = dataset.map(map_to_pred)
predictions = {filename.split("/")[-1]:prediction for filename, prediction in zip(filenames, list(result["prediction"]))}
print(predictions)

with open(os.path.join(language_dir, "predictions_for_generated_audio.json"), "w", encoding="utf-8") as f:
    json.dump(predictions, f, indent=4, ensure_ascii = False)
