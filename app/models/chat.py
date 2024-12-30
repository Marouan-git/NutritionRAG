# models/chat.py
"""
Modèles Pydantic pour la validation des données
Inclut les modèles du TP1 et les nouveaux modèles pour le TP2
"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Réponse standard du chatbot"""
    response: str

class ChatRequest(BaseModel):
    """Requête de base pour une conversation sans contexte"""
    message: str
    session_id: str  # Ajouté pour supporter les deux versions

class ChatMessage(BaseModel):
    """Structure d'un message individuel dans l'historique"""
    role: str  # "user" ou "assistant"
    content: str

class ChatHistory(BaseModel):
    """Collection de messages formant une conversation"""
    messages: List[ChatMessage]