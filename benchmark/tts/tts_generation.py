import argparse
import os
import json
import openai
from openai import OpenAI
from tqdm import tqdm



def main(args):
    os.makedirs(os.path.join(args.folder, "generated_audio"), exist_ok=True)
    with open(
        os.path.join(args.folder, "dialogue_list_final.json"), encoding="utf-8"
    ) as f:
        data = json.load(f)
    with open(os.path.join(args.folder, "user_list_final.json"), encoding="utf-8") as f:
        users_profiles = json.load(f)

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    user_profile_dict = {}
    for user in users_profiles:
        user_profile_dict[user['id']] = {key: value for key, value in user.items() if key!='id'}
    
    for dialogue in tqdm(data[500:]):
        for utterance in dialogue["utterance"]:
            if utterance["role"] == "user":
                user_name = utterance["audio_name"].split("_")[0]
                speech_file_path = os.path.join(args.folder, "generated_audio", utterance["audio_name"])
                user_profile = user_profile_dict[user_name]
                education_level = user_profile_dict[user_name]['education_level'].replace('-', ' ')
                instructions = f"Speak as a {user_profile['age_group']} year old native speaker of {user_profile['primary_language']} who was born in {user_profile['place_of_origin']} and lives in {user_profile['region_of_residence']}. The speaker is educated to {education_level} level."
                with client.audio.speech.with_streaming_response.create(
                    model="gpt-4o-mini-tts",
                    voice="coral",
                    input=utterance["annotated_transcription"],
                    instructions=instructions,
                    response_format="wav",
                ) as response:
                    response.stream_to_file(speech_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command line arguments")
    parser.add_argument(
        "-f", "--folder", type=str, help="Folder where the data is stored"
    )
    parser.add_argument(
        "-m", "--model_name", type=str, help="The model used for inference/evaluation"
    )
    parser.add_argument(
        "-s",
        "--stage",
        type=str,
        help="The stage we're at; Options: [inference, evaluation]",
    )
    args = parser.parse_args()

    main(args)
