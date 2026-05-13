def compute_metrics_for_turn(gold_ids, pred_ids, k_values=[1, 3, 5, 7, 10]):
    gold_ids = set(gold_ids)
    pred_ids = list(pred_ids)

    result = {}

    for k in k_values:
        top_k = set(pred_ids[:k])

        tp = len(gold_ids & top_k)
        fp = len(top_k - gold_ids)
        fn = len(gold_ids - top_k)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        result[f"Recall@{k}"] = recall
        result[f"Precision@{k}"] = precision
        result[f"F1@{k}"] = f1

    # MRR (reciprocal rank of first correct item)
    rr = 0.0
    for rank, pid in enumerate(pred_ids, start=1):
        if pid in gold_ids:
            rr = 1 / rank
            break
    result["MRR"] = rr

    # Out-of-knowledge prediction — assume it's 0 if anything retrieved
    # result["OutOfKnowledgeGold"] = out_of_knowledge
    # result["OutOfKnowledgePred"] = len(gold_ids) == 0

    return result