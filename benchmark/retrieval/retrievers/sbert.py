from sentence_transformers import SentenceTransformer, util
import torch
from .base import BaseRetriever

class SBERTRetriever(BaseRetriever):
    def __init__(self, corpus, language="eng", model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        super().__init__(corpus, language)
        self.model = SentenceTransformer(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def index(self):
        print("🔍 Encoding corpus embeddings with SBERT...")
        self.embeddings = self.model.encode(self.corpus, convert_to_tensor=True, show_progress_bar=True)

    def retrieve(self, query, top_k=5):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.embeddings)[0]  # shape: (corpus_size,)
        top_results = torch.topk(scores, k=top_k)
        top_indices = top_results.indices.tolist()
        top_scores = top_results.values.tolist()

        return [(self.corpus[i], top_scores[j]) for j, i in enumerate(top_indices)]