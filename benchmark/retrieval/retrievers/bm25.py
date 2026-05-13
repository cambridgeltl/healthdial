from rank_bm25 import BM25Okapi
from .base import BaseRetriever
import jieba

def tokenize(text, language="eng"):
    text = text.lower()
    if language == "chn" or language.startswith("zh"):
        return list(jieba.cut(text))
    else:
        return text.split()


class BM25Retriever(BaseRetriever):
    def index(self):
        self.tokenized_corpus = [tokenize(doc, self.language) for doc in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def retrieve(self, query, top_k=5):
        tokenized_query = tokenize(query, self.language)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda j: (-scores[j], j))[:top_k]
        return [(self.corpus[i], scores[i]) for i in top_indices]