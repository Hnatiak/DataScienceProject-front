from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import HTMLResponse
import httpx
from fastapi.templating import Jinja2Templates
from src.services.pdf_precessing import extract_text_from_pdf
from envir_ import *
# import requests
import ast


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})


# Функція реєстрації нового користувача
@router.post("/signup")
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
                "auth/registration_success.html",
                {"request": request, "data": response_data},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                error_detail = e.response.json().get("detail", "Unprocessable Entity")
                return templates.TemplateResponse(
                    "auth/registration_failure.html",
                    {"request": request, "error": error_detail},
                )
            return templates.TemplateResponse(
                "auth/registration_failure.html", {"request": request, "error": str(e)}
            )


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


# Функція входу користувача
@router.post("/login", response_class=HTMLResponse)
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
                "auth/login_success.html", {"request": request}
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_detail = e.response.json().get("detail", "Unauthorized")
                if error_detail == "Email not confirmed":
                    return templates.TemplateResponse(
                        "auth/email_not_confirmed.html", {"request": request}
                    )
                elif error_detail == "Invalid email" or error_detail == "Invalid password":
                    return templates.TemplateResponse(
                        "auth/login_failure.html", {"request": request}
                    )
                else:
                    return templates.TemplateResponse(
                        "auth/Unauthorized.html", {"request": request}
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція виходу користувача
@router.get("/logout", response_class=HTMLResponse)
async def login_user(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token missing or invalid",
        # )
        return templates.TemplateResponse(
                    "auth/access_denied.html", {"request": request}
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
                "auth/logout.html", {"request": request}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "auth/Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

