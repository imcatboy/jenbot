from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.objects import exceptions


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


async def domain_exception_handler(
    request: Request, exc: exceptions.DomainException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Error occurred while processing the request"},
    )


async def object_not_found_exception_handler(
    request: Request, exc: exceptions.ObjectNotFoundException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Object not found"}
    )


async def object_already_exists_exception_handler(
    request: Request, exc: exceptions.ObjectAlreadyExistsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Object already exists"},
    )


async def too_many_objects_found_exception_handler(
    request: Request, exc: exceptions.TooManyObjectsFoundException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Too many objects found"},
    )


async def duplicate_ids_exception_handler(
    request: Request, exc: exceptions.DuplicateIdsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Duplicate IDs found"},
    )

async def missing_option_exception_handler(
    request: Request, exc: exceptions.MissingOptionException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Missing option found"},
    )

async def invalid_option_relation_exception_handler(
    request: Request, exc: exceptions.InvalidOptionRelationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid option relation found"},
    )