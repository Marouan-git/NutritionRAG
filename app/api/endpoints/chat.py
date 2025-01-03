# api/chat.py
"""
Routes FastAPI pour le chatbot
Inclut les endpoints du TP1 et du TP2
"""
from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest,  ChatResponse
from services.llm_service import LLMService
from typing import Dict, List

router = APIRouter()
llm_service = LLMService()



@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Nouvel endpoint du TP2 avec gestion de session"""
    try:
        response = await llm_service.generate_response(
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sessions")
async def get_all_sessions() -> List[str]:
    """
    Récupération de toutes les sessions disponibles
    """
    try:
        return await llm_service.get_all_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str) -> List[Dict[str, str]]:
    """Récupération de l'historique d'une conversation"""
    try:
        return await llm_service.get_conversation_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/chat/simple", response_model=ChatResponse)
# async def chat_simple(request: ChatRequestTP1) -> ChatResponse:
#     """Endpoint simple du TP1"""
#     try:
#         response = await llm_service.generate_response(request.message)
#         return ChatResponse(response=response)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/chat/with-context", response_model=ChatResponse)
# async def chat_with_context(request: ChatRequestWithContext) -> ChatResponse:
#     """Endpoint avec contexte du TP1"""
#     try:
#         response = await llm_service.generate_response(
#             message=request.message,
#             context=request.context
#         )
#         return ChatResponse(response=response)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))