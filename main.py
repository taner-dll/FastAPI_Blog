from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Session, sessionmaker, declarative_base  # type: ignore[reportMissingImports]

app = FastAPI()
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




# Pydantic models for request and response validation
class PostCreate(BaseModel):
    title: str
    content: str
    
class PostUpdate(BaseModel):
    title: str
    content: str
    
class PartialPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    
    
    
# Dependency to get a database session    
def get_db():
    db = SessionLocal()
    try:
        yield db # Yield the database session to the endpoint
    finally:
        db.close()


# Root endpoint
@app.get("/")
async def read_root():
    return {"Hello": "World"}

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

    db_post.title = post.title
    db_post.content = post.content

    db.commit()
    db.refresh(db_post)
    return db_post

# Endpoint to partially update an existing post
@app.patch("/posts/{post_id}")
async def partial_update_post(post_id: int, post: PartialPostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.title is not None:
        db_post.title = post.title
    if post.content is not None:
        db_post.content = post.content

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