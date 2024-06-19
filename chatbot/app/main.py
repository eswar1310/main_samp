from fastapi import Depends, FastAPI, Form, File, Query, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import HttpUrl

from app.chatbot import ChatBot, extract_text_from_pdf, extract_text_from_url, split_text_into_chunks


# Initialize FastAPI app
app = FastAPI()
chatbot = None



# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    with open(r"C:\Users\eswar.melam\OneDrive - Qentelli\Desktop\main_samp\Backend\chatbot\static\index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)



# Dictionary to store user-specific chatbot instances
user_chatbots = {}


@app.post("/initialize_chatbot/")
async def initialize_chatbot(url: HttpUrl = Form(None), file: UploadFile = File(None)):
    global chatbot
    if file:
        content = await file.read()
        text = extract_text_from_pdf(content)
    elif url:
        text = extract_text_from_url(url)
    else:
        return {"error": "No input provided. Please upload a PDF or provide a URL."}
 
    document_chunks = split_text_into_chunks(text, chunk_size=1024, overlap=64)
    chatbot = ChatBot(vectordb=None, document_chunks=document_chunks)
    return {"message": "Chatbot initialized with provided content."}

@app.post("/Ask_The_Question/")
async def ask_question(question: str): 
    global chatbot
    if chatbot is None:
        return {"error": "Chatbot not initialized. Upload a PDF first."}
    answer = chatbot.process_question(question)
    return {"answer": answer}

