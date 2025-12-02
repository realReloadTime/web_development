from datetime import datetime, timedelta, UTC

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext

from backend.config import settings
from backend.repository.user import UserRepository, get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------- Password Hashing -------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ------------------- JWT Token Handling -------------------
def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + expires_delta

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# ------------------- User Authentication -------------------
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        repo: UserRepository = Depends(get_user_repository)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token has expired."
        )

    except JWTError:
        raise credentials_exception

    user = await repo.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user


def create_refresh_token(data: dict) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(UTC) + expires_delta

    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


async def get_current_user_refresh(
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="users/refresh")),
        repo: UserRepository = Depends(get_user_repository)
):
    try:
        payload = jwt.decode(
            token,
            settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await repo.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
