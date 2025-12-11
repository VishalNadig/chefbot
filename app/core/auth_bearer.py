from typing import Any
from typing import Dict
from typing import Optional

from fastapi import HTTPException
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.core.auth_handler import decode_jwt


class JWTBearer(HTTPBearer):
    """Main Auth Bearer Class, handles Auth for Hypersonix Apps."""

    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Any:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=403, detail='Invalid authentication scheme.')
            user_meta = self.verify_jwt(credentials.credentials)
            if not user_meta:
                raise HTTPException(status_code=403, detail='Invalid token or expired token.')
            return user_meta
        else:
            raise HTTPException(status_code=403, detail='Invalid authorization code.')

    def verify_jwt(self, jwtoken: str) -> Dict:
        """Decode Bearer Jwt Token"""
        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = {}

        if payload:
            return payload
        return {}
