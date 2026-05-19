from passlib.context import CryptContext

from identity.application.services.i_password_service import IPasswordService


class BcryptPasswordService(IPasswordService):
    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain: str) -> str:
        return self._context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._context.verify(plain, hashed)
