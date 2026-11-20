
from fastapi import FastAPI
from app.routes.documents import router as documents_router
from app.chat import router as chat_router

app = FastAPI(title="Integrated AI Assistant")

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {
        "message": "AI Assistant API is running"
    }
