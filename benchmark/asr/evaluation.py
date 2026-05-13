import asr_utils
import evaluate
import jieba

wer_metric = evaluate.load("wer")
cer_metric = evaluate.load("cer")


def evaluate(data, model_name):
    all_user_utterances = []
    for dialogue in data:
        for utterance in dialogue["utterance"]:
            if utterance["role"] == "user":
                if "CHN" not in dialogue["task_id"]:
                    all_user_utterances.append(utterance)
                else:
                    utterance["annotated_transcription"] = " ".join(list(jieba.cut(utterance["annotated_transcription"])))
                    utterance[f"{model_name}_asr_result"] = " ".join(list(jieba.cut(utterance[f"{model_name}_asr_result"])))
                    all_user_utterances.append(utterance)


    gold_results = [
        utterance["annotated_transcription"] for utterance in all_user_utterances
    ]
    predicted_results = [
        utterance[f"{model_name}_asr_result"] for utterance in all_user_utterances
    ]

    wer = wer_metric.compute(predictions=predicted_results, references=gold_results)
    cer = cer_metric.compute(predictions=predicted_results, references=gold_results)
    return {"wer": wer, "cer": cer}
