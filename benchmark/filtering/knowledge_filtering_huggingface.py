import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm
import random
import os
import json
import re

class HealthDialogueDatabase:

    def __init__(self, db_path, load_parallel_data = True):

        self.db_path = db_path


        # Load database data
        self.language_snippet_list_dic, self.support_language_list, self.unique_id_snippet_dic, self.parallel_id_snippet_dic = self._load_data(load_parallel_data = load_parallel_data)

    def _load_data(self, load_parallel_data = True):

        language_snippet_list_dic = {}

        with open(self.db_path, "r") as f:
            raw_data = json.load(f)

        if load_parallel_data:
            raw_data = list(filter(lambda x : x["parallel_data"], raw_data))

        for item in raw_data:
            this_snippet_list = language_snippet_list_dic.get(item["language"].lower(), [])
            this_snippet_list.append(item)
            language_snippet_list_dic[item["language"].lower()] = this_snippet_list

        if load_parallel_data:
            lengths = [len(lst) for lst in language_snippet_list_dic.values()]
            assert all(length == lengths[0] for length in lengths), "Not all parallel lists have the same length"

        support_language_list = list(language_snippet_list_dic.keys())

        unique_id_snippet_dic = {}
        parallel_id_snippet_dic = {}
        for language in support_language_list:
            snippet_list =  language_snippet_list_dic[language]
            for snippet in snippet_list:
                unique_id = snippet["unique_identifier"]
                assert unique_id not in unique_id_snippet_dic
                unique_id_snippet_dic[unique_id] = snippet

                if snippet["parallel_data"]:
                    assert snippet["parallel_identifier"]

                    this_language_snippet_dic = parallel_id_snippet_dic.get(snippet["parallel_identifier"], {})
                    this_language_snippet_dic[language] = snippet
                    parallel_id_snippet_dic[snippet["parallel_identifier"]] = this_language_snippet_dic

        for parallel_id, language_snippet_dic in parallel_id_snippet_dic.items():
            for language in support_language_list:
                assert language in language_snippet_dic

        return language_snippet_list_dic, support_language_list, unique_id_snippet_dic, parallel_id_snippet_dic



    def get_all_snippet_list_for_language(self, language):
        language = language.lower()
        assert language in self.support_language_list
        return self.language_snippet_list_dic[language]

    def query_with_parallel_id_with(self, parallel_id):
        assert parallel_id in self.parallel_id_snippet_dic
        return self.parallel_id_snippet_dic[parallel_id]

    def query_with_unique_id_with(self, unique_id):
        assert unique_id in self.unique_id_snippet_dic
        return self.unique_id_snippet_dic[unique_id]



def save_to_json_file(data, filename):
    json_string = json.dumps(data, indent=4, ensure_ascii=False)

    with open(filename, 'w') as file:
        file.write(json_string)


def read_json_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    return data


instruction_prompt = '''
You are a careful and precise AI assistant whose task is to select the minimal set of relevant information snippets (if any) to answer a user's query.

Task:

You are given a dialogue history between a user and an AI healthcare assistant. The user asks a question or expresses a concern related to health, which may or may not be answerable using the provided information snippets sourced from the WHO website.

You are also given a set of candidate snippets, each containing an `id`, `topic`, `title`, and `content`.

Your goal is to:

- Select the smallest complete set of snippet IDs that would allow an assistant to properly and accurately answer the user’s query.
- Include only those snippets that are **strictly necessary and directly relevant**.
- If no snippet is relevant, return an empty list `[]`.

Important:

- Do **not** include snippets that are only weakly or tangentially related.
- Do **not** modify or rewrite snippet content.
- Do **not** include explanations or any text outside the final answer.

Format:

Return only a **JSON array** of selected snippet IDs:

Example of a valid response:

["id1", "id2"]

Or, if no relevant snippets:

[]

'''


def example_to_prompt(example, index, top_k, snippet_database, give_answer=True):
    query = example["query"]

    # Get full snippet dicts for gold and predicted
    gold_snippet_list = get_clean_snippet_list_from_id(example["gold_ids"], snippet_database)
    candidate_snippet_list = get_clean_snippet_list_from_id(example["predicted_ids"][:top_k], snippet_database)

    # Get gold snippet IDs
    gold_ids = set(example["gold_ids"])

    # Determine which predicted snippets are correct (in gold)
    answer_snippet_id_list = [
        snippet["id"] for snippet in candidate_snippet_list if snippet["id"] in gold_ids
    ]

    # Build prompt string
    if give_answer:
        prompt_st = f"Example {index}\n\n"
    else:
        prompt_st = f"Now for the actual task:\n\n"

    prompt_st += f"Dialogue history:\n{query.strip()}\n\n"
    prompt_st += "Candidate snippets:\n"
    for snippet in candidate_snippet_list:
        prompt_st += (
            f"- ID: {snippet['id']}\n"
            f"  Title: {snippet['title'].strip()}\n"
            f"  Content: {snippet['content'].strip()}\n\n"
        )

    if give_answer:
        prompt_st += f"Answer:\n{json.dumps(answer_snippet_id_list)}\n"
    else:
        prompt_st += "Answer: (Return only the JSON array of selected snippet IDs)"

    return prompt_st


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


def get_clean_snippet(snippet):
    result = {}
    result["id"] = snippet["unique_identifier"]
    result["topic"] = snippet["data"]["topic"]
    result["title"] = snippet["data"]["title"]
    result["content"] = snippet["data"]["content"]
    return result

def get_clean_snippet_list_from_id(snippet_id_list, snippet_database):
    result = list(map(lambda x : get_clean_snippet(snippet_database.query_with_unique_id_with(x)), snippet_id_list))
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default="eng", help="Language code (e.g. eng, ara, chn, esp)")
    parser.add_argument("--full_dataset", type=bool, default=False, help="Use full dataset for training")
    parser.add_argument("--top_k", type=int, default=False, help="top_k")
    parser.add_argument("--num_icl_example", type=int, default=False, help="num_icl_example")
    args = parser.parse_args()

    dial_list = None
    assert args.language in ["ara", "eng", "chn", "esp"]
    if args.language == "eng":
        dial_list = read_json_from_file("../data/english/dialogue_list_final.json")
        result = read_json_from_file("./train_results_eng.json") + read_json_from_file("./results_eng.json")
    elif args.language == "chn":
        dial_list = read_json_from_file("../data/chinese/dialogue_list_final.json")
        result = read_json_from_file("./train_results_chn.json") + read_json_from_file("./results_chn.json")
    elif args.language == "ara":
        dial_list = read_json_from_file("../data/arabic/dialogue_list_final.json")
        result = read_json_from_file("./train_results_ara.json") + read_json_from_file("./results_ara.json")
    else:
        dial_list = read_json_from_file("../data/spanish/dialogue_list_final.json")
        result = read_json_from_file("./train_results_esp.json") + read_json_from_file("./results_esp.json")

    for dial_data, retrival_data in zip(dial_list, result):
        assert dial_data["task_id"] == retrival_data["task_id"]
        for turn in retrival_data["retrievals"]["turns"]:
            turn["need_retrival"] = dial_data["utterance"][turn["turn_index"]]["need_retrieval"]
            turn["out_of_knowledge"] = dial_data["utterance"][turn["turn_index"]]["out_of_knowledge"]

    all_dev_turn = []
    for dial in result[:500]:
        all_dev_turn.extend(dial["retrievals"]["turns"])
    all_dev_turn = list(filter(lambda x: x["need_retrival"], all_dev_turn))

    all_test_turn = []
    for dial in result[-1000:]:
        all_test_turn.extend(dial["retrievals"]["turns"])

    all_test_turn = list(filter(lambda x: x["need_retrival"], all_test_turn))
    this_database = HealthDialogueDatabase(db_path="../data/who_database.json")

    random.seed(10086)
    icl_prompt = "Examples: "
    random_example_list = random.sample(all_dev_turn, args.num_icl_example)
    for idx, item in enumerate(random_example_list):
        this_example_prompt = example_to_prompt(item, idx,  args.top_k, snippet_database=this_database,)
        icl_prompt += "\n"
        icl_prompt += (this_example_prompt)

    input_list = []

    for index, item in enumerate(all_test_turn):
        this_input = {}

        task_prompt = example_to_prompt(item, 0, args.top_k,snippet_database=this_database, give_answer=False)

        prompt = instruction_prompt + icl_prompt + task_prompt

        this_input["prompt"] = prompt

        this_input["id"] = args.language + "_" + str(index)

        input_list.append(this_input)



    # Load LLaMA model
    model_name = "meta-llama/Llama-3.1-8B-Instruct"  # change to your model path if local
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to(
        "cuda" if torch.cuda.is_available() else "cpu")

    # Evaluate on test set
    correct = 0
    total = 0

    if args.full_dataset:
        test_samples = input_list
    else:

        test_samples = input_list[:10]

    print("\n🔍 Starting Evaluation...\n")
    for example in tqdm(test_samples):
        full_prompt =example["prompt"]
        this_id = example["id"]
        prediction = infer(model, tokenizer, full_prompt)

        print(f"Predicted: {prediction}, Actual: {example['gold_ids']}")
    #
    #     if predicted_label is None:
    #         continue  # skip ambiguous answers
    #
    #     if predicted_label == example["need_retrieval"]:
    #         correct += 1
    #     total += 1
    #
    # accuracy = correct / total if total > 0 else 0
    # print(f"\n✅ Evaluation Complete. Accuracy: {accuracy:.4f} ({correct}/{total})")




if __name__ == "__main__":
    main()


