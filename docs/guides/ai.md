# AI

## Text completion

```python
from pookiepages.ai import OpenAICompatibleProvider, AIConfig, ChatMessage

provider = OpenAICompatibleProvider(AIConfig(
    url="https://api.openai.com/v1",
    key="sk-your-api-key",
    default="gpt-4o",
    storeHistory=True,
))

result = await provider.complete(
    messages=[ChatMessage(role="user", content="What is pookiepages?")],
    conversationId="session-abc",
)
print(result.content)
print(result.usage.promptTokens, result.usage.completionTokens)
```

## Streaming

```python
async for chunk in provider.stream(
    messages=[ChatMessage(role="user", content="Tell me a story")],
):
    print(chunk, end="", flush=True)
```

## Conversation history

```python
history = provider.history("session-abc")
provider.clearHistory("session-abc")
summary = await provider.summarize("session-abc")
```

## Embeddings

```python
from pookiepages.ai import EmbeddingProvider, EmbeddingsConfig

embedder = EmbeddingProvider(EmbeddingsConfig(
    url="https://api.openai.com/v1",
    key="sk-your-key",
    model="text-embedding-3-small",
    dimensions=1536,
))

vector = await embedder.embed("my search text")
vectors = await embedder.embedMany(["text one", "text two"])
```
