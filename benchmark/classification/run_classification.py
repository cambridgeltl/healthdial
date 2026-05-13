import os
import sys
import argparse
from util import *
from tqdm import tqdm

from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding
)
from datasets import DatasetDict
from sklearn.metrics import  accuracy_score
import numpy as np
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))



def tokenize_function(example, tokenizer):
    return tokenizer(example["text"], truncation=True, padding=True)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, predictions)
    return {"accuracy": acc}

def train_model(datasets):
    model_checkpoint = "xlm-roberta-base"
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

    # Convert `need_retrieval` to int for classification
    def format_labels(example):
        example["label"] = int(example["need_retrieval"])
        return example

    datasets = datasets.map(format_labels)
    tokenized_datasets = datasets.map(lambda x: tokenize_function(x, tokenizer), batched=True)
    tokenized_datasets = tokenized_datasets.remove_columns(["text", "need_retrieval"])

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=2)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Training setup
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir="./logs",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=3,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy"
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    # Train and evaluate
    trainer.train()
    print("✅ Validation Results:", trainer.evaluate())

    # Final test evaluation
    test_results = trainer.evaluate(tokenized_datasets["test"])
    print("🧪 Test Results:", test_results)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default="eng", help="Language code (e.g. eng, ara, spa)")
    args = parser.parse_args()

    datasets = load_data(language=args.language)

    print(datasets)
    print(datasets["train"][0])

    train_model(datasets)