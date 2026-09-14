# FastAPI Blog

A blog web application built with FastAPI, SQLite, SQLAlchemy, Jinja2 templates, and JWT authentication.

The application provides a browser-based interface for reading, creating, updating, and deleting blog posts, as well as REST API endpoints for post operations.

## Features

- Homepage with recent posts and post count
- Blog post listing and detail pages
- User registration and login
- JWT bearer-token authentication
- Authenticated user profile page
- Protected post creation, update, and deletion
- SQLite database with SQLAlchemy models
- Pydantic request models in the `entities/` package
- Shared Jinja2 layout and static CSS/JavaScript files
- Responsive blog and authentication interface

## Technology Stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Jinja2
- Pydantic
- PyJWT
- Passlib with Argon2
- HTML, CSS, and JavaScript

## Project Structure

```text
FastAPI_Blog/
├── main.py
├── blog.db
├── entities/
│   ├── __init__.py
│   ├── post.py
│   └── user.py
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── posts.html
│   ├── post_detail.html
│   ├── auth.html
│   ├── profile.html
│   └── create_post.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── auth.js
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer
- pip

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install fastapi uvicorn sqlalchemy jinja2 pyjwt passlib argon2-cffi
```

## Running the Application

Start the development server from the project root:

```bash
python -m uvicorn main:app --reload
```

Open the application at:

```text
http://127.0.0.1:8000/
```

The database file is created automatically as `blog.db` when the application starts.

## Web Pages

| Route | Description |
| --- | --- |
| `/` | Homepage |
| `/blog` | Blog post listing |
| `/post/{post_id}` | Blog post detail page |
| `/auth` | Login and registration page |
| `/profile-page` | Authenticated profile page |
| `/posts/create` | Authenticated post creation page |

## Authentication

The application uses JWT tokens. After login or registration, the token is stored in the browser's `localStorage` and sent with protected requests using:

```http
Authorization: Bearer <access_token>
```

Authentication is required for:

- Creating a post through `/posts/create`
- Updating a post
- Partially updating a post
- Deleting a post
- Loading the authenticated profile

Any authenticated user can update or delete posts. Ownership and administrator roles are not used.

## API Endpoints

### Authentication

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/register` | Register a user and receive a JWT token |
| `POST` | `/login` | Authenticate a user and receive a JWT token |
| `GET` | `/profile` | Return the current user's profile |

### Posts

| Method | Route | Authentication |
| --- | --- | --- |
| `GET` | `/posts` | Not required |
| `GET` | `/posts/{post_id}` | Not required |
| `POST` | `/posts` | Not required |
| `POST` | `/posts/create` | Required |
| `PUT` | `/posts/{post_id}` | Required |
| `PATCH` | `/posts/{post_id}` | Required |
| `DELETE` | `/posts/{post_id}` | Required |

Example update request:

```http
PUT /posts/1
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
	"title": "Updated title",
	"content": "Updated content"
}
```

## Database

The application uses SQLite with this database URL:

```text
sqlite:///./blog.db
```

The database is initialized through SQLAlchemy when the application starts. The local database file is ignored by Git.

## Security Notes

Before deploying to production:

- Move `SECRET_KEY` to an environment variable.
- Use a production-grade database and migrations.
- Enable HTTPS.
- Add stricter input validation and error handling.
- Avoid exposing secrets in source code.

## Development Notes

- `main.py` contains the application, routes, authentication helpers, and SQLAlchemy models.
- `entities/` contains Pydantic request schemas.
- `templates/` contains Jinja2 pages.
- `static/css/style.css` contains the application styles.
- `static/js/auth.js` handles login, registration, logout, route guards, and post actions.
