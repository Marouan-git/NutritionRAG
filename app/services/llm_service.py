from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.services.memory import InMemoryHistory
import os
from typing import AsyncGenerator, List, Dict, Optional, Any
from app.services.mongo_service import MongoService, mongo_service
import asyncio
from app.services.rag_service import RAGService


class LLMService:
    """
    Service LLM unifié supportant à la fois les fonctionnalités du TP1 et du TP2
    """
    def __init__(self):
        self.rag_service = RAGService()
        
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
            model_name="gpt-4o",
            api_key=api_key,
            streaming=True
        )
        
        self.conversation_store = {}
        
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Tu es un assistant nutrition. "
                "1. Tu ne réponds qu'aux questions liées à la nutrition. "
                "   Si la question n'est pas liée à la nutrition, réponds poliment : "
                "\"Désolé, je ne réponds qu'aux questions sur la nutrition.\" "
                "2. Si l'utilisateur pose une question liée à la nutrition, "
                "   mais l'information n'est pas dans le contexte, dis : "
                "\"Désolé, je n'ai pas assez d'informations pour répondre.\" "
                "3. Utilise uniquement le contexte fourni ; n'invente pas d'informations hors contexte. "
                "4. Lorsque tu fournis des informations tirées du contexte, mentionne toujours la source entre parenthèses, " 
                "par exemple (Source : page XX). S'il y a plus d'une page, mentionne-les en conséquence dans l'ordre de pertinence."
            ),
            ("system", "Contexte : {context}"),
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
                                session_id: Optional[str] = None,
                                use_rag: bool = False) -> str:
        """
        Méthode unifiée pour générer des réponses
        Supporte les deux modes : avec contexte (TP1) et avec historique (TP2)
        """
        # Build a RAG context if requested
        rag_context = ""
        if use_rag and self.rag_service.vector_store:
            # similarity_search now returns a list of dict with text + metadata
            relevant_docs = await self.rag_service.similarity_search(message)
            rag_context_parts = []
            for d in relevant_docs:
                chunk_text = d["text"]
                page_num = d["metadata"].get("page", "??")
                print(f"Metadata: {d['metadata']}")
                print(page_num)
                print(chunk_text)
                # Combine chunk text with a source reference
                rag_context_parts.append(f"{chunk_text}\n(Source: page {page_num})")
            rag_context = "\n\n".join(rag_context_parts)
        
        # Reconstruct the conversation so far from Mongo
        history_messages = []
        mongo_history = await self.mongo_service.get_conversation_history(session_id)
        for msg in mongo_history:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                history_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                history_messages.append(AIMessage(content=content))

        # Add the new user message to the local (in-process) history
        history_messages.append(HumanMessage(content=message))
        
        # Invoke chain with the constructed prompt + history + rag context
        response = await self.chain_with_history.ainvoke(
            {
                "question": message,
                "context": rag_context
            },
            config={"configurable": {"session_id": session_id}},
            history=history_messages
        )
        response_text = response.content

        # Save user and assistant messages to Mongo
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
    
    async def create_session(self) -> str:
        """Create a new conversation session without initial message"""
        import uuid
        session_id = str(uuid.uuid4())
        
        # Initialize empty history
        self.conversation_store[session_id] = InMemoryHistory()
        
        # Create empty conversation document in MongoDB
        await self.mongo_service.create_empty_session(session_id)
        return session_id

    # Add to LLMService class
    async def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session and its history"""
        # Delete from memory store
        if session_id in self.conversation_store:
            del self.conversation_store[session_id]
        
        # Delete from MongoDB
        return await self.mongo_service.delete_conversation(session_id)
    
    async def rename_session(self, old_session_id: str, new_session_id: str) -> bool:
        """Rename a session in both memory and database"""
        # Check if new session ID already exists
        if await self.mongo_service.get_conversation_history(new_session_id):
            raise ValueError("New session ID already exists")

        # Update MongoDB
        mongo_success = await self.mongo_service.rename_session(old_session_id, new_session_id)
        
        # Update in-memory store
        if old_session_id in self.conversation_store:
            self.conversation_store[new_session_id] = self.conversation_store.pop(old_session_id)
        
        return mongo_success
    
    async def stream_response(self, message: str, session_id: str) -> AsyncGenerator[str, None]:
        """Stream response from LLM with RAG context"""
        full_response = ""
        # Save user message first
        await self.mongo_service.save_message(session_id, "user", message)
        print(f"User message saved: {message}")

        rag_context = ""
        if self.rag_service.vector_store:
            # similarity_search now returns a list of dict with text + metadata
            relevant_docs = await self.rag_service.similarity_search(message)
            rag_context_parts = []
            for d in relevant_docs:
                chunk_text = d["text"]
                page_num = d["metadata"].get("page", "??")
                print(f"Metadata: {d['metadata']}")
                print(page_num)
                print(chunk_text)
                # Combine chunk text with a source reference
                rag_context_parts.append(f"{chunk_text}\n(Source: page {page_num})")
            rag_context = "\n\n".join(rag_context_parts)

        # Reconstruct the conversation so far from Mongo
        history_messages = []
        mongo_history = await self.mongo_service.get_conversation_history(session_id)
        for msg in mongo_history:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                history_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                history_messages.append(AIMessage(content=content))

        # Add the new user message to the local (in-process) history
        history_messages.append(HumanMessage(content=message))
        
        # Create streaming version of the chain
        chain = self.prompt | self.llm

        try:
        
            
            # Stream response chunks
            async for chunk in chain.astream({
                "question": message,
                "context": rag_context,
                "history": history_messages
            }):
                if isinstance(chunk, AIMessage):
                    full_response += chunk.content
                    yield chunk.content
                    await asyncio.sleep(0.01)  # Smooth streaming

            # Save complete assistant response after streaming finishes
            await self.mongo_service.save_message(session_id, "assistant", full_response)
            print(f"Assistant response saved: {full_response}")
            
        except Exception as e:
            yield f"\n\nError: {str(e)}"

            

        