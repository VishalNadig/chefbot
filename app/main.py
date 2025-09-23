import uuid
from typing import Any
from typing import Dict
from typing import Optional

import loguru
from decouple import config
from elasticapm.contrib.starlette import ElasticAPM
from elasticapm.contrib.starlette import make_apm_client
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from fastapi_redis_cache import FastApiRedisCache
from sqlalchemy.orm import Session

from app.routes import views

apm = make_apm_client()
app = FastAPI()
app.include_router(views.router)

app.add_middleware(ElasticAPM, client=apm)
add_pagination(app)

logger = loguru.logger
logger.remove()

log_file = open('app/logs/logs.log', 'a')
logger.add(
    log_file,
    format='{time} - {level} - ({extra[request_id]}) {message} ',
    level='DEBUG',
    serialize=True,
)

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


@app.middleware('http')
async def request_middleware(request: Request, call_next: Any) -> Optional[Dict]:
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    with logger.contextualize(request_id=request_id):
        logger.info('Request started')

        try:
            response = await call_next(request)

        except Exception as ex:
            logger.error(f'Request failed: {ex}')
            response = JSONResponse(
                content={
                    'info':
                        {
                            'success': False,
                            'response': 'Internal Server Error',
                        },
                    'request_id': request_id,
                }, status_code=500,
            )

        finally:
            response.headers['X-Request-ID'] = request_id
            logger.info('Request ended')
            return response


@app.on_event('startup')
def startup() -> None:
    """Load Redis cache on startup."""
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=f"redis://:{config('REDIS_PASSWORD')}@{config('REDIS_HOST')}:{config('REDIS_PORT')}",  # noqa
        prefix='myapi-cache',
        response_header='X-MyAPI-Cache',
        ignore_arg_types=[Request, Response, Session],
    )
