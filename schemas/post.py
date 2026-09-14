from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str
    content: str


class PartialPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None