from fastapi import (
    FastAPI,
    Request,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import httpx
import uvicorn
import base64


from src.routes import upload_pdf, auth, users

app = FastAPI()

# Підключення папки зі статичними файлами (стилі, скрипти)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення папки з шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

base_url = "http://localhost:8000/api"

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
            return response
        except httpx.ReadTimeout:
            return templates.TemplateResponse(
                "Timeout.html", {"request": request}
            )

app.add_middleware(TimeoutMiddleware)

def base64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")

templates.env.filters["b64encode"] = base64encode

app.include_router(upload_pdf.router)
app.include_router(auth.router)
app.include_router(users.router)


# Базовий шаблон з кнопками для запуску різних функцій
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})



if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True, log_level="info")
