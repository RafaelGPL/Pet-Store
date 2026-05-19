import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from identity.application.services.i_token_service import ITokenService
from identity.domain.exceptions.user_exceptions import InvalidTokenException

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "petstore-dev-secret-change-in-production")
ALGORITHM = "HS256"
EXPIRE_DAYS = 90


class JwtTokenService(ITokenService):
    def create_token(self, user_id: str) -> str:
        payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(days=EXPIRE_DAYS),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise InvalidTokenException()
            return user_id
        except JWTError:
            raise InvalidTokenException()
