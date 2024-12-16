from pydantic import BaseModel, Field


class Computer(BaseModel):
    id: int
    computer_model: str
    year_of_manufacture: int
    employee_id: int


class ComputerComponent(BaseModel):
    id: int
    component_type: str
    component_model: str
    manufacturer: str
    computer_id: int


class Departments(BaseModel):
    id: int
    department_name: str


class Employee(BaseModel):
    id: int
    last_name: str
    first_name: str
    post: str
    department_id: int


class Order(BaseModel):
    id: int
    order_date: str = Field(examples=["1-1-0000"])
    employee_id: int
    component_id: int


class UserCreate(BaseModel):
    username: str
    password: str
