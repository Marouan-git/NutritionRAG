from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router as api_router
from app.services.llm_service import LLMService
from app.services.mongo_service import mongo_service
import uvicorn

load_dotenv()

app = FastAPI(
    title="Agent conversationnel",
    description="API pour un agent conversationnel donné lors du TP1",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inclure les routes
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)