from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Session, sessionmaker, declarative_base  # type: ignore[reportMissingImports]
from entities.post import PostCreate, PostUpdate, PartialPostUpdate



app = FastAPI()

# static files configuration
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates configuration
templates = Jinja2Templates(directory="templates")

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  

# Create a sessionmaker for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a base class for the SQLAlchemy models
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
Base.metadata.create_all(bind=engine)





    
    
    
# Dependency to get a database session    
def get_db():
    db = SessionLocal()
    try:
        yield db # Yield the database session to the endpoint
    finally:
        db.close()


# Home page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.id.desc()).limit(3).all()
    total_posts = db.query(Post).count()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Ana Sayfa",
            "posts": posts,
            "total_posts": total_posts,
        },
    )


@app.get("/blog", response_class=HTMLResponse)
async def blog_page(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={"title": "Blog Yazıları", "posts": posts},
    )



# Endpoint to get all posts
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()


# Post endpoint to get a specific post by ID
@app.get("/posts/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Endpoint to create a new post
@app.post("/posts")
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Endpoint to update an existing post
@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_post.title = post.title  # type: ignore[assignment]
    db_post.content = post.content # type: ignore[assignment]
    db.commit()
    db.refresh(db_post)
    return db_post

# Endpoint to partially update an existing post
@app.patch("/posts/{post_id}")
async def partial_update_post(post_id: int, post: PartialPostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    # type: ignore[assignment]
    if post.title is not None:
        db_post.title = post.title  # type: ignore
    if post.content is not None:
        db_post.content = post.content # type: ignore

    db.commit()
    db.refresh(db_post)
    return db_post

# Endpoint to delete a post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}