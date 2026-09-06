import uuid
from datetime import datetime, timezone

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Response, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel, EmailStr, Field

from auth.deps import get_current_user
from core.config import settings
from core.security import create_jwt, hash_password, verify_password
from db.database import get_db
from db.models import serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "access_token"

USER_COLUMNS = "id, email, name, picture, password_hash, google_sub, created_at"


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthIn(BaseModel):
    credential: str


class SetPasswordIn(BaseModel):
    password: str = Field(min_length=8, max_length=128)


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
        max_age=settings.JWT_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, response: Response, pool=Depends(get_db)):
    email = body.email.lower()
    existing = await pool.fetchval("SELECT 1 FROM users WHERE email = $1", email)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    doc = {
        "id": uuid.uuid4().hex,
        "email": email,
        "name": body.name.strip(),
        "password_hash": hash_password(body.password),
        "google_sub": None,
        "picture": None,
        "created_at": datetime.now(timezone.utc),
    }
    try:
        await pool.execute(
            f"INSERT INTO users ({USER_COLUMNS}) VALUES ($1, $2, $3, $4, $5, $6, $7)",
            doc["id"], doc["email"], doc["name"], doc["picture"],
            doc["password_hash"], doc["google_sub"], doc["created_at"],
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    _set_session_cookie(response, create_jwt(doc["id"], email))
    return {"user": serialize_user(doc)}


@router.post("/login")
async def login(body: LoginIn, response: Response, pool=Depends(get_db)):
    user = await pool.fetchrow(
        f"SELECT {USER_COLUMNS} FROM users WHERE email = $1", body.email.lower()
    )
    if user and not user["password_hash"]:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "This account uses Google sign-in. Use 'Continue with Google' below.",
        )
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    _set_session_cookie(response, create_jwt(user["id"], user["email"]))
    return {"user": serialize_user(user)}


@router.post("/google")
async def google_auth(body: GoogleAuthIn, response: Response, pool=Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Google sign-in is not configured",
        )

    try:
        info = id_token.verify_oauth2_token(
            body.credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google credential")

    if not info.get("email_verified"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Google account email not verified")

    google_sub = info["sub"]
    email = info["email"].lower()
    name = (info.get("name") or email.split("@")[0]).strip()
    picture = info.get("picture")

    user = await pool.fetchrow(
        f"SELECT {USER_COLUMNS} FROM users WHERE google_sub = $1", google_sub
    )
    if not user:
        user = await pool.fetchrow(
            f"SELECT {USER_COLUMNS} FROM users WHERE email = $1", email
        )
        if user and not user["google_sub"]:
            await pool.execute(
                "UPDATE users SET google_sub = $1 WHERE id = $2", google_sub, user["id"]
            )
            user = dict(user) | {"google_sub": google_sub}
        elif user:
            user = dict(user)
        else:
            try:
                await pool.execute(
                    f"INSERT INTO users ({USER_COLUMNS}) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    uuid.uuid4().hex, email, name, picture, None, google_sub,
                    datetime.now(timezone.utc),
                )
            except asyncpg.UniqueViolationError:
                user = await pool.fetchrow(
                    f"SELECT {USER_COLUMNS} FROM users WHERE email = $1", email
                ) or None

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Google login failed")

    _set_session_cookie(response, create_jwt(user["id"], user["email"]))
    return {"user": serialize_user(user)}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user": serialize_user(user)}


@router.post("/set-password")
async def set_password(
    body: SetPasswordIn,
    user=Depends(get_current_user),
    pool=Depends(get_db),
):
    await pool.execute(
        "UPDATE users SET password_hash = $1 WHERE id = $2",
        hash_password(body.password), user["id"],
    )
    return {"message": "Password updated"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Logged out"}