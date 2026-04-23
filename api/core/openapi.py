from typing import List, TypedDict, Type, Dict

from domain.objects import schemas


class EndpointMetadata(TypedDict):
    summary: str
    description: str
    tags: List[str]


class TagMetadata(TypedDict):
    name: str
    description: str


class ResponseMetadata(TypedDict):
    description: str
    model: Type[schemas.BaseResponse]


class APIMetadata(TypedDict):
    title: str
    version: str
    summary: str
    description: str
    openapi_tags: List[TagMetadata]
    responses: Dict[int, ResponseMetadata]


TAGS_METADATA: List[TagMetadata] = [
]


ENDPOINTS_METADATA: Dict[str, EndpointMetadata] = {
}


RESPONSES_METADATA: Dict[int, ResponseMetadata] = {
    400: {
        "description": "Request data is invalid",
        "model": schemas.ExceptionResponse
    },
    401: {
        "description": "Token is invalid or expired",
        "model": schemas.ExceptionResponse
    },
    403: {
        "description": "Access denied",
        "model": schemas.ExceptionResponse
    },
    404: {
        "description": "Object not found",
        "model": schemas.ExceptionResponse
    },
    409: {
        "description": "Logical error",
        "model": schemas.ExceptionResponse
    },
    500: {
        "description": "Internal server error",
        "model": schemas.ExceptionResponse
    }
}


API_METADATA: APIMetadata = {
    "title": "JenHub API",
    "version": "0.1.0",
    "summary": "API for JenHub",
    "description": "Create, read, update and delete lessons and replacements from CollegeTime",
    "openapi_tags": TAGS_METADATA,
    "responses": RESPONSES_METADATA
}