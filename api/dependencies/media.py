from dependency_injector.wiring import inject, Provide
from fastapi.concurrency import run_in_threadpool
from fastapi import UploadFile, File, Depends
from fastapi.exceptions import HTTPException
from PIL import Image, ImageOps
from typing import List, Tuple
from filetype import guess
from pathlib import Path
from uuid import uuid4

from api.core.container import AppContainer
from api.core.settings import Settings
from domain.objects import dtos, entities
from domain.services import MediaService
from api.dependencies.uow import get_media_service
from api.dependencies.auth import Authorize


class ImageProcessor:
    def __init__(
        self,
        max_size: int,
        allowed_extensions: List[str],
        target_size: Tuple[int, int],
        storage_path: str,
    ):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions
        self.target_size = target_size
        self.storage_path = Path(storage_path)

    async def validate_and_process(self, file: UploadFile, settings: Settings):
        if file.size > self.max_size:
            raise HTTPException(400, "File is too large")

        file_info = guess(file.file)
        await file.seek(0)

        if not file_info or file_info.extension not in self.allowed_extensions:
            raise HTTPException(400, "Invalid file type")

        if len(file.filename) > settings.FILE_MAX_NAME_LENGTH:
            raise HTTPException(400, "File name is too long")

        try:
            image = Image.open(file.file)
            image.load()
        except Exception:
            raise HTTPException(400, "Invalid image")

        if image.height > 3000 or image.width > 3000:
            raise HTTPException(400, "Image is too large")

        if image.height < self.target_size[0] or image.width < self.target_size[1]:
            raise HTTPException(400, "Image is too small")

        image = await run_in_threadpool(
            ImageOps.fit, image, self.target_size, Image.Resampling.LANCZOS
        )
        return image, file_info.extension

    async def save_image(self, image: Image.Image, name: str, extension: str):
        path = self.storage_path / f"{name}.{extension}"
        await run_in_threadpool(image.save, path, format=image.format)
        image.close()


@inject
async def get_avatar(
    file: UploadFile = File(description="Avatar file to upload"),
    user: entities.UserEntity = Depends(Authorize()),
    settings: Settings = Depends(Provide[AppContainer.settings]),
    media_service: MediaService = Depends(get_media_service),
) -> entities.FileEntity:
    processor = ImageProcessor(
        max_size=settings.AVATAR_MAX_SIZE,
        allowed_extensions=settings.ALLOWED_AVATAR_EXTENSIONS,
        target_size=settings.AVATAR_SIZE,
        storage_path=settings.AVATAR_STORAGE_PATH,
    )

    image, extension = await processor.validate_and_process(file, settings)
    name = uuid4().hex

    dto = dtos.CreateFileDTO(
        name=name,
        display_name=file.filename,
        extension=extension,
        uploaded_by_user_id=user.id,
    )
    file_obj = await media_service.create_file(dto)
    await media_service.link_file_to_marketplace_user(
        file_id=file_obj.id, user_id=user.id
    )

    await processor.save_image(image, name, extension)
    return file_obj


@inject
async def get_product_image(
    file: UploadFile = File(...),
    user: entities.UserEntity = Depends(Authorize()),
    settings: Settings = Depends(Provide[AppContainer.settings]),
    media_service: MediaService = Depends(get_media_service),
) -> entities.FileEntity:
    processor = ImageProcessor(
        max_size=settings.PRODUCT_IMAGE_MAX_SIZE,
        allowed_extensions=settings.ALLOWED_PRODUCT_IMAGE_EXTENSIONS,
        target_size=settings.PRODUCT_IMAGE_SIZE,
        storage_path=settings.PRODUCT_IMAGE_STORAGE_PATH,
    )

    image, extension = await processor.validate_and_process(file, settings)
    name = uuid4().hex

    dto = dtos.CreateFileDTO(
        name=name,
        display_name=file.filename,
        extension=extension,
        uploaded_by_user_id=user.id,
    )
    file_obj = await media_service.create_file(dto)
    await processor.save_image(image, name, extension)
    return file_obj


@inject
async def get_message_file(
    file: UploadFile = File(description="Message file to upload"),
    settings: Settings = Depends(Provide[AppContainer.settings]),
    user: entities.UserEntity = Depends(Authorize()),
    media_service: MediaService = Depends(get_media_service),
) -> entities.FileEntity:
    if file.size > settings.MESSAGE_FILE_MAX_SIZE:
        raise HTTPException(status_code=400, detail="File is too large")

    type = guess(file.file)
    await file.seek(0)

    if not type or type.extension not in settings.ALLOWED_MESSAGE_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if len(file.filename) > settings.FILE_MAX_NAME_LENGTH:
        raise HTTPException(status_code=400, detail="File name is too long")

    name = uuid4().hex
    dto = dtos.CreateFileDTO(
        name=name,
        display_name=file.filename,
        extension=type.extension,
        uploaded_by_user_id=user.id,
    )
    file_object = await media_service.create_file(dto)
    await run_in_threadpool(
        file.file.write,
        f"{settings.MESSAGE_FILE_STORAGE_PATH}/{name}.{type.extension}",
    )
    file.close()
    return file_object
