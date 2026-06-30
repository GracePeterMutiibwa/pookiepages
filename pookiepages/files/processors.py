from __future__ import annotations
from typing import Any
from PIL import Image
import io


def processImage(
    file_data: bytes,
    resize: tuple[int, int] | None = None,
    thumbnail: tuple[int, int] | None = None,
    convert: str | None = None,
    quality: int | None = None,
) -> bytes:
    image = Image.open(io.BytesIO(file_data))

    if convert:
        image = image.convert(convert.upper())

    if resize:
        image = image.resize(resize, Image.LANCZOS)

    if thumbnail:
        image.thumbnail(thumbnail, Image.LANCZOS)

    outputBuffer = io.BytesIO()
    saveFormat = image.format or "JPEG"
    saveKwargs: dict[str, Any] = {}
    if quality is not None:
        saveKwargs["quality"] = quality

    image.save(outputBuffer, format=saveFormat, **saveKwargs)
    return outputBuffer.getvalue()


def generateThumbnail(file_data: bytes, size: tuple[int, int] = (128, 128)) -> bytes:
    return processImage(file_data, thumbnail=size)
