from __future__ import annotations
from typing import Any, Generator
import orjson
from flask import Response


class JsonResponse(Response):
    """JSON response using orjson for fast serialization."""

    def __init__(self, data: Any, status: int = 200, headers: dict | None = None):
        serialized = orjson.dumps(data)
        super().__init__(
            response=serialized,
            status=status,
            headers=headers or {},
            mimetype="application/json",
        )


class StreamResponse(Response):
    """Streaming response for generators (SSE, chunked transfer, AI streaming)."""

    def __init__(self, generator: Generator, mimetype: str = "text/event-stream", status: int = 200):
        super().__init__(
            response=generator,
            status=status,
            mimetype=mimetype,
            direct_passthrough=True,
        )
        self.headers["Cache-Control"] = "no-cache"
        self.headers["X-Accel-Buffering"] = "no"
