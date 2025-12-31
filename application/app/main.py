from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import user_router
from core.database import db_manager, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    db_manager.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(user_router, prefix="/user")


@app.get("/")
async def root():
    return {"message": "Hello World"}
