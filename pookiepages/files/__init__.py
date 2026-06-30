from __future__ import annotations
import os
import mimetypes
from dataclasses import dataclass, field
from typing import Any
import pookiedb as pk
from pookiepages.exceptions import PookiePagesError


@dataclass
class FileConfig:
    allowedTypes: list[str] = field(default_factory=lambda: ["image/jpeg", "image/png", "image/webp"])
    maxSizeMb: float = 10.0


class FileField(pk.URLField):
    """Semantic field for storing uploaded file URLs. Stored as URLField in DB."""
    pass


class UploadedFile:
    def __init__(self, file_storage: Any, file_config: FileConfig | None = None):
        self._fileStorage = file_storage
        self.fileConfig = file_config or FileConfig()
        self.filename = file_storage.filename
        self._data: bytes | None = None
        self._validated = False

    def _readData(self) -> bytes:
        if self._data is None:
            self._data = self._fileStorage.read()
        return self._data

    def validate(self):
        data = self._readData()
        sizeMb = len(data) / (1024 * 1024)
        if sizeMb > self.fileConfig.maxSizeMb:
            raise PookiePagesError(
                f"File upload failed. File size {sizeMb:.1f}MB exceeds the maximum of "
                f"{self.fileConfig.maxSizeMb}MB. "
                f"Upload a smaller file or increase FileConfig.maxSizeMb."
            )

        mimeType = mimetypes.guess_type(self.filename)[0] or ""
        if self.fileConfig.allowedTypes and mimeType not in self.fileConfig.allowedTypes:
            raise PookiePagesError(
                f"File upload failed. File type '{mimeType}' is not allowed. "
                f"Allowed types: {', '.join(self.fileConfig.allowedTypes)}. "
                f"Upload a file of the correct type or update FileConfig.allowedTypes."
            )
        self._validated = True

    async def save(
        self,
        resize: tuple[int, int] | None = None,
        thumbnail: tuple[int, int] | None = None,
        convert: str | None = None,
        quality: int | None = None,
    ):
        from flask import current_app
        storageBackend = current_app.config.get("PP_STORAGE")

        if storageBackend is None:
            from pookiepages.storage.local import LocalStorage
            storageBackend = LocalStorage()

        data = self._readData()
        mimeType = mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

        if mimeType.startswith("image/") and any([resize, thumbnail, convert, quality]):
            from pookiepages.files.processors import processImage
            data = processImage(data, resize=resize, thumbnail=thumbnail, convert=convert, quality=quality)

        savedFile = await storageBackend.save(data, self.filename)

        if thumbnail:
            from pookiepages.files.processors import generateThumbnail
            thumbData = generateThumbnail(self._readData(), thumbnail)
            thumbName = f"thumb_{self.filename}"
            thumbFile = await storageBackend.save(thumbData, thumbName)
            savedFile.thumbnailUrl = thumbFile.url

        return savedFile
