# OpenAI and compatible APIs

pookiepages uses the OpenAI-compatible API format for both completions and embeddings. Any provider that implements the OpenAI REST API can be used.

## Completions

```python
from pookiepages.ai import OpenAICompatibleProvider, AIConfig, ChatMessage

provider = OpenAICompatibleProvider(AIConfig(
    url="https://api.openai.com/v1",
    key="sk-your-key",
    default="gpt-4o",
    storeHistory=True,
))

result = await provider.complete(
    messages=[ChatMessage(role="user", content="Hello")],
    conversationId="session-abc",
)
```

## Embeddings

```python
from pookiepages.ai import EmbeddingProvider, EmbeddingsConfig

embedder = EmbeddingProvider(EmbeddingsConfig(
    url="https://api.openai.com/v1",
    key="sk-your-key",
    model="text-embedding-3-small",
    dimensions=1536,
    vectorsPath="vectors/",
))
```

## Using Anthropic Claude via OpenAI-compatible proxy

Point `url` to a proxy that wraps the Anthropic API with an OpenAI-compatible interface, or use a service like LiteLLM.

## Using Ollama (local)

```python
provider = OpenAICompatibleProvider(AIConfig(
    url="http://localhost:11434/v1",
    key="ollama",
    default="llama3.2",
))
```
