import psycopg2
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, Depends

from app.auth.auth import pwd_context, is_user_superadmin
from app.operations.dao import UserDAO
from app.utils.database import create_connection_users

superadmin_router = APIRouter(
    prefix="",
    tags=["superadmin"]
)

templates = Jinja2Templates(directory="templates")


@superadmin_router.get("/superadmin", response_class=HTMLResponse)
async def get_superadmin(request: Request, is_user=Depends(is_user_superadmin)):
    if is_user:
        return templates.TemplateResponse("superadmin.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@superadmin_router.post("/superadmin", response_class=HTMLResponse)
async def post_superadmin(request: Request):
    users = UserDAO.fetch_all_data()
    return templates.TemplateResponse(
        "superadmin.html",
        {
            "request": request,
            "users": users,
        },
    )


@superadmin_router.get('/get_updated_users_table', response_class=HTMLResponse)
async def get_updated_users_table(is_user=Depends(is_user_superadmin)):
    if is_user:
        try:
            users = UserDAO.fetch_all_data()
            table_html = '''
                <table>
                    <tr>
                        <th>Username</th>
                        <th>Password</th>
                        <th>Role</th>
                        <th>Is Approved</th>
                    </tr>
            '''
            for user in users:
                username = user[1]
                password = user[2]
                role = user[3]
                is_approved = "Yes" if user[4] else "No"

                table_html += f'''
                    <tr>
                        <td>{username}</td>
                        <td>{password}</td>
                        <td>{role}</td>
                        <td>{is_approved}</td>
                    </tr>
                '''
            table_html += '</table>'
            return table_html

        except Exception as e:
            return {"error": str(e)}
    else:
        return RedirectResponse(url="/")


@superadmin_router.get("/add_user", response_class=HTMLResponse)
def add_user_form(request: Request, is_user=Depends(is_user_superadmin)):
    if is_user:
        return templates.TemplateResponse("superadmin.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@superadmin_router.post("/add_user")
async def add_user(request: Request, new_username: str = Form(...), new_password: str = Form(...),
                   new_role: str = Form(...), new_approved: bool = Form(...)):
    connection = create_connection_users()
    try:
        cursor = connection.cursor()
        select_query = "SELECT COUNT(*) FROM users WHERE username = %s"
        values = (new_username,)
        cursor.execute(select_query, values)
        count = cursor.fetchone()[0]
        if count > 0:
            error_message = "Username already exists."
            return templates.TemplateResponse(
                "superadmin.html",
                {"request": request, "error": error_message, "message_color": "red", "close_add_user": False},
            )

        hashed_password = pwd_context.hash(new_password)

        insert_query = "INSERT INTO users (username, password, role, is_approved) VALUES (%s, %s, %s, %s)"
        values = (new_username, hashed_password, new_role, new_approved)
        cursor.execute(insert_query, values)
        connection.commit()

        message = "User added"
        return templates.TemplateResponse(
            "superadmin.html",
            {"request": request, "message": message, "message_color": "green", "close_add_user": True},
        )
    except Exception as e:
        error_message = str(e)
        return templates.TemplateResponse(
            "superadmin.html",
            {"request": request, "error": error_message, "message_color": "red", "close_add_user": False},
        )


@superadmin_router.get("/delete_user", response_class=HTMLResponse)
def delete_user_form(request: Request, is_user=Depends(is_user_superadmin)):
    if is_user:
        return templates.TemplateResponse("superadmin.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@superadmin_router.post("/delete_user")
async def delete_user(request: Request, username: str = Form(...)):
    connection = create_connection_users()
    try:
        cursor = connection.cursor()
        select_query = "SELECT role FROM users WHERE username = %s"
        values = (username,)
        cursor.execute(select_query, values)

        delete_query = "DELETE FROM users WHERE username = %s AND role != 'superadmin'"
        cursor.execute(delete_query, values)
        connection.commit()

        message = "User deleted"
        return templates.TemplateResponse(
            "superadmin.html",
            {"request": request, "message": message, "message_color": "green"},
        )
    except Exception as e:
        error_message = str(e)
        return templates.TemplateResponse(
            "superadmin.html",
            {"request": request, "error": error_message, "message_color": "red"},
        )


@superadmin_router.post("/assign_admin")
async def assign_admin(request: Request, username: str = Form(...)):
    connection = create_connection_users()
    try:
        cursor = connection.cursor()
        update_query = "UPDATE users SET role = 'admin', is_approved = true WHERE username = %s"
        values = (username,)
        cursor.execute(update_query, values)
        connection.commit()
        users = UserDAO.fetch_all_data()
        success = "Admin assigned"
        return templates.TemplateResponse(
            "superadmin.html",
            {
                "request": request,
                "users": users,
                "success": success,
            },
        )
    except psycopg2.Error as e:
        print("Error while connecting to PostgreSQL", e)
        return templates.TemplateResponse(
            "superadmin.html",
            {
                "request": request,
                "error": True,
            },
        )
    finally:
        connection.close()
