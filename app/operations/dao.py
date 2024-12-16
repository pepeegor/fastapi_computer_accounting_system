from app.dao.base import BaseDAO, BaseUserDAO


class ComputerDAO(BaseDAO):

    table = 'Computer'


class ComputerComponentDAO(BaseDAO):

    table = 'ComputerComponent'


class DepartmentsDAO(BaseDAO):

    table = 'Departments'


class EmployeeDAO(BaseDAO):

    table = 'Employee'


class OrderDAO(BaseDAO):

    table = 'public.order'


class UserDAO(BaseUserDAO):

    table = 'public.users'
