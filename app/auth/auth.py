import psycopg2
from fastapi import FastAPI, Request, Form, Depends, Response, Cookie
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.utils.database import create_connection_users

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# Функция для проверки хэша пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Функция для создания токена доступа
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_access_token(request: Request):
    return request.session.get("access_token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           access_token: str = Depends(get_access_token)):
    try:
        token = access_token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        connection = create_connection_users()
        cursor = connection.cursor()
        select_query = "SELECT username, role, is_approved FROM users WHERE username = %s"
        values = (username,)
        cursor.execute(select_query, values)
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        user_data = {
            "username": result[1],
            "role": result[2],
            "is_approved": result[3]
        }
        return user_data
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL", e)
        raise HTTPException(status_code=500, detail="Database error")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def is_user_superadmin(access_token: str = Depends(get_access_token)) -> bool:
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            if role == "superadmin":
                return True
        except JWTError:
            pass
    return False


def is_user_admin(access_token: str = Depends(get_access_token)) -> bool:
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            if role == "admin":
                return True
        except JWTError:
            pass
    return False


def is_user_approved(access_token: str = Depends(get_access_token)) -> bool:
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            is_approved = payload.get("is_approved")
            if is_approved:
                return True
        except JWTError:
            pass
    return False