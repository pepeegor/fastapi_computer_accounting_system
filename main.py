from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.admin.router import admin_router
from app.auth.router import auth_router
from app.operations.router import api_router
import uvicorn
from app.superadmin.router import superadmin_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.include_router(api_router)
app.include_router(auth_router)
app.include_router(superadmin_router)
app.include_router(admin_router)

templates = Jinja2Templates(directory="templates")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)