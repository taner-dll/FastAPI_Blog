from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.post import Post
from models.user import User
from schemas.post import PostCreate


router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/auth")
async def auth_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"title": "Login"},
    )


@router.get("/profile-page")
async def profile_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"title": "Profile"},
    )


@router.get("/")
async def home_page(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.id.desc()).limit(3).all()
    total_posts = db.query(Post).count()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Home",
            "posts": posts,
            "total_posts": total_posts,
        },
    )


@router.get("/blog")
async def blog_page(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={"title": "Blog Posts", "posts": posts},
    )


@router.get("/posts/create")
async def create_post_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create_post.html",
        context={"title": "Create a Post"},
    )


@router.post("/posts/create")
async def create_post_from_form(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {"message": "Post created", "user": current_user.username}


@router.get("/post/{post_id}")
async def post_detail_page(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        request=request,
        name="post_detail.html",
        context={"title": post.title, "post": post},
    )