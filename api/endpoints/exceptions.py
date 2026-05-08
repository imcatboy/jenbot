from sentry_sdk import capture_exception
from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.objects import exceptions


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


async def domain_exception_handler(
    request: Request, exc: exceptions.DomainException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Error occurred while processing the request"},
    )


async def object_not_found_exception_handler(
    request: Request, exc: exceptions.ObjectNotFoundException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Object not found"}
    )


async def object_already_exists_exception_handler(
    request: Request, exc: exceptions.ObjectAlreadyExistsException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Object already exists"},
    )


async def too_many_objects_found_exception_handler(
    request: Request, exc: exceptions.TooManyObjectsFoundException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Too many objects found"},
    )


async def duplicate_ids_exception_handler(
    request: Request, exc: exceptions.DuplicateIdsException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Duplicate IDs found"},
    )


async def missing_option_exception_handler(
    request: Request, exc: exceptions.MissingOptionException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Missing option found"},
    )


async def invalid_option_relation_exception_handler(
    request: Request, exc: exceptions.InvalidOptionRelationException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid option relation found"},
    )


async def not_enough_inventory_exception_handler(
    request: Request, exc: exceptions.NotEnoughInventoryException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Not enough inventory"},
    )


async def invalid_data_exception_handler(
    request: Request, exc: exceptions.InvalidDataException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid data"},
    )


async def deal_not_pending_exception_handler(
    request: Request, exc: exceptions.DealNotPendingException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Deal not pending"},
    )


async def deal_self_purchase_exception_handler(
    request: Request, exc: exceptions.DealSelfPurchaseException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Deal self purchase found"},
    )


async def chat_participant_not_found_exception_handler(
    request: Request, exc: exceptions.ChatParticipantNotFoundException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Chat participant not found"},
    )


async def file_not_found_exception_handler(
    request: Request, exc: exceptions.FileNotFoundException
) -> JSONResponse:
    capture_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "File not found"},
    )