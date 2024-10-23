import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import traceback
from fastapi import Request, Response
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException, Request
import time

load_dotenv(find_dotenv(), override=True, verbose=True)
app = FastAPI(title="gm guanhai API", docs_url=None, redoc_url=None)
# sys.path.append('.')
from utils.log import get_logger
from routers import health, product_cate_map


from routers import (
    health,
    product_cate_map,
    publication_rewrite,
    attribute_extract,
    content_fully_rewrite,
    voc,
    business_advisor
)

logger = get_logger('gm-guanhai-aigc')


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    start = time.time()
    response = Response("Internal server error", status_code=500)
    try:
        response = await call_next(request)

    except Exception:
        error_data = [
            f"status: {response.status_code}\n",
            f"params: {request.query_params}\n",
            f"path_params: {request.url.path}\n",
            f"time: {time.time() - start}\n",
            f"traceback: {traceback.format_exc()[-2000:]}",
        ]

        error_msg = "".join(error_data)
        logger.error(error_msg)

    end = time.time()
    logger.info(
        f"{request.client.host}:{request.client.port} {request.url.path} {response.status_code} took {round(end-start,5)}"
    )
    return response


app.include_router(health.router)
app.include_router(product_cate_map.router)

app.include_router(publication_rewrite.router)
app.include_router(attribute_extract.router)
app.include_router(content_fully_rewrite.router)
app.include_router(voc.router)

app.include_router(business_advisor.router)


if __name__ == "__main__":
    uvicorn.run(app="aigc_server:app", host="0.0.0.0", port=8006, reload=True)
