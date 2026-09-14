from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controllers.auth_controller import router as auth_router
from controllers.page_controller import router as page_router
from controllers.post_controller import router as post_router
from database import Base, engine
from models import Post, User


Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Blog")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(page_router)
app.include_router(auth_router)
app.include_router(post_router)


__all__ = ["app", "Post", "User"]