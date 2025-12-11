import uuid
from typing import Any
from typing import Dict
from typing import Optional

from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from fastapi_pagination import add_pagination
# from fastapi_redis_cache import FastApiRedisCache
# from sqlalchemy.orm import Session

app = FastAPI()
# add_pagination(app)


origins = [
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


