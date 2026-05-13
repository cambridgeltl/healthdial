import openai
import os
import torch
from .base import BaseRetriever
from tqdm import tqdm

class OpenAIRetriever(BaseRetriever):
    def __init__(self, corpus, language="eng", embedding_model="text-embedding-3-small", cache_dir="../results/embeddings/"):
        super().__init__(corpus, language)
        self.model_name = embedding_model
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # Use a hash of corpus to avoid filename collisions (optional)
        model_tag = self.model_name.replace("-", "_")  # for cleaner filename
        self.embedding_path = os.path.join(
            cache_dir, f"openai_{model_tag}_{language}_{len(self.corpus)}_embeddings.pt"
        )

    def embed(self, texts):
        results = []
        batch_size = 100
        for i in tqdm(range(0, len(texts), batch_size), desc="🔍 OpenAI Embedding"):
            batch = texts[i:i+batch_size]
            response = openai.embeddings.create(
                input=batch,
                model=self.model_name
            )
            results.extend([d.embedding for d in response.data])
        return torch.tensor(results)

    def index(self):
        if os.path.exists(self.embedding_path):
            print(f"📦 Loading cached embeddings from {self.embedding_path}")
            self.embeddings = torch.load(self.embedding_path)
        else:
            print("🔍 Encoding corpus embeddings with OpenAI...")
            self.embeddings = self.embed(self.corpus)
            self.embeddings = torch.nn.functional.normalize(self.embeddings, dim=1)
            torch.save(self.embeddings, self.embedding_path)
            print(f"✅ Saved embeddings to {self.embedding_path}")

    def retrieve(self, query, top_k=5):
        query_embedding = openai.embeddings.create(
            input=[query],
            model=self.model_name
        ).data[0].embedding
        query_tensor = torch.tensor(query_embedding)
        query_tensor = torch.nn.functional.normalize(query_tensor, dim=0)

        scores = torch.matmul(self.embeddings, query_tensor)
        top_results = torch.topk(scores, k=top_k)
        top_indices = top_results.indices.tolist()
        top_scores = top_results.values.tolist()

        return [(self.corpus[i], top_scores[j]) for j, i in enumerate(top_indices)]