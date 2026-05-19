import uuid

from identity.application.dto.user_dto import UserDto
from identity.application.queries.get_current_user_query import GetCurrentUserQuery
from identity.domain.exceptions.user_exceptions import UserNotFoundException
from identity.domain.repositories.i_user_repository import IUserRepository


class GetCurrentUserHandler:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def handle(self, query: GetCurrentUserQuery) -> UserDto:
        user = self._user_repository.find_by_id(uuid.UUID(query.user_id))
        if user is None:
            raise UserNotFoundException(query.user_id)
        return UserDto.from_user(user)
