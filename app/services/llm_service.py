# services/llm_service.py
"""
Service principal gérant les interactions avec le modèle de langage
Compatible avec les fonctionnalités du TP1 et du TP2
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from services.memory import InMemoryHistory
import os
from typing import List, Dict, Optional, Any
from services.mongo_service import MongoService, mongo_service
import asyncio



class LLMService:
    """
    Service LLM unifié supportant à la fois les fonctionnalités du TP1 et du TP2
    """
    def __init__(self):
        
        self.mongo_service = mongo_service
        # Send a ping to confirm a successful connection to MongoDB
        try:
            self.mongo_service.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY n'est pas définie")
        
        # Configuration commune
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            api_key=api_key
        )
        
        self.conversation_store = {}
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Vous êtes un assistant utile et concis."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])
        
        self.chain = self.prompt | self.llm
        
        
        # Configuration du gestionnaire d'historique
        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Récupère l'historique d'une session"""
        if session_id not in self.conversation_store:
            self.conversation_store[session_id] = InMemoryHistory()
        return self.conversation_store[session_id]
    

    async def generate_response(self, 
                              message: str, 
                              context: Optional[List[Dict[str, str]]] = None,
                              session_id: Optional[str] = None) -> str:
        """
        Méthode unifiée pour générer des réponses
        Supporte les deux modes : avec contexte (TP1) et avec historique (TP2)
        """

        # Get history
        history_messages = []
       
        mongo_history = await self.mongo_service.get_conversation_history(session_id)
        for msg in mongo_history:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                history_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                history_messages.append(AIMessage(content=content))

        # Add the new user message to the history
        history_messages.append(HumanMessage(content=message))
            
        response = await self.chain_with_history.ainvoke(
            {"question": message},
            config={"configurable": {"session_id": session_id}},
            history=history_messages
        )
        response_text = response.content

        try:
            await self.mongo_service.save_message(session_id, "user", message)
            print(f"Message saved: {message}")
            await self.mongo_service.save_message(session_id, "assistant", response_text)
            print(f"Assistant response saved: {response_text}")
        except Exception as e:
            print(f"Exception Raised: {e}")
          
        return response_text
            
            
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Récupère l'historique depuis MongoDB"""
        return await self.mongo_service.get_conversation_history(session_id)
    
    async def get_all_sessions(self) -> List[str]:
        """Récupère tous les IDs de session depuis MongoDB"""
        return await self.mongo_service.get_all_sessions()