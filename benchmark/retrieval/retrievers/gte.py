import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from .base import BaseRetriever

class GTEEmbedRetriever(BaseRetriever):
    def __init__(self, corpus, language="eng", model_name="Alibaba-NLP/gte-multilingual-base"):
        super().__init__(corpus, language)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.max_length = 8192
        self.output_dim = 768  # GTE base output dimension

        self.query_instruction = ""  # GTE typically doesn't require special instructions
        self.passage_instruction = ""

    def encode(self, texts, instruction=""):
        inputs = [instruction + text for text in texts]
        batch_dict = self.tokenizer(
            inputs,
            max_length=self.max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        outputs = self.model(**batch_dict)
        embeddings = outputs.last_hidden_state[:, 0][:, :self.output_dim]
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings

    def index(self, batch_size=4):
        print("🔍 Encoding corpus embeddings with GTE-multilingual-base in batches...")
        all_embeddings = []
        self.model.eval()

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