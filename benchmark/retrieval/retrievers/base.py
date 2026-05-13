


class BaseRetriever:
    def __init__(self, corpus, language="eng"):
        self.language = language
        self.corpus = corpus

    def index(self):
        raise NotImplementedError

    def retrieve(self, query, top_k=5):
        """
        Should return a list of (text, score)
        """
        raise NotImplementedError