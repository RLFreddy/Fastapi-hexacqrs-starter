from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.contexts.auth.application.commands.register_user import RegisterUserCommand
from src.contexts.auth.application.commands.register_user_handler import RegisterUserHandler
from src.contexts.auth.application.queries.auth_users import GetAuthUsersQuery
from src.contexts.auth.application.queries.auth_users_handler import GetAuthUsersHandler
from src.contexts.auth.application.queries.login_user import LoginUserQuery
from src.contexts.auth.application.queries.login_user_handler import LoginUserHandler
from src.shared.application.dependency_injection import Container
from src.shared.application.exceptions import UnauthorizedError, ValidationError
from src.shared.interfaces.errors import ValidationErrorResponse

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        examples=["user@example.com"],
        description="Email address for the new account",
    )
    password: str = Field(
        ...,
        min_length=6,
        examples=["Str0ng!Pass123"],
        description="Password (min 6 characters)",
    )


class RegisterResponse(BaseModel):
    user_id: str = Field(
        ...,
        examples=["ae28faaf-fe63-4665-b785-bb696412ff12"],
        description="UUID of the created user",
    )
    model_config = ConfigDict(json_schema_extra={"examples": [{"user_id": "ae28faaf-fe63-4665-b785-bb696412ff12"}]})


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        examples=["user@example.com"],
        description="Registered email address",
    )
    password: str = Field(
        ...,
        examples=["Str0ng!Pass123"],
        description="Account password",
    )


class LoginResponse(BaseModel):
    authenticated: bool = Field(..., examples=[True])
    user_id: str = Field(
        ...,
        examples=["ae28faaf-fe63-4665-b785-bb696412ff12"],
        description="Authenticated user UUID",
    )
    token: str = Field(
        ...,
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZTI4ZmFhZi1mZTYzLTQ2NjUtYjc4NS1iYjY5NjQxMmZmMTIiLCJleHAiOjE3ODI2MTgyODV9.c6VB0PWZGqr8bS_qPZm1Nw5cSGn75j3MkmFEg0ca2Js"  # noqa: E501
        ],
        description="JWT access token",
    )
    token_type: str = Field(
        default="bearer",
        examples=["bearer"],
        description="Token type for Authorization header",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "authenticated": True,
                    "user_id": "ae28faaf-fe63-4665-b785-bb696412ff12",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZTI4ZmFhZi1mZTYzLTQ2NjUtYjc4NS1iYjY5NjQxMmZmMTIiLCJleHAiOjE3ODI2MTgyODV9.c6VB0PWZGqr8bS_qPZm1Nw5cSGn75j3MkmFEg0ca2Js",  # noqa: E501
                    "token_type": "bearer",
                }
            ]
        }
    )


class AuthUserResponse(BaseModel):
    id: str = Field(
        ...,
        examples=["ae28faaf-fe63-4665-b785-bb696412ff12"],
        description="User UUID",
    )
    email: str = Field(
        ...,
        examples=["user@example.com"],
        description="User email",
    )
    is_active: bool = Field(
        ...,
        examples=[True],
        description="Whether the account is active",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "ae28faaf-fe63-4665-b785-bb696412ff12",
                    "email": "user@example.com",
                    "is_active": True,
                }
            ]
        }
    )


class ErrorDetail(BaseModel):
    detail: str = Field(..., examples=["Invalid credentials"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"detail": "User not found"},
                {"detail": "Invalid password"},
                {"detail": "Email already registered"},
                {"detail": "Internal server error"},
            ]
        }
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Register a new user",
    description="Creates a new user account. The email must be unique. The password is hashed with bcrypt before storage.",  # noqa: E501
    responses={
        400: {"model": ErrorDetail, "description": "Invalid input or email already registered"},
        422: {
            "model": ValidationErrorResponse,
            "description": "Validation error — invalid email, short password, or missing field",
        },
        500: {"model": ErrorDetail, "description": "Internal server error"},
    },
)
@inject
async def register_user(
    request: RegisterRequest, handler: RegisterUserHandler = Depends(Provide[Container.auth_register_handler])
):
    try:
        command = RegisterUserCommand(email=request.email, password=request.password)
        user_id = handler.handle(command)
        return RegisterResponse(user_id=user_id)
    except ValueError as e:
        raise ValidationError(detail=str(e))


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate a user",
    description="Authenticates a user with email and password. Returns a JWT bearer token valid for 60 minutes.",
    responses={
        400: {"model": ErrorDetail, "description": "Invalid credentials (user not found or wrong password)"},
        422: {
            "model": ValidationErrorResponse,
            "description": "Validation error — invalid email format or missing field",
        },
        500: {"model": ErrorDetail, "description": "Internal server error"},
    },
)
@inject
async def login_user(request: LoginRequest, handler: LoginUserHandler = Depends(Provide[Container.auth_login_handler])):
    try:
        query = LoginUserQuery(email=request.email, password=request.password)
        result = handler.handle(query)
        return LoginResponse(
            authenticated=result["authenticated"],
            user_id=result["user_id"],
            token=result["token"],
            token_type=result["token_type"],
        )
    except ValueError as e:
        raise UnauthorizedError(detail=str(e))


@router.get(
    "/users",
    response_model=List[AuthUserResponse],
    summary="List all registered users",
    description="Returns all users registered in the authentication context. This endpoint is public.",
    responses={
        500: {"model": ErrorDetail, "description": "Internal server error"},
    },
)
@inject
async def get_users(handler: GetAuthUsersHandler = Depends(Provide[Container.auth_users_handler])):
    query = GetAuthUsersQuery()
    users = handler.handle(query)
    return [AuthUserResponse(id=u["id"], email=u["email"], is_active=u["is_active"]) for u in users]
