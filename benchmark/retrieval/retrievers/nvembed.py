import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from .base import BaseRetriever

class NVEmbedRetriever(BaseRetriever):
    def __init__(self, corpus, language="eng", model_name="nvidia/NV-Embed-v2"):
        super().__init__(corpus, language)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.max_length = 2048

        # Task-specific instruction
        self.query_instruction = "Instruct: Given a question, retrieve passages that answer the question\nQuery: "
        self.passage_instruction = ""

    def add_eos(self, texts):
        return [text + self.tokenizer.eos_token for text in texts]

    def encode(self, texts, instruction=""):
        inputs = [instruction + text for text in texts]
        inputs = self.add_eos(inputs)
        return self.model.encode(inputs, instruction=instruction, max_length=self.max_length)

    def index(self, batch_size=4):
        # print("🔍 Encoding corpus embeddings with NV-Embed-v2...")
        # # "get the maximum length of the corpus"
        # max_length = max(len(self.model.tokenizer.tokenize(text)) for text in self.corpus)
        # print(f"Max length of corpus: {max_length}")
        # self.max_length = max_length
        print("🔍 Encoding corpus embeddings with NV-Embed-v2 in batches...")
        all_embeddings = []
        self.model.eval()

        with torch.no_grad():
            for i in range(0, len(self.corpus), batch_size):
                batch = self.corpus[i:i + batch_size]
                batch_embeddings = self.encode(batch, instruction=self.passage_instruction)
                batch_embeddings = F.normalize(batch_embeddings, p=2, dim=1)
                all_embeddings.append(batch_embeddings)

        self.embeddings = torch.cat(all_embeddings, dim=0)

    def retrieve(self, query, top_k=5):
        with torch.no_grad():
            query_embedding = self.encode([query], instruction=self.query_instruction)
            query_embedding = F.normalize(query_embedding, p=2, dim=1)
            scores = torch.matmul(query_embedding, self.embeddings.T)[0]
            top_results = torch.topk(scores, k=top_k)
            top_indices = top_results.indices.tolist()
            top_scores = top_results.values.tolist()
        return [(self.corpus[i], top_scores[j]) for j, i in enumerate(top_indices)]