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


# Роут для відображення форми завантаження PDF
@router.get("/upload_pdf_test", response_class=HTMLResponse)
async def upload_pdf_form(request: Request):

    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("access_denied.html", {"request": request})

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.post(
                f"{base_url}/pdf/request_for_title_docs/", headers=headers          #, data=form_data
            )
            response.raise_for_status()
            ansver_from = response.json()

            return templates.TemplateResponse("pdf/upload_pdf_test.html", {"request": request, "documents": ansver_from})
        
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


# Функція для обробки PDF
@router.post("/upload_pdf_test", response_class=HTMLResponse)
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
    pdf_text = extract_text_from_pdf(pdf.file)


    async with httpx.AsyncClient() as client:
        try:
            form_data = {
                "description": description,
                "text": pdf_text,
            }

            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.post(
                f"{base_url}/pdf/upload_new_pdf/", headers=headers, data=form_data
            )

            response.raise_for_status()
            ansver_from = response.json()

            return templates.TemplateResponse("/pdf/upload_pdf_success.html", {"request": request, "pdf_text": ansver_from})

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
        





# Функція для завантаження тексту з ПДФ док-ту
@router.post("/upload_pdf_test_new", response_class=HTMLResponse)
async def upload_new_pdf(
    request: Request,
    pdf: UploadFile = File(...),
    
):
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("access_denied.html", {"request": request})

    # Отримання тексту з PDF (функція повинна бути реалізована окремо)
    pdf_text = extract_text_from_pdf(pdf.file)


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
        ansver_from = response.json()

    return templates.TemplateResponse("/pdf/upload_pdf_success.html", {"request": request}) #, "pdf_text": ansver_from})






# # Функція для вибору, з яким документом ми працюємо
# @router.post("/choice_doc", response_class=HTMLResponse)
# async def choice_doc(
#     request: Request,
#     document: str = Form(...),
# ):
    
#     access_token = request.session.get("access_token")
#     if not access_token:
#         # Відмовити у доступі, якщо токен відсутній
#         return templates.TemplateResponse("access_denied.html", {"request": request})

#     async with httpx.AsyncClient() as client:
#         form_data = {
#             "text": document,
#         }

#         headers = {"Authorization": f"Bearer {access_token}"}

#         response = requests.post(
#             f"{base_url}/pdf/upload_new_pdf_test", headers=headers, data=form_data
#         )

#         response.raise_for_status()
#         ansver_from = response.json()

#     return templates.TemplateResponse("/pdf/upload_pdf_test.html", {"request": request, "document_list": ansver_from})




# Функція витягування логів
@router.post("/upload_page")
async def upload_page(request: Request, 
                      document: str = Form(...),
                      documents: str = Form(...),
                      ):
    
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("access_denied.html", {"request": request})

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
    return templates.TemplateResponse("/pdf/upload_pdf_test.html", {
        "request": request,
        "documents": document_list,
        "document_content": ansver_from,
        "selected_document": document  # Для того, щоб зберегти вибір
    })


# Задаємо питання, отрумуємо відповідь
@router.post("/ask_question")
async def ask_question(request: Request, 
                      question: str = Form(...),
                      document_content: str = Form(...),
                      document: str = Form(...),
                      documents: str = Form(...),
                      ):
    
    access_token = request.session.get("access_token")
    if not access_token:
        # Відмовити у доступі, якщо токен відсутній
        return templates.TemplateResponse("access_denied.html", {"request": request})

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
            return templates.TemplateResponse("/pdf/upload_pdf_test.html", {
                "request": request,
                "documents": document_list,
                "document_content": document_content_list,
                "selected_document": document  # Для того, щоб зберегти вибір
            })
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
        

