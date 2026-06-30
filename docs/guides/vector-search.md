# Vector search

pookiepages wraps zvec for in-process vector search.

## Setup

```python
from pookiepages.ai import EmbeddingProvider, EmbeddingsConfig
from pookiepages.vectors import VectorStore

embedder = EmbeddingProvider(EmbeddingsConfig(
    url="https://api.openai.com/v1",
    key="sk-your-key",
    model="text-embedding-3-small",
    dimensions=1536,
))

store = VectorStore(path="vectors/docs", dimensions=1536, embedder=embedder)
```

## Insert

```python
await store.insert(
    id="doc-1",
    text="pookiepages is a Python web framework",
    metadata={"source": "readme", "page": 1},
)
```

## Search

```python
results = await store.search("Python web framework", top_k=5)
for result in results:
    print(result.id, result.score, result.metadata)
```

## Delete

```python
store.delete("doc-1")
```
