import os
import soundfile as sf
import time
import io
import torch
import transformers

from typing import Any
from openai import OpenAI
from tqdm import tqdm

from asr_utils import MODEL_SHORT_TO_NAME


def run_inference(
    data: list[dict[str, Any]], model_name: str, foldername: str
) -> list[dict[str, Any]]:
    if model_name in ["whisper", "gpt4omini"]:
        updated_data = openai_inference(data, model_name, foldername)
    elif model_name == "phi":
        updated_data = huggingface_inference(data, model_name, foldername)
    else:
        raise ValueError("currently only suporting openai models")
    return updated_data


def openai_inference(
    data: list[dict[str, Any]], model_name: str, foldername: str
) -> list[dict[str, Any]]:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    for example in tqdm(data):
        for utterance in example["utterance"]:
            if utterance["role"] == "user":
                audio_file = utterance["audio_name"]
                audio_file = open(os.path.join(foldername, "audio", audio_file), "rb")
                transcription = client.audio.transcriptions.create(
                    model=MODEL_SHORT_TO_NAME[model_name], file=audio_file
                )
                utterance[f"{model_name}_asr_result"] = transcription.text
    return data


def huggingface_inference(
    data: list[dict[str, Any]], model_name: str, foldername: str
) -> list[dict[str, Any]]:
    model_path = MODEL_SHORT_TO_NAME[model_name]
    # Load model and processor
    processor = transformers.AutoProcessor.from_pretrained(
        model_path, trust_remote_code=True
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True,
        # if you do not use Ampere or later GPUs, change attention to "eager"
        _attn_implementation="flash_attention_2",
    )

    # Load generation config
    generation_config = transformers.GenerationConfig.from_pretrained(model_path)

    # Define prompt structure
    user_prompt = "<|user|>"
    assistant_prompt = "<|assistant|>"
    prompt_suffix = "<|end|>"

    speech_prompt = "Transcribe the audio to text complrehensively."
    prompt = f"{user_prompt}<|audio_1|>{speech_prompt}{prompt_suffix}{assistant_prompt}"

    for example in tqdm(data):
        for utterance in example["utterance"]:
            if utterance["role"] == "user":
                audio_file = utterance["audio_name"]
                audio, samplerate = sf.read(
                    os.path.join(foldername, "audio", audio_file)
                )
                inputs = processor(
                    text=prompt, audios=[(audio, samplerate)], return_tensors="pt"
                ).to("cuda:0")
                with torch.no_grad():
                    generate_ids = model.generate(
                        **inputs,
                        max_new_tokens=1000,
                        generation_config=generation_config,
                    )
                    generate_ids = generate_ids[:, inputs["input_ids"].shape[1] :]
                    response = processor.batch_decode(
                        generate_ids,
                        skip_special_tokens=True,
                        clean_up_tokenization_spaces=False,
                    )[0]
                utterance[f"{model_name}_asr_result"] = response
    return data
