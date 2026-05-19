from identity.application.commands.register_user_command import RegisterUserCommand
from identity.application.dto.user_dto import UserDto
from identity.application.services.i_password_service import IPasswordService
from identity.application.services.i_token_service import ITokenService
from identity.domain.exceptions.user_exceptions import UserAlreadyExistsException
from identity.domain.model.user import User
from identity.domain.model.username import Username
from identity.domain.repositories.i_user_repository import IUserRepository


class RegisterUserHandler:
    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    def handle(self, command: RegisterUserCommand) -> UserDto:
        username = Username(value=command.username)
        if self._user_repository.find_by_username(username.value) is not None:
            raise UserAlreadyExistsException(username.value)

        password_hash = self._password_service.hash(command.password)
        user = User.register(username=username, password_hash=password_hash)
        self._user_repository.save(user)

        token = self._token_service.create_token(str(user.id))
        return UserDto.from_user(user, access_token=token)
