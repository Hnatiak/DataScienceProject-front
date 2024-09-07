from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import httpx
import requests
from fastapi.templating import Jinja2Templates
from src.services.pdf_precessing import extract_text_from_pdf
from envir_ import *

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/PDF",tags=["PDF"])


# Роут для відображення форми завантаження PDF
@router.get("/upload_pdf", response_class=HTMLResponse)
async def upload_pdf_form(request: Request):
    return templates.TemplateResponse("upload_pdf.html", {"request": request})


# Функція для обробки PDF
@router.post("/upload_pdf", response_class=HTMLResponse)
async def upload_pdf(
    request: Request,
    pdf: UploadFile = File(...),
    description: str = Form(...),
):
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("access_denied.html", {"request": request})

    # Отримання тексту з PDF (функція повинна бути реалізована окремо)
    pdf_text = await extract_text_from_pdf(pdf.file)


    async with httpx.AsyncClient() as client:
        form_data = {
            "description": description,
            "text": pdf_text,
        }

        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.post(
            f"{base_url}/upload_new_pdf", headers=headers, data=form_data
        )

        response.raise_for_status()

    return templates.TemplateResponse("upload_success.html", {"request": request, "pdf_text": pdf_text})
