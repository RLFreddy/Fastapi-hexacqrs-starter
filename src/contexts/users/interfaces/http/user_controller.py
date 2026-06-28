from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.contexts.users.application.queries.get_user import GetUserQuery
from src.contexts.users.application.queries.get_user_handler import GetUserHandler
from src.contexts.users.application.queries.get_users import GetUsersQuery
from src.contexts.users.application.queries.get_users_handler import GetUsersHandler
from src.shared.application.auth import get_current_user
from src.shared.application.dependency_injection import Container
from src.shared.infrastructure.event_bus import RabbitMQEventBus
from src.shared.interfaces.errors import ValidationErrorResponse


class UserCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        examples=["John Doe"],
        description="Full name of the user",
    )
    email: EmailStr = Field(
        ...,
        examples=["john@example.com"],
        description="Email address of the user",
    )
    password: str = Field(
        ...,
        min_length=6,
        examples=["Str0ng!Pass123"],
        description="User password (min 6 characters)",
    )


class UserCreateResponse(BaseModel):
    message: str = Field(
        ...,
        examples=["User creation started"],
        description="Confirmation message",
    )
    model_config = ConfigDict(json_schema_extra={"examples": [{"message": "User creation started"}]})


class UserResponse(BaseModel):
    id: str = Field(
        ...,
        examples=["ae28faaf-fe63-4665-b785-bb696412ff12"],
        description="User UUID",
    )
    name: str = Field(..., examples=["John Doe"], description="User full name")
    email: str = Field(..., examples=["john@example.com"], description="User email")
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "ae28faaf-fe63-4665-b785-bb696412ff12",
                    "name": "John Doe",
                    "email": "john@example.com",
                }
            ]
        }
    )


class ErrorDetail(BaseModel):
    detail: str = Field(..., examples=["Error description"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"detail": "Not authenticated"},
                {"detail": "Token expired"},
                {"detail": "Invalid token"},
                {"detail": "User not found"},
                {"detail": "Internal server error"},
            ]
        }
    )


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserCreateResponse,
    status_code=202,
    summary="Create a user (async via event bus)",
    description="Initiates user creation through the RabbitMQ event bus. The user is created asynchronously by a background consumer.",  # noqa: E501
    responses={
        422: {
            "model": ValidationErrorResponse,
            "description": "Validation error — invalid email, short password, empty name, or missing field",
        },
        500: {"model": ErrorDetail, "description": "Event bus unavailable or internal error"},
    },
)
@inject
async def create_user(
    user_data: UserCreateRequest, event_bus: RabbitMQEventBus = Depends(Provide[Container.event_bus])
) -> UserCreateResponse:
    try:
        await event_bus.publish(
            exchange="users",
            routing_key="user.created",
            message={"name": user_data.name, "email": user_data.email, "password": user_data.password},
        )
        return UserCreateResponse(message="User creation started")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List all users",
    description="Returns all users from the users context. Requires JWT authentication.",
    responses={
        401: {"model": ErrorDetail, "description": "Not authenticated or invalid/expired token"},
        500: {"model": ErrorDetail, "description": "Internal server error"},
    },
)
@inject
def get_users(
    handler: GetUsersHandler = Depends(Provide[Container.get_users_handler]),
    _current_user: str = Depends(get_current_user),
) -> list[UserResponse]:
    try:
        query = GetUsersQuery()
        users = handler.handle(query)
        return [UserResponse(id=u["id"], name=u["name"], email=u["email"]) for u in users]
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    description="Returns a single user by their UUID. Requires JWT authentication.",
    responses={
        401: {"model": ErrorDetail, "description": "Not authenticated or invalid/expired token"},
        404: {"model": ErrorDetail, "description": "User not found"},
        500: {"model": ErrorDetail, "description": "Internal server error"},
    },
)
@inject
def get_user(
    user_id: str,
    handler: GetUserHandler = Depends(Provide[Container.get_user_handler]),
    _current_user: str = Depends(get_current_user),
) -> UserResponse:
    query = GetUserQuery(user_id=user_id)
    try:
        user = handler.handle(query)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(id=user["id"], name=user["name"], email=user["email"])
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
