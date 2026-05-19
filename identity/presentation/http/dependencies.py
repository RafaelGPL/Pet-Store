from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from identity.domain.exceptions.user_exceptions import InvalidTokenException
from identity.infrastructure.security.jwt_token_service import JwtTokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        return JwtTokenService().verify_token(token)
    except InvalidTokenException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
