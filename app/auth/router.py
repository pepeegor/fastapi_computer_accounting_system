from datetime import timedelta

import psycopg2
from fastapi import APIRouter, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request


from app.auth.auth import pwd_context, ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.database import create_connection_users
from app.auth.auth import create_access_token, verify_password

auth_router = APIRouter(
    prefix="",
    tags=["api"]
)

templates = Jinja2Templates(directory="templates")


@auth_router.get("/", response_class=HTMLResponse)
async def login(request: Request, error: bool = False):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@auth_router.post("/", response_class=HTMLResponse)
async def login_post(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    connection = create_connection_users()
    try:
        cursor = connection.cursor()
        select_query = "SELECT password, role, is_approved FROM users WHERE username = %s"
        values = (username,)
        cursor.execute(select_query, values)
        result = cursor.fetchone()

        if result and verify_password(password, result[0]):
            if result[2]:  # Check if the user is approved
                user_data = {"sub": username, "role": result[1], "is_approved": result[2]}
                access_token = create_access_token(user_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
                request.session["access_token"] = access_token

                if result[1] == "superadmin":
                    return RedirectResponse(url="/superadmin")
                elif result[1] == "admin":
                    return RedirectResponse(url="/admin")
                else:
                    return RedirectResponse(url="/home")
            else:
                # User is not approved, redirect to waiting page
                return RedirectResponse(url="/waiting_approval")
        else:
            return templates.TemplateResponse("login.html", {"request": request, "error": True})
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL", e)
        return templates.TemplateResponse("login.html", {"request": request, "error": True})
    finally:
        cursor.close()
        connection.close()


# Добавьте зависимость get_current_user для проверки токена доступа
@auth_router.get("/waiting_approval")
async def waiting_approval(request: Request):
    return templates.TemplateResponse("waiting_approval.html", {"request": request})


@auth_router.post("/waiting_approval", response_class=HTMLResponse)
async def waiting_approval(request: Request):
    return templates.TemplateResponse("waiting_approval.html", {"request": request})


@auth_router.get("/register", response_class=HTMLResponse)
async def reg_page(request: Request, error: bool = False):
    return templates.TemplateResponse("register.html", {"request": request, "error": error})


@auth_router.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    # Проверка совпадения паролей
    if password != confirm_password:
        error_message = "Passwords do not match."
        return templates.TemplateResponse("register.html", {"request": request, "error": error_message})

    # Проверка, что пользователь с таким именем пользователя не существует
    connection = create_connection_users()
    try:
        cursor = connection.cursor()
        select_query = "SELECT COUNT(*) FROM users"
        cursor.execute(select_query)
        count = cursor.fetchone()[0]

        if count == 0:
            role = "superadmin"
            is_approved = True
        else:
            role = "user"
            is_approved = False

        select_query = "SELECT COUNT(*) FROM users WHERE username = %s"
        values = (username,)
        cursor.execute(select_query, values)
        count = cursor.fetchone()[0]
        if count > 0:
            error_message = "Username already exists."
            return templates.TemplateResponse("register.html", {"request": request, "error": error_message})

        hashed_password = pwd_context.hash(password)

        insert_query = "INSERT INTO users (username, password, role, is_approved) VALUES (%s, %s, %s, %s)"
        values = (username, hashed_password, role, is_approved)
        cursor.execute(insert_query, values)
        connection.commit()

    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL", e)
        error_message = "An error occurred. Please try again later."
        return templates.TemplateResponse("register.html", {"request": request, "error": error_message})
    finally:
        connection.close()

    return RedirectResponse(url="/")


@auth_router.get("/logout")
async def logout(request: Request):
    if "access_token" in request.session:
        del request.session["access_token"]
    return RedirectResponse(url="/")
