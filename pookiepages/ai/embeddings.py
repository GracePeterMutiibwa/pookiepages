from __future__ import annotations
from dataclasses import dataclass
import httpx
from pookiepages.exceptions import PookiePagesError


@dataclass
class EmbeddingsConfig:
    url: str = ""
    key: str = ""
    model: str = "text-embedding-3-small"
    vectorsPath: str = "vectors"
    dimensions: int = 1536


class EmbeddingProvider:
    def __init__(self, config: EmbeddingsConfig):
        self.config = config
        self._baseUrl = config.url.rstrip("/")

    def _buildHeaders(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.key}",
            "Content-Type": "application/json",
        }

    def _handleHttpError(self, response: httpx.Response):
        if response.status_code >= 400:
            raise PookiePagesError(
                f"Embedding request failed at {self._baseUrl}. "
                f"Provider returned {response.status_code}: {response.text}. "
                f"Check your API key, model name, and endpoint URL."
            )

    async def embed(self, text: str) -> list[float]:
        results = await self.embedMany([text])
        return results[0]

    async def embedMany(self, texts: list[str]) -> list[list[float]]:
        payload = {"model": self.config.model, "input": texts}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self._baseUrl}/embeddings",
                    json=payload,
                    headers=self._buildHeaders(),
                )
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as connErr:
            raise PookiePagesError(
                f"Embedding request failed. The provider at '{self._baseUrl}' was unreachable: {connErr}. "
                f"Check your EmbeddingsConfig.url and network connectivity."
            )

        self._handleHttpError(response)
        data = response.json()
        return [item["embedding"] for item in data["data"]]
