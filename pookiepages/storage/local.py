from __future__ import annotations
import os
import uuid
from dataclasses import dataclass


@dataclass
class SavedFile:
    url: str
    name: str
    size: int
    mimeType: str
    thumbnailUrl: str = ""


class LocalStorage:
    def __init__(self, upload_dir: str = "uploads", serve_url: str = "/uploads"):
        self.uploadDir = upload_dir
        self.serveUrl = serve_url.rstrip("/")
        os.makedirs(upload_dir, exist_ok=True)

    async def save(self, file_data: bytes, filename: str) -> SavedFile:
        import mimetypes
        uniqueName = f"{uuid.uuid4().hex}_{filename}"
        filePath = os.path.join(self.uploadDir, uniqueName)

        with open(filePath, "wb") as outputFile:
            outputFile.write(file_data)

        mimeType = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        return SavedFile(
            url=f"{self.serveUrl}/{uniqueName}",
            name=uniqueName,
            size=len(file_data),
            mimeType=mimeType,
        )
