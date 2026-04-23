from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseRequest(BaseSchema): ...


class BaseResponse(BaseSchema): ...


class ExceptionResponse(BaseResponse):
    detail: str