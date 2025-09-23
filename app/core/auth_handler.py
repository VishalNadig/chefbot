from typing import Dict

from decouple import config
from jose import jwt

JWT_SECRET = config('JWT_SECRET')
JWT_ALGORITHM = config('JWT_ALGORITHM')


def decode_jwt(token: str) -> Dict:
    """Decode the Internal JWT token to get user meta."""
    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[
                JWT_ALGORITHM,
            ], options={'verify_exp': False},
        )
        return payload
    except:
        return {}
