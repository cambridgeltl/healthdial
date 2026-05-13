import torch
from FlagEmbedding import BGEM3FlagModel
from .base import BaseRetriever

class BGEEmbedRetriever(BaseRetriever):
    def __init__(self, corpus, language="eng", model_name="BAAI/bge-m3"):
        super().__init__(corpus, language)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = BGEM3FlagModel(model_name, use_fp16=True)
        self.max_length = 8192
        self.query_instruction = ""  # Can be adjusted if needed
        self.passage_instruction = ""

    def encode(self, texts, instruction=""):
        # BGE can use instruction-tuned prompts, but not required here
        inputs = [instruction + text for text in texts]
        output = self.model.encode(
            inputs,
            batch_size=12,
            max_length=self.max_length
        )
        embeddings = output['dense_vecs']
        return torch.tensor(embeddings, device=self.device)

    def index(self, batch_size=12):
        print("🔍 Encoding corpus embeddings with BGE-M3 in batches...")
        all_embeddings = []
        self.model.model.eval()

        with torch.no_grad():
            for i in range(0, len(self.corpus), batch_size):
                batch = self.corpus[i:i + batch_size]
                batch_embeddings = self.encode(batch, instruction=self.passage_instruction)
                all_embeddings.append(batch_embeddings)

        self.embeddings = torch.cat(all_embeddings, dim=0)

    def retrieve(self, query, top_k=5):
        with torch.no_grad():
            query_embedding = self.encode([query], instruction=self.query_instruction)
            scores = torch.matmul(query_embedding, self.embeddings.T)[0]
            top_results = torch.topk(scores, k=top_k)
            top_indices = top_results.indices.tolist()
            top_scores = top_results.values.tolist()
        return [(self.corpus[i], top_scores[j]) for j, i in enumerate(top_indices)]