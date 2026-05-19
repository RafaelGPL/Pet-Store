from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

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
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str


class MeResponse(BaseModel):
    user_id: str
    username: str


# --- dependencies ---


def _repo() -> SqliteUserRepository:
    return SqliteUserRepository()


def _password_svc() -> BcryptPasswordService:
    return BcryptPasswordService()


def _token_svc() -> JwtTokenService:
    return JwtTokenService()


# --- routes ---


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(body: RegisterRequest):
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


@router.post("/token", response_model=TokenResponse)
def get_token(form: OAuth2PasswordRequestForm = Depends()):
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


@router.get("/me", response_model=MeResponse)
def me(user_id: str = Depends(get_current_user_id)):
    try:
        dto = GetCurrentUserHandler(_repo()).handle(GetCurrentUserQuery(user_id=user_id))
    except UserNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return MeResponse(user_id=dto.id, username=dto.username)
