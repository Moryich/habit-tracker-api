from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.routes.user import user
from app.routes.habit import habit
from app.routes.auth import auth

app = FastAPI()
app.include_router(habit)
app.include_router(auth)
app.include_router(user)

@app.exception_handler(AppException)
def exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
