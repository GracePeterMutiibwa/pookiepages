# response

## JsonResponse

```python
from pookiepages.response import JsonResponse

return JsonResponse({"key": "value"}, status=200)
return JsonResponse({"error": "not found"}, status=404)
```

Serializes data using `orjson` and sets `Content-Type: application/json`. Accepts any JSON-serializable dict, list, or Pydantic model.

## StreamResponse

```python
from pookiepages.response import StreamResponse

async def chunks():
    for chunk in provider.stream(messages):
        yield chunk

return StreamResponse(chunks(), mimetype="text/event-stream")
```

Sets `Cache-Control: no-cache` and `X-Accel-Buffering: no` for real-time streaming.
