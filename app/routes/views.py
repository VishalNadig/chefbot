from fastapi import APIRouter
from fastapi.responses import Response
from fastapi_pagination import Page
from fastapi_pagination import paginate
from fastapi_pagination.bases import AbstractPage
from fastapi_redis_cache import cache

from app.core import datastore
from app.routes.models import User
from app.routes.models import users

# from fastapi import Depends
# from app.core.auth_bearer import JWTBearer

router = APIRouter()


# Sample endpoint with Auth
@router.get("/info")
@cache()
def index() -> Response:
    # user: Dict = Depends(JWTBearer()) {for auth}
    """Index Url.

    Returns:
        [response or HTTPException]: 200 if the app is up with db connected or
        204 if db not connected.
    """
    status_code = 200
    try:
        datastore_ = datastore.get_datastore()
        with datastore_() as datastore_session:
            conn = datastore_session.connection()
            conn.close()
    except Exception as _:
        status_code = 204
    return Response(status_code=status_code)


# Sample endpoint with Pagination
@router.get("/users", response_model=Page[User])
async def get_users() -> AbstractPage[User]:
    """Pagination Example using dummy data."""
    return paginate(users)
