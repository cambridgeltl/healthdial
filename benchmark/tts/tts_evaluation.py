import json
import argparse
from pymcd.mcd import Calculate_MCD
import os
from mel_cepstral_distance import compare_audio_files
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Command line arguments")
parser.add_argument(
    "-l", "--language", type=str, help="Folder where the data is stored"
)
args = parser.parse_args()


language_name = args.language


filename = os.path.join("data", language_name, "both_asr_result.json")
with open(filename, encoding='utf-8', ) as f:
    both_asrs = json.load(f)

results = []
audio_names = []
for dialogue in tqdm(both_asrs):
    for utterance in dialogue["utterance"]:
        if utterance["role"] == "user":
            audio_name = utterance["audio_name"]
            filename = os.path.join("data", language_name, "audio", audio_name)
            generated_filename = os.path.join("data", language_name, "generated_audio", audio_name)
            assert os.path.isfile(filename)
            assert os.path.isfile(generated_filename)
            audio_names.append(audio_name)
            # mcd, penalty = compare_audio_files(filename, generated_filename)
            # results.append((mcd, penalty))
            # print(mcd)

for audio_name in tqdm(audio_names):
    filename = os.path.join("data", language_name, "audio", audio_name)
    generated_filename = os.path.join("data", language_name, "generated_audio", audio_name)
    mcd, penalty = compare_audio_files(filename, generated_filename)
    results.append((mcd, penalty))

results_mcd = [tuple_mcd[0] for tuple_mcd in results]
results_penalty = [tuple_mcd[1] for tuple_mcd in results]
print(language_name)
print(np.mean(results_mcd))
print(np.mean(results_penalty))