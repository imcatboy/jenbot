from typing import Literal, Tuple


MediaType = Literal["photo", "video"]

PHOTO_PREFIX = "photo:"
VIDEO_PREFIX = "video:"


def encode_attachment(file_id: str, media_type: MediaType) -> str:
    prefix = VIDEO_PREFIX if media_type == "video" else PHOTO_PREFIX
    return f"{prefix}{file_id}"


def parse_attachment(value: str) -> Tuple[str, MediaType | None]:
    if value.startswith(VIDEO_PREFIX):
        return value.removeprefix(VIDEO_PREFIX), "video"
    if value.startswith(PHOTO_PREFIX):
        return value.removeprefix(PHOTO_PREFIX), "photo"
    
    return value, None


def attachment_file_id(value: str) -> str:
    file_id, _ = parse_attachment(value)
    return file_id
