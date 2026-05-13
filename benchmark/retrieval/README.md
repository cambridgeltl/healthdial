# 🧠 Multilingual Health Dialogue Retrieval Benchmark

This project implements and benchmarks various retrieval methods on a multilingual spoken dialogue dataset for health education. It supports context-aware retrieval and evaluation across multiple languages and retrievers.

---

## 🚀 How to Run

To run BM25 retrieval on English data:

```bash
python run_retrieval.py --language eng --retriever bm25

python run_retrieval.py --language eng --retriever openai --embedding_model text-embedding-3-large
```

You can change the `--language` and `--retriever` arguments to test different settings.

language options are: esp, chn, eng, ara

---

## 🧠 Retrieval Experiment Design Considerations

### 1. 🔍 Knowledge Corpus Construction

**What is retrieved?**

Two strategies were considered for building the retrieval corpus:

- **Option A: Content Only**  
  Use only the main textual content of each knowledge snippet.  
  **Example:**

  ```
  Vaccination is a simple, safe, and effective way of protecting you against harmful diseases...
  ```

- **✅ Option B (Chosen): Topic + Title + Content**  
  To enhance surface-form matching, we concatenate the topic and title with the main content.  
  **Example:**

  ```
  Vaccines and immunization: What is vaccination? What is vaccination? Vaccination is a simple, safe...
  ```

  This richer representation improves the likelihood of matching user queries with relevant documents, especially when user phrasing aligns with section headers or topics rather than body text.

---

### 2. 🪟 Context-Aware Query Construction

**How is the query constructed?**

For each assistant response turn:

- The context window includes **all** utterances (system and user) up to and including the current user query.
- Only **user turns** are extracted from this window and concatenated to form the final query string.

This allows the retriever to:

- Capture dialogue progression
- Disambiguate entities
- Incorporate cumulative user information

**Example (at turn index 5):**

| Turn | Speaker   | Utterance                        |
| ---- | --------- | -------------------------------- |
| 00   | Assistant | Greeting                         |
| 01   | User      | Expresses concern about daughter |
| 02   | Assistant | Follow-up                        |
| 03   | User      | Elaborates on eating habits      |
| 04   | Assistant | Asks for more details            |

**Query for retrieval:**

```
User 01 utterance + Assistant 02 response + User 03 utterance + Assistant 04 response
```

---

## 🧪 Evaluation Setup

For each assistant turn (i.e. a system-generated reply), we evaluate the top-K retrieved snippets against the gold standard using the following metrics:

- `Recall@K`
- `Precision@K`
- `F1@K`
- `MRR` (Mean Reciprocal Rank)
- `Out-of-Knowledge Prediction`:
  - `OutOfKnowledgeGold`: Whether the gold response required knowledge not in the base.
  - `OutOfKnowledgePred`: Whether the retriever returned no known snippets.

**Outputs:**

- Turn-level metrics are saved individually.
- Aggregate results are computed across the dataset.

