from identity.application.dto.user_dto import UserDto
from identity.application.queries.authenticate_user_query import AuthenticateUserQuery
from identity.application.services.i_password_service import IPasswordService
from identity.application.services.i_token_service import ITokenService
from identity.domain.exceptions.user_exceptions import InvalidCredentialsException
from identity.domain.repositories.i_user_repository import IUserRepository


class AuthenticateUserHandler:
    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    def handle(self, query: AuthenticateUserQuery) -> UserDto:
        user = self._user_repository.find_by_username(query.username.lower())
        if user is None:
            raise InvalidCredentialsException()
        if not self._password_service.verify(query.password, user.password_hash):
            raise InvalidCredentialsException()

        token = self._token_service.create_token(str(user.id))
        return UserDto.from_user(user, access_token=token)
