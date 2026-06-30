from __future__ import annotations
from typing import Any


def loadHistory(conversation_id: str) -> list[dict]:
    from pookiepages.database.tables import PpConversation
    try:
        messages = PpConversation.objects.filter(conversationId=conversation_id).order_by("createdAt")
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    except Exception:
        return []


def appendToHistory(conversation_id: str, role: str, content: str, model: str = ""):
    from pookiepages.database.tables import PpConversation
    PpConversation.objects.create(
        conversationId=conversation_id,
        role=role,
        content=content,
        model=model,
    )


def clearHistory(conversation_id: str):
    from pookiepages.database.tables import PpConversation
    try:
        PpConversation.objects.filter(conversationId=conversation_id).delete()
    except Exception:
        pass
