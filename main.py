from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import jwt
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Session, sessionmaker, declarative_base  # type: ignore[reportMissingImports]
from entities.post import PostCreate, PostUpdate, PartialPostUpdate
from entities.user import UserCreate, UserLogin, UserOut
from passlib.context import CryptContext  # type: ignore[reportMissingImports]
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm




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

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = "your_secret_key"  # Replace with your own
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



# Create a base class for the SQLAlchemy models
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
Base.metadata.create_all(bind=engine)





    
    
    
# Dependency to get a database session    
def get_db():
    db = SessionLocal()
    try:
        yield db # Yield the database session to the endpoint
    finally:
        db.close()
        
# Authentication and User Management

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # type: ignore
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user         
        
        
        
# Page rendering endpoints
        
@app.get("/auth", response_class=HTMLResponse)
async def read_auth(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={
            "title": "Giriş Yap",
        },
    )

@app.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        }
    }
          
@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    
    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Şifre çok uzun. Lütfen daha kısa bir şifre seç.")
    
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "message": "Kayıt başarılı",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        }
    }


@app.get("/profile-page", response_class=HTMLResponse)
async def profile_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"title": "Profil"}
    )

@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }

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
    
@app.get("/posts/create", response_class=HTMLResponse)
async def create_post_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create_post.html",
        context={"title": "Yeni Yazı Oluştur"}
    )

@app.post("/posts/create")
async def create_post_from_form(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {
        "message": "Yazı oluşturuldu",
        "user": current_user.username,
    }
    
@app.get("/post/{post_id}", response_class=HTMLResponse)
async def post_detail_page(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post bulunamadı")

    return templates.TemplateResponse(
        request=request,
        name="post_detail.html",
        context={
            "title": post.title,
            "post": post,
        },
    )





#API -  Endpoints for Posts

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
async def update_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_post.title = post.title # type: ignore
    db_post.content = post.content # type: ignore

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
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(db_post)
    db.commit()

    return {"message": "Post deleted successfully"}




