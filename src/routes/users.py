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


# Функція перегляду користувача
@router.get("/user", response_class=HTMLResponse)
async def search_users(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return templates.TemplateResponse(
                    "auth/access_denied.html", {"request": request}
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
                "users/user.html", {"request": request, "user": user}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "auth/access_denied.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )



@router.get("/delete", response_class=HTMLResponse)
async def delete_form(request: Request):
    return templates.TemplateResponse("users/delete_or_not.html", {"request": request})

# Функція видалення користувача
@router.post("/delete", response_class=HTMLResponse)
async def delete_user(request: Request):
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

            response_users = await client.delete(
                f"{base_url}/users/me",
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
