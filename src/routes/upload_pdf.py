from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import HTMLResponse
import httpx
from fastapi.templating import Jinja2Templates
from src.services.pdf_precessing import extract_text_from_pdf
from envir_ import *
# import requests
import ast
from typing import Optional


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# Роут для відображення форми завантаження PDF
@router.get("/upload_pdf", response_class=HTMLResponse)
async def upload_pdf_form(request: Request):

    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("auth/access_denied.html", {"request": request})

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.post(
                f"{base_url}/pdf/request_for_title_docs/", headers=headers          #, data=form_data
            )
            response.raise_for_status()
            ansver_from = response.json()

            return templates.TemplateResponse("pdf/upload_pdf.html", {"request": request, "documents": ansver_from})
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "auth/access_denied.html", {"request": request}
                )
            # if e.response.status_code == 429:
            #     return templates.TemplateResponse(
            #         "suspicious_activity.html", {"request": request}
            #     )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )



# Функція для завантаження тексту з ПДФ док-ту
@router.post("/upload_pdf", response_class=HTMLResponse)
async def upload_pdf(
    request: Request,
    pdf: UploadFile = File(...),
    
):
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("auth/access_denied.html", {"request": request})

    # Отримання тексту з PDF (функція повинна бути реалізована окремо)
    try:
        pdf_text = extract_text_from_pdf(pdf.file)
    except:
        return templates.TemplateResponse("pdf/no_text.html", {"request": request})

    try:
        async with httpx.AsyncClient() as client:
            form_data = {
                "description": pdf.filename,
                "text": pdf_text,
            }

            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.post(
                f"{base_url}/pdf/upload_new_pdf_test/", headers=headers, data=form_data
            )

            response.raise_for_status()
            # ansver_from = response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            return templates.TemplateResponse(
                "pdf/document_exists.html", {"request": request}
            )

    return templates.TemplateResponse("pdf/upload_pdf_success.html", {"request": request})



# Функція витягування логів
@router.post("/upload_page")
async def upload_page(request: Request, 
                      document: str = Form(...),
                      documents: str = Form(...),
                      ):
    
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("auth/access_denied.html", {"request": request})

    async with httpx.AsyncClient() as client:
        form_data = {
            "data": document,
        }

        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.post(
            f"{base_url}/query_history/get_query_history/", headers=headers, data=form_data
        )

        response.raise_for_status()
        ansver_from = response.json()


    # Якщо документ вибраний, отримуємо його вміст
    # document_content = documents_data.get(document, "") if document else ""
    
    document_list = documents.split(',')
    # Передаємо дані в шаблон
    return templates.TemplateResponse("pdf/upload_pdf.html", {
        "request": request,
        "documents": document_list,
        "document_content": ansver_from,
        "selected_document": document  # Для того, щоб зберегти вибір
    })


# Задаємо питання, отрумуємо відповідь
@router.post("/ask_question")
async def ask_question(request: Request, 
                      question: str = Form(...),
                      document_content: Optional[str] = Form("[]"),
                      document: Optional[str] = Form(None) ,
                      documents: str = Form(...),
                      ):
    
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("auth/access_denied.html", {"request": request})

    if not document or document == "":
        return templates.TemplateResponse("pdf/no_choice_doc.html", {"request": request})
    

    async with httpx.AsyncClient(timeout=None) as client:
        try:

            form_data = {
                "question": question,
                "document": document,
                }

            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.post(
                f"{base_url}/model/ask_question/", headers=headers, data=form_data
            )

            print(response)
            response.raise_for_status()
            ansver_from = response.json()

    
            document_list = documents.split(',')
            document_content_list = ast.literal_eval(document_content)
            document_content_list.append((question, ansver_from))

            # Передаємо дані в шаблон
            return templates.TemplateResponse("pdf/upload_pdf.html", {
                "request": request,
                "documents": document_list,
                "document_content": document_content_list,
                "selected_document": document  # Для того, щоб зберегти вибір
            })
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "auth/access_denied.html", {"request": request}
                )
            # if e.response.status_code == 429:
            #     return templates.TemplateResponse(
            #         "suspicious_activity.html", {"request": request}
            #     )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )
        



# Задаємо питання, отрумуємо відповідь
@router.post("/delete_logs")
async def ask_question(request: Request, 
                      question: str = Form(...),
                      document_content: Optional[str] = Form("[]"),
                      document: Optional[str] = Form(None) ,
                      documents: str = Form(...),
                      ):
    
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("auth/access_denied.html", {"request": request})

    if not document or document == "":
        return templates.TemplateResponse("pdf/no_choice_doc.html", {"request": request})
    

    async with httpx.AsyncClient(timeout=None) as client:
        try:

            form_data = {
                "document": document,
                }

            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.post(
                f"{base_url}/query_history/{form_data}", headers=headers
            )

            response.raise_for_status()
            ansver_from = response.json()

    
            document_list = documents.split(',')
            document_content_list = ast.literal_eval(document_content)
            document_content_list.append((question, ansver_from))

            # Передаємо дані в шаблон
            return templates.TemplateResponse("pdf/upload_pdf.html", {
                "request": request,
                "documents": document_list,
                "document_content": document_content_list,
                "selected_document": document  # Для того, щоб зберегти вибір
            })
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "auth/access_denied.html", {"request": request}
                )
            # if e.response.status_code == 429:
            #     return templates.TemplateResponse(
            #         "suspicious_activity.html", {"request": request}
            #     )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )