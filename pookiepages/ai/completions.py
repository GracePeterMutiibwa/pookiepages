from __future__ import annotations
from dataclasses import dataclass, field
from typing import AsyncGenerator, Any
import httpx
from pookiepages.exceptions import PookiePagesError


@dataclass
class AIConfig:
    url: str = ""
    key: str = ""
    models: list[str] = field(default_factory=list)
    default: str = ""
    storeHistory: bool = False


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class UsageInfo:
    promptTokens: int = 0
    completionTokens: int = 0


@dataclass
class CompletionResult:
    content: str
    model: str
    usage: UsageInfo


class OpenAICompatibleProvider:
    def __init__(self, config: AIConfig):
        self.config = config
        self._baseUrl = config.url.rstrip("/")

    def _buildHeaders(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.key}",
            "Content-Type": "application/json",
        }

    def _resolveModel(self, model: str | None) -> str:
        return model or self.config.default or (self.config.models[0] if self.config.models else "gpt-4o")

    def _handleHttpError(self, response: httpx.Response):
        if 400 <= response.status_code < 500:
            raise PookiePagesError(
                f"AI completion failed at {self._baseUrl}. "
                f"Provider returned {response.status_code}: {response.text}. "
                f"Check your API key and request parameters."
            )
        if response.status_code >= 500:
            raise PookiePagesError(
                f"AI completion failed at {self._baseUrl}. "
                f"Provider returned {response.status_code} (server error): {response.text}. "
                f"Check the provider's status page for outages."
            )

    async def complete(
        self,
        messages: list[ChatMessage] | list[dict],
        system: str | None = None,
        model: str | None = None,
        conversation_id: str | None = None,
    ) -> CompletionResult:
        resolvedModel = self._resolveModel(model)
        allMessages = []

        if system:
            allMessages.append({"role": "system", "content": system})

        if conversation_id and self.config.storeHistory:
            from pookiepages.ai.history import loadHistory, appendToHistory
            historyMessages = loadHistory(conversation_id)
            allMessages.extend(historyMessages)

        for msg in messages:
            if isinstance(msg, ChatMessage):
                allMessages.append({"role": msg.role, "content": msg.content})
            else:
                allMessages.append(msg)

        payload = {"model": resolvedModel, "messages": allMessages}

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self._baseUrl}/chat/completions",
                    json=payload,
                    headers=self._buildHeaders(),
                )
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            raise PookiePagesError(
                f"AI completion failed. The provider at '{self._baseUrl}' was unreachable: {connErr}. "
                f"Check your AIConfig.url and network connectivity."
            )

        self._handleHttpError(response)
        data = response.json()

        responseContent = data["choices"][0]["message"]["content"]
        usageData = data.get("usage", {})
        result = CompletionResult(
            content=responseContent,
            model=data.get("model", resolvedModel),
            usage=UsageInfo(
                promptTokens=usageData.get("prompt_tokens", 0),
                completionTokens=usageData.get("completion_tokens", 0),
            ),
        )

        if conversation_id and self.config.storeHistory:
            from pookiepages.ai.history import appendToHistory
            for msg in messages:
                role = msg.role if isinstance(msg, ChatMessage) else msg.get("role", "user")
                content = msg.content if isinstance(msg, ChatMessage) else msg.get("content", "")
                appendToHistory(conversation_id, role, content, resolvedModel)
            appendToHistory(conversation_id, "assistant", responseContent, resolvedModel)

        return result

    async def stream(
        self,
        messages: list[ChatMessage] | list[dict],
        conversation_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        resolvedModel = self._resolveModel(None)
        allMessages = []

        if conversation_id and self.config.storeHistory:
            from pookiepages.ai.history import loadHistory
            allMessages.extend(loadHistory(conversation_id))

        for msg in messages:
            if isinstance(msg, ChatMessage):
                allMessages.append({"role": msg.role, "content": msg.content})
            else:
                allMessages.append(msg)

        payload = {"model": resolvedModel, "messages": allMessages, "stream": True}

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{self._baseUrl}/chat/completions",
                    json=payload,
                    headers=self._buildHeaders(),
                ) as response:
                    self._handleHttpError(response)
                    fullContent = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunkData = line[6:]
                            if chunkData.strip() == "[DONE]":
                                break
                            try:
                                import orjson
                                chunk = orjson.loads(chunkData)
                                delta = chunk["choices"][0].get("delta", {})
                                chunkContent = delta.get("content", "")
                                if chunkContent:
                                    fullContent += chunkContent
                                    yield chunkContent
                            except Exception:
                                pass

                    if conversation_id and self.config.storeHistory and fullContent:
                        from pookiepages.ai.history import appendToHistory
                        for msg in messages:
                            role = msg.role if isinstance(msg, ChatMessage) else msg.get("role", "user")
                            content = msg.content if isinstance(msg, ChatMessage) else msg.get("content", "")
                            appendToHistory(conversation_id, role, content, resolvedModel)
                        appendToHistory(conversation_id, "assistant", fullContent, resolvedModel)

        except PookiePagesError:
            raise
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            raise PookiePagesError(
                f"AI streaming failed. The provider at '{self._baseUrl}' was unreachable: {connErr}. "
                f"Check your AIConfig.url and network connectivity."
            )

    def history(self, conversation_id: str) -> list[dict]:
        from pookiepages.ai.history import loadHistory
        return loadHistory(conversation_id)

    def clearHistory(self, conversation_id: str):
        from pookiepages.ai.history import clearHistory
        clearHistory(conversation_id)

    async def summarize(self, conversation_id: str) -> str:
        historyMessages = self.history(conversation_id)
        if not historyMessages:
            return ""
        summaryPrompt = [{"role": "user", "content": "Summarize the above conversation in 2-3 sentences."}]
        result = await self.complete(historyMessages + summaryPrompt)
        return result.content
