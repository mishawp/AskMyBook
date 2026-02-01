import sys

sys.path.insert(0, "/application")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import user_router, chat_router, document_router, auth_router
from core import (
    db_manager,
    init_db,
    init_minio,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_minio()
    await init_db()
    yield
    await db_manager.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/user")
app.include_router(chat_router, prefix="/chat")
app.include_router(document_router, prefix="/document")


@app.get("/")
async def root():
    return {"message": "Hello World"}
