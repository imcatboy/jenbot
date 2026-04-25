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
    {
        "name": "User",
        "description": "User endpoints"
    },
    {
        "name": "Marketplace",
        "description": "Marketplace endpoints"
    },
    {
        "name": "Messaging",
        "description": "Messaging endpoints"
    },
    {
        "name": "Product",
        "description": "Product endpoints"
    }
]


ENDPOINTS_METADATA: Dict[str, EndpointMetadata] = {
    "get_me": {
        "summary": "Get current user information",
        "description": "Get current user information",
        "tags": ["User"]
    },
    "get_user": {
        "summary": "Get user information by ID",
        "description": "Get user information by ID",
        "tags": ["User"]
    },
    "update_user": {
        "summary": "Update current user information",
        "description": "Update current user information",
        "tags": ["User"]
    },
    "create_review": {
        "summary": "Create a review",
        "description": "Create a review",
        "tags": ["User"]
    },
    "get_reviews": {
        "summary": "Get reviews by user ID",
        "description": "Get reviews by user ID",
        "tags": ["User"]
    },
    "get_advertisements": {
        "summary": "Get advertisements",
        "description": "Get advertisements",
        "tags": ["Marketplace"]
    },
    "get_advertisement": {
        "summary": "Get advertisement by ID",
        "description": "Get advertisement by ID",
        "tags": ["Marketplace"]
    },
    "create_advertisement": {
        "summary": "Create an advertisement",
        "description": "Create an advertisement",
        "tags": ["Marketplace"]
    },
    "update_advertisement": {
        "summary": "Update advertisement by ID",
        "description": "Update advertisement by ID",
        "tags": ["Marketplace"]
    },
    "delete_advertisement": {
        "summary": "Delete advertisement by ID",
        "description": "Delete advertisement by ID",
        "tags": ["Marketplace"]
    },
    "get_chats": {
        "summary": "Get chats",
        "description": "Get chats",
        "tags": ["Messaging"]
    },
    "get_chat": {
        "summary": "Get chat by ID",
        "description": "Get chat by ID",
        "tags": ["Messaging"]
    },
    "create_chat": {
        "summary": "Create a chat",
        "description": "Create a chat",
        "tags": ["Messaging"]
    },
    "create_message": {
        "summary": "Create a message",
        "description": "Create a message",
        "tags": ["Messaging"]
    },
    "get_messages": {
        "summary": "Get messages by chat ID",
        "description": "Get messages by chat ID",
        "tags": ["Messaging"]
    },
    "get_message": {
        "summary": "Get message by ID",
        "description": "Get message by ID",
        "tags": ["Messaging"]
    },
    "get_products": {
        "summary": "Get products",
        "description": "Get products",
        "tags": ["Product"]
    },
    "get_product": {
        "summary": "Get product by ID",
        "description": "Get product by ID",
        "tags": ["Product"]
    },
    "create_product": {
        "summary": "Create a product",
        "description": "Create a product",
        "tags": ["Product"]
    },
    "get_categories": {
        "summary": "Get categories",
        "description": "Get categories",
        "tags": ["Product"]
    },
    "get_category": {
        "summary": "Get category by ID",
        "description": "Get category by ID",
        "tags": ["Product"]
    },
    "create_category": {
        "summary": "Create a category",
        "description": "Create a category",
        "tags": ["Product"]
    },
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