from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.dependency import database
from app.config.security import api_authenticate
from app.router import router as main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.start()
    yield
    await database.end()


router = APIRouter(prefix="/api/v1", dependencies=[Depends(api_authenticate)])
router.include_router(main_router)

app = FastAPI(lifespan=lifespan, redirect_slashes=False)
app.include_router(router)


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, e: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": str(e)},
    )


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
