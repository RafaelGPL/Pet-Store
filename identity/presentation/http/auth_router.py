from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from identity.application.commands.register_user_command import RegisterUserCommand
from identity.application.handlers.authenticate_user_handler import AuthenticateUserHandler
from identity.application.handlers.get_current_user_handler import GetCurrentUserHandler
from identity.application.handlers.register_user_handler import RegisterUserHandler
from identity.application.queries.authenticate_user_query import AuthenticateUserQuery
from identity.application.queries.get_current_user_query import GetCurrentUserQuery
from identity.domain.exceptions.user_exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from identity.infrastructure.persistence.sqlite_user_repository import SqliteUserRepository
from identity.infrastructure.security.bcrypt_password_service import BcryptPasswordService
from identity.infrastructure.security.jwt_token_service import JwtTokenService
from identity.presentation.http.dependencies import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"], redirect_slashes=False)


# --- Pydantic models ---


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        examples=["alice"],
        description="3–50 characters; letters, numbers, hyphens, and underscores only. "
        "Stored in lowercase.",
    )
    password: str = Field(
        min_length=1,
        examples=["s3cr3tA!"],
        description="Plain-text password. Stored as a bcrypt hash; never logged or returned.",
    )


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT Bearer token. Pass as `Authorization: Bearer <token>`.")
    token_type: str = Field(examples=["bearer"])
    user_id: str = Field(description="UUID of the newly created / authenticated user.")
    username: str = Field(examples=["alice"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "username": "alice",
            }
        }
    }


class MeResponse(BaseModel):
    user_id: str = Field(description="UUID of the authenticated user.")
    username: str = Field(examples=["alice"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "username": "alice",
            }
        }
    }


# --- dependencies ---


def _repo() -> SqliteUserRepository:
    return SqliteUserRepository()


def _password_svc() -> BcryptPasswordService:
    return BcryptPasswordService()


def _token_svc() -> JwtTokenService:
    return JwtTokenService()


# --- routes ---


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenResponse,
    summary="Register a new user",
    responses={
        409: {"description": "Username already taken."},
        422: {"description": "Username or password failed validation rules."},
    },
)
def register(body: RegisterRequest):
    """
    Create a new user account and immediately return a Bearer token.

    - **username**: 3–50 characters, alphanumeric + hyphens/underscores, normalised to lowercase.
    - **password**: any non-empty string; stored as a bcrypt hash.

    Use the returned `access_token` in an `Authorization: Bearer <token>` header on all
    subsequent requests.
    """
    try:
        dto = RegisterUserHandler(_repo(), _password_svc(), _token_svc()).handle(
            RegisterUserCommand(username=body.username, password=body.password)
        )
    except UserAlreadyExistsException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return TokenResponse(
        access_token=dto.access_token,
        token_type="bearer",
        user_id=dto.id,
        username=dto.username,
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Log in (OAuth2 password flow)",
    responses={
        401: {"description": "Invalid username or password."},
    },
)
def get_token(form: OAuth2PasswordRequestForm = Depends()):
    """
    Exchange credentials for a Bearer token using the **OAuth2 password flow**.

    Send `username` and `password` as **form data** (not JSON).
    This endpoint is also used by the Swagger UI "Authorize" button.
    """
    try:
        dto = AuthenticateUserHandler(_repo(), _password_svc(), _token_svc()).handle(
            AuthenticateUserQuery(username=form.username, password=form.password)
        )
    except InvalidCredentialsException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=dto.access_token,
        token_type="bearer",
        user_id=dto.id,
        username=dto.username,
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get the current user",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        404: {"description": "Token is valid but the user no longer exists."},
    },
)
def me(user_id: str = Depends(get_current_user_id)):
    """
    Return the `user_id` and `username` of the currently authenticated user.

    Requires a valid `Authorization: Bearer <token>` header.
    """
    try:
        dto = GetCurrentUserHandler(_repo()).handle(GetCurrentUserQuery(user_id=user_id))
    except UserNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return MeResponse(user_id=dto.id, username=dto.username)
