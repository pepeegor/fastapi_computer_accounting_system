from datetime import datetime, date
import json
import psycopg2
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, HTTPException, Depends, Response, UploadFile, File
from starlette.responses import JSONResponse

from app.auth.auth import pwd_context, is_user_superadmin, is_user_admin, is_user_approved
from app.operations.dao import ComputerDAO, ComputerComponentDAO, DepartmentsDAO, OrderDAO, EmployeeDAO, UserDAO
from app.operations.schemas import Computer, ComputerComponent, Departments, Order, Employee, UserCreate
from app.utils.database import create_connection_users


admin_router = APIRouter(
    prefix="",
    tags=["admin"]
)

templates = Jinja2Templates(directory="templates")


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


@admin_router.get("/admin", response_class=HTMLResponse)
async def get_admin(request: Request, is_user=Depends(is_user_admin)):
    if is_user:
        return templates.TemplateResponse("admin.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@admin_router.post("/approve_user", response_class=HTMLResponse, dependencies=[Depends(is_user_admin)])
def approve_user_post(request: Request, username: str = Form(...)):
    UserDAO.approve_user(username)
    users = UserDAO.fetch_req("false")
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "users": users
        },
    )


@admin_router.post("/admin", response_class=HTMLResponse, dependencies=[Depends(is_user_admin)])
def post_admin(request: Request):
    users = UserDAO.fetch_req("false")

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "users": users
        },
    )


@admin_router.get("/home_admin", response_class=HTMLResponse)
async def get_home_admin(request: Request, is_user=Depends(is_user_admin), is_user_super=Depends(is_user_superadmin)):
    if is_user or is_user_super:
        computer_data = ComputerDAO.fetch_all_data()
        computer_component_data = ComputerComponentDAO.fetch_all_data()
        department_data = DepartmentsDAO.fetch_all_data()
        employee_data = EmployeeDAO.fetch_all_data()

        return templates.TemplateResponse(
            "home_admin.html",
            {
                "request": request,
                "computer_data": computer_data,
                "computer_component_data": computer_component_data,
                "department_data": department_data,
                "employee_data": employee_data,
            },
        )
    else:
        return RedirectResponse(url="/")


@admin_router.post("/home_admin", response_class=HTMLResponse)
def post_home_admin(request: Request):
    computer_data = ComputerDAO.fetch_all_data()
    computer_component_data = ComputerComponentDAO.fetch_all_data()
    department_data = DepartmentsDAO.fetch_all_data()
    employee_data = EmployeeDAO.fetch_all_data()

    return templates.TemplateResponse(
        "home_admin.html",
        {
            "request": request,
            "computer_data": computer_data,
            "computer_component_data": computer_component_data,
            "department_data": department_data,
            "employee_data": employee_data,
        },
    )


@admin_router.get("/order_page", response_class=HTMLResponse)
def order_page_get(request: Request,  is_user=Depends(is_user_admin), is_user_super=Depends(is_user_superadmin)):
    if is_user or is_user_super:
        order_data = OrderDAO.fetch_all_data()

        return templates.TemplateResponse(
            "order_page.html",
            {
                "request": request,
                "order_data": order_data,
            },
        )
    else:
        return RedirectResponse(url="/")


@admin_router.post("/order_page", response_class=HTMLResponse)
def order_page_post(request: Request):
    order_data = OrderDAO.fetch_all_data()

    return templates.TemplateResponse(
        "order_page.html",
        {
            "request": request,
            "orders": order_data,
        },
    )


@admin_router.get("/delete_data", response_class=HTMLResponse)
async def get_delete_data(request: Request, is_user=Depends(is_user_admin), is_user_super=Depends(is_user_superadmin)):
    if is_user or is_user_super:
        return templates.TemplateResponse("delete_data.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@admin_router.post("/delete_data", response_class=HTMLResponse)
async def post_delete_data(request: Request):
    data = await request.form()
    table_name = data.get("table_name")
    if table_name == "Computer":
        return templates.TemplateResponse("delete_data_computer.html", {"request": request})
    elif table_name == "ComputerComponent":
        return templates.TemplateResponse("delete_data_computercomponent.html", {"request": request})
    elif table_name == "Departments":
        return templates.TemplateResponse("delete_data_departments.html", {"request": request})
    else:
        return templates.TemplateResponse("delete_data_employee.html", {"request": request})


@admin_router.post("/delete_data/computer", response_class=HTMLResponse)
async def post_delete_computer(request: Request):
    data = await request.form()
    computer_id = int(data.get("computer_id"))
    check = ComputerDAO.delete_data(computer_id)
    if check:
        success = "Data deleted."
        return templates.TemplateResponse("delete_data_computer.html", {"request": request, "success": success})
    else:
        error_message = "An error occurred. Сheck the entered data."
        return templates.TemplateResponse("delete_data_computer.html", {"request": request, "error": error_message})


@admin_router.post("/delete_data/computercomponent", response_class=HTMLResponse)
async def post_delete_components(request: Request):
    data = await request.form()
    component_id = int(data.get("component_id"))
    check = ComputerComponentDAO.delete_data(component_id)
    if check:
        success = "Data deleted."
        return templates.TemplateResponse("delete_data_computercomponent.html", {"request": request, "success": success})
    else:
        error_message = "An error occurred. Сheck the entered data."
        return templates.TemplateResponse("delete_data_computercomponent.html", {"request": request, "error": error_message})


@admin_router.post("/delete_data/departments", response_class=HTMLResponse)
async def post_delete_deps(request: Request):
    data = await request.form()
    department_id = int(data.get("department_id"))
    check = DepartmentsDAO.delete_data(department_id)
    if check:
        success = "Data deleted."
        return templates.TemplateResponse("delete_data_departments.html", {"request": request, "success": success})
    else:
        error_message = "An error occurred. Сheck the entered data."
        return templates.TemplateResponse("delete_data_departments.html", {"request": request, "error": error_message})


@admin_router.post("/delete_data/employee", response_class=HTMLResponse)
async def post_delete_deps(request: Request):
    data = await request.form()
    employee_id = int(data.get("employee_id"))
    check = EmployeeDAO.delete_data(employee_id)
    if check:
        success = "Data deleted."
        return templates.TemplateResponse("delete_data_employee.html", {"request": request, "success": success})
    else:
        error_message = "An error occurred. Сheck the entered data."
        return templates.TemplateResponse("delete_data_employee.html", {"request": request, "error": error_message})


@admin_router.get("/order_page/clear", response_class=HTMLResponse)
async def clear_orders(request: Request, is_user=Depends(is_user_admin), is_user_super=Depends(is_user_superadmin)):
    if is_user or is_user_super:
        OrderDAO.truncate_table()
        return templates.TemplateResponse("order_page.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@admin_router.get("/export_data")
async def export_data(is_user=Depends(is_user_admin), is_user_super=Depends(is_user_superadmin)):
    if is_user or is_user_super:
        computer_data = ComputerDAO.fetch_all_data()
        computercomponent_data = ComputerComponentDAO.fetch_all_data()
        departments_data = DepartmentsDAO.fetch_all_data()
        employee_data = EmployeeDAO.fetch_all_data()
        order_data = OrderDAO.fetch_all_data()

        data = {
            "Computer": computer_data,
            "ComputerComponent": computercomponent_data,
            "Departments": departments_data,
            "Employee": employee_data,
            "Order": order_data
        }

        json_data = json.dumps(data, cls=DateEncoder)
        temp_file = "data.json"

        with open(temp_file, "w") as file:
            file.write(json_data)

        return FileResponse(temp_file, filename="data.json", media_type="application/json")
    else:
        return RedirectResponse(url="/")


@admin_router.post("/import_data")
async def import_data(file: UploadFile = File(...), is_user=Depends(is_user_admin), is_user_super=Depends(is_user_superadmin)):
    if is_user or is_user_super:
        try:
            contents = await file.read()
            data = json.loads(contents)

            departments_data = data.get("Departments", [])
            for department in departments_data:
                department_name = department[1]

                values = (department_name,)
                DepartmentsDAO.add_data(values)

            employee_data = data.get("Employee", [])
            for employee in employee_data:
                last_name = employee[1]
                first_name = employee[2]
                post = employee[3]
                department_id = employee[4]

                values = (last_name, first_name, post, department_id)
                EmployeeDAO.add_data(values)

            computer_data = data.get("Computer", [])
            for computer in computer_data:
                computer_model = computer[1]
                year_of_manufacture = computer[2]
                employee_id = computer[3]

                values = (computer_model, year_of_manufacture, employee_id)
                ComputerDAO.add_data(values)

            computercomponent_data = data.get("ComputerComponent", [])
            for computercomponent in computercomponent_data:
                component_type = computercomponent[1]
                component_model = computercomponent[2]
                manufacturer = computercomponent[3]
                computer_id = computercomponent[4]

                values = (component_type, component_model, manufacturer, computer_id)
                ComputerComponentDAO.add_data(values)


            order_data = data.get("Order", [])
            for order in order_data:
                order_date = order[1]
                employee_id = order[2]
                component_id = order[3]

                values = (order_date, employee_id, component_id)
                OrderDAO.add_data(values)

            # Возвращаем успешный ответ
            return RedirectResponse(url="/home_admin")
        except Exception as e:
            return JSONResponse(content={"message": "Error importing data", "error": str(e)})
    else:
        return RedirectResponse(url="/")