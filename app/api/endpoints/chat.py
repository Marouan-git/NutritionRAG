"""
Routes FastAPI pour le chatbot
Inclut les endpoints du TP1 et du TP2
"""
import json
from fastapi import APIRouter, File, HTTPException, Body, UploadFile, status
from app.models.chat import ChatRequest,  ChatResponse, SessionResponse, RenameSessionRequest
from app.services.llm_service import LLMService
from typing import Dict, List
from fastapi.responses import StreamingResponse

router = APIRouter()
llm_service = LLMService()



### RAG endpoint ###
    

@router.post("/chat/rag")
async def chat_with_rag(request: ChatRequest):
    """Simplified streaming endpoint"""
    return StreamingResponse(
        llm_service.stream_response(request.message, request.session_id),
        media_type="text/plain"
    )


### Sessions endpoints ###

    
@router.get("/sessions")
async def get_all_sessions() -> List[str]:
    """
    Récupération de toutes les sessions disponibles
    """
    try:
        return await llm_service.get_all_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session():
    """Create a new empty chat session"""
    try:
        session_id = await llm_service.create_session()
        return SessionResponse(session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{old_session_id}", response_model=SessionResponse)
async def rename_session(
    old_session_id: str,
    request: RenameSessionRequest
):
    """Rename an existing session ID"""
    try:
        success = await llm_service.rename_session(
            old_session_id=old_session_id,
            new_session_id=request.new_session_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return SessionResponse(session_id=request.new_session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add endpoint for session deletion
@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """Permanently delete a chat session and its history"""
    try:
        success = await llm_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str) -> List[Dict[str, str]]:
    """Récupération de l'historique d'une conversation"""
    try:
        return await llm_service.get_conversation_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

### Documents endpoints ###

    
@router.post("/documents/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    clear_existing: bool = Body(False)
) -> dict:
    """
    Endpoint to upload and index a PDF document.

    Args:
        file: The PDF file to be uploaded and indexed.
        clear_existing: If True, clears existing vector store before indexing.

    Returns:
        Confirmation message upon successful indexing.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Pass the file content to the RAG service
        await llm_service.rag_service.load_and_index_pdf(file_content, clear_existing)
        
        return {"message": "PDF document indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents")
async def clear_documents() -> dict:
    """Endpoint pour supprimer tous les documents indexés"""
    try:
        llm_service.rag_service.clear()
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))