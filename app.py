from datetime import datetime
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Header,
    Request,
    Depends,
    UploadFile,
    status,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import httpx
import uvicorn
import requests
import base64

from src.services.pdf_precessing import extract_text_from_pdf
from src.routes import upload_pdf_test

app = FastAPI()

# Підключення папки зі статичними файлами (стилі, скрипти)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення папки з шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

# base_url = "https://photoshare-python-back.onrender.com/api"
base_url = "http://localhost:8000/api"
# base_url = "https://photoshare-python-back-48d1.onrender.com/api"

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
            return response
        except httpx.ReadTimeout:
            return templates.TemplateResponse(
                # "Timeout.html", {"request": request, "message": "The request timed out. Please try again later."}
                "Timeout.html", {"request": request}
            )

app.add_middleware(TimeoutMiddleware)

def base64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")

templates.env.filters["b64encode"] = base64encode

app.include_router(upload_pdf_test.router, prefix='/pdf')


# Базовий шаблон з кнопками для запуску різних функцій
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# Функція реєстрації нового користувача
@app.post("/signup")
async def signup_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    data = {
        "username": name,
        "email": email,
        "password": password,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/signup", json=data)
            response.raise_for_status()  # Перевірка статусу відповіді
            response_data = response.json()
            return templates.TemplateResponse(
                "registration_success.html",
                {"request": request, "data": response_data},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                error_detail = e.response.json().get("detail", "Unprocessable Entity")
                return templates.TemplateResponse(
                    "registration_failure.html",
                    {"request": request, "error": error_detail},
                )
            return templates.TemplateResponse(
                "registration_failure.html", {"request": request, "error": str(e)}
            )


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Функція входу користувача
@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request, name: str = Form(...), password: str = Form(...)
):
    data = {"username": name, "password": password}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/login", data=data)
            response.raise_for_status()
            tokens = response.json()

            request.session["access_token"] = tokens["access_token"]

            return templates.TemplateResponse(
                "login_success.html", {"request": request}
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_detail = e.response.json().get("detail", "Unauthorized")
                if error_detail == "User is banned":
                    return templates.TemplateResponse(
                        "user_banned.html", {"request": request}
                    )
                elif error_detail == "Email not confirmed":
                    return templates.TemplateResponse(
                        "email_not_confirmed.html", {"request": request}
                    )
                elif error_detail == "Invalid email" or error_detail == "Invalid password":
                    return templates.TemplateResponse(
                        "login_failure.html", {"request": request}
                    )
                else:
                    return templates.TemplateResponse(
                        "Unauthorized.html", {"request": request}
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція виходу користувача
@app.get("/logout", response_class=HTMLResponse)
async def login_user(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token missing or invalid",
        # )
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_users = await client.post(
                f"{base_url}/auth/logout",
                headers=headers,
                follow_redirects=True,
            )
            request.session["access_token"] = None
            response_users.raise_for_status()
            users = response_users.json()

            return templates.TemplateResponse(
                "logout.html", {"request": request}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція перегляду користувача
@app.get("/user", response_class=HTMLResponse)
async def search_users(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_users = await client.get(
                f"{base_url}/users/me",
                headers=headers,
                # params={"limit": limit, "offset": offset},
                follow_redirects=True,
            )
            response_users.raise_for_status()
            user = response_users.json()

            return templates.TemplateResponse(
                "user.html", {"request": request, "user": user}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
            if e.response.status_code == 429:
                return templates.TemplateResponse(
                    "suspicious_activity.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )



# # Роут для відображення форми завантаження PDF
# @app.get("/upload_pdf", response_class=HTMLResponse)
# async def upload_pdf_form(request: Request):
#     return templates.TemplateResponse("upload_pdf.html", {"request": request})


# # Функція для обробки PDF
# @app.post("/upload_pdf", response_class=HTMLResponse)
# async def upload_pdf(
#     request: Request,
#     pdf: UploadFile = File(...),
#     description: str = Form(...),
# ):
#     access_token = request.session.get("access_token")
#     if not access_token:
#         # Відмовити у доступі, якщо токен відсутній
#         return templates.TemplateResponse("access_denied.html", {"request": request})

#     # Отримання тексту з PDF (функція повинна бути реалізована окремо)
#     pdf_text = extract_text_from_pdf(pdf.file)


#     async with httpx.AsyncClient() as client:
#         form_data = {
#             "description": description,
#             "text": pdf_text,
#         }

#         headers = {"Authorization": f"Bearer {access_token}"}

#         response = requests.post(
#             f"{base_url}/pdf/upload_new_pdf", headers=headers, data=form_data
#         )

#         response.raise_for_status()
#         ansver_from = response.json()

#     return templates.TemplateResponse("/upload_pdf_success.html", {"request": request, "pdf_text": ansver_from})



if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True, log_level="info")
