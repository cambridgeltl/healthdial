import argparse
from util import load_data
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm
from vllm import LLM, SamplingParams

def format_example(example, include_output=True):
    prompt = f"Text: {example['text']}\nNeeds Retrieval? "
    if include_output:
        label_str = "Yes" if example["need_retrieval"] else "No"
        prompt += label_str
    return prompt

def build_few_shot_prompt(train_dataset, k=10):
    system_instruction = (
        "You are a helpful AI assistant. Your task is to determine whether a given utterance needs retrieval from an external knowledge source.\n"
        "The user is interacting in a multilingual spoken dialogue system. If the utterance expresses uncertainty, asks for factual knowledge, "
        "mentions symptoms or medical conditions, or refers to something beyond the assistant's built-in capabilities, then it *needs retrieval*.\n"
        "Note: Around 75% of utterances *do* need retrieval, so be conservative when saying 'No'.\n"
        "Label each example as 'Yes' or 'No' based on whether retrieval is needed.\n\n"
    )
    prompt = system_instruction
    for i in range(k):
        prompt += format_example(train_dataset[i]) + "\n\n"
    return prompt

def infer(model, tokenizer, prompt, max_new_tokens=10):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        pad_token_id=tokenizer.eos_token_id
    )
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded[len(prompt):].strip()

def infer_batch(model, tokenizer, prompts, max_new_tokens=10):
    # Tokenize batch with padding
    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        pad_token_id=tokenizer.eos_token_id
    )

    decoded_outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    
    # Remove the original prompt from the output to isolate the model's answer
    return [
        decoded[len(prompt):].strip()
        for decoded, prompt in zip(decoded_outputs, prompts)
    ]

def normalize_prediction(pred):
    pred = pred.lower()
    if "yes" in pred or "true" in pred:
        return True
    elif "no" in pred or "false" in pred:
        return False
    return True  # unclear case

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default="eng", help="Language code (e.g. eng, ara, esp)")
    parser.add_argument("--full_dataset", type=bool, default=False, help="Use full dataset for training")
    args = parser.parse_args()

    datasets = load_data(language=args.language)

    print("🌍 Dataset loaded:", datasets)

    # Build 10-shot prompt from training set
    few_shot_prompt = build_few_shot_prompt(datasets["train"], k=10)

    # Load LLaMA model
    model_name = "meta-llama/Llama-3.1-8B-Instruct"  # change to your model path if local
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to("cuda" if torch.cuda.is_available() else "cpu")

    # Evaluate on test set
    correct = 0
    total = 0

    # select a subset of the test set for evaluation
    if args.full_dataset:
        test_samples = datasets["test"]
    else:
        # Select a smaller subset for quick evaluation
        # Adjust the range as needed
        test_samples = datasets["test"].select(range(30)) 

    print("\n🔍 Starting Evaluation...\n")
    # for example in tqdm(datasets["test"]):
    for example in tqdm(test_samples):
        full_prompt = few_shot_prompt + format_example(example, include_output=False)
        prediction = infer(model, tokenizer, full_prompt)
        predicted_label = normalize_prediction(prediction)
        print(f"Predicted: {predicted_label}, Actual: {example['need_retrieval']}")

        if predicted_label is None:
            continue  # skip ambiguous answers

        if predicted_label == example["need_retrieval"]:
            correct += 1
        total += 1

    accuracy = correct / total if total > 0 else 0
    print(f"\n✅ Evaluation Complete. Accuracy: {accuracy:.4f} ({correct}/{total})")



if __name__ == "__main__":
    main()