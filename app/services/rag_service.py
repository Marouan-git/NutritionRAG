import tempfile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from typing import List
from chromadb.config import Settings
import os
import shutil
from io import BytesIO

class RAGService:
    def __init__(self, persist_dir: str = "./data/vectorstore"):
        """
        Initialise le service RAG avec un vector store persistant
        
        Args:
            persist_dir: Chemin où persister le vector store
        """
        self.persist_dir = persist_dir

        self._client = None

        
        
        # Création du dossier de persistance s'il n'existe pas
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
 
        try:
            if os.path.exists(os.path.join(self.persist_dir, "chroma.sqlite3")):
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
                self._client = self.vector_store._client
            else:
                self.vector_store = None
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            self.vector_store = None
        
        # Configure Chroma client settings
        self._client_settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            allow_reset=True  # Enable reset functionality
        )
        
        # Initialize with safe settings
        self._init_vector_store()
    
    def _init_vector_store(self):
        """Initialize vector store with proper settings"""
        try:
            if os.path.exists(os.path.join(self.persist_dir, "chroma.sqlite3")):
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings,
                    client_settings=self._client_settings
                )
            else:
                self.vector_store = None
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            self.vector_store = None
       
    
    async def load_and_index_pdf(self, file_content: bytes, clear_existing: bool = False) -> None:
        """
        Load and index a PDF document.

        Args:
            file_content: Byte content of the PDF file.
            clear_existing: If True, clears the existing vector store before indexing.
        """
        if clear_existing and os.path.exists(self.persist_dir):
            self.clear()

        # Create a temporary file to save the PDF content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        try:
            # Use PyMuPDFLoader to load the PDF from the temporary file
            loader = PyMuPDFLoader(tmp_file_path)
            documents = loader.load()

            # (Optional) Ensure each page has 'page' metadata if not already present
            # for idx, doc in enumerate(documents):
            #     if "page" not in doc.metadata:
            #         doc.metadata["page"] = idx + 1  # 1-based page numbering

            # Split the documents
            splits = self.text_splitter.split_documents(documents)


            if self.vector_store is None:
                # Initialize a new vector store from the splitted docs (with metadata)
                self.vector_store = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory=self.persist_dir
                )
                self._client = self.vector_store._client
            else:
                # Add to the existing vector store
                self.vector_store.add_documents(splits)


        except Exception as e:
            print(f"Error loading and indexing PDF: {e}")
            raise e
        finally:
            # Ensure the temporary file is deleted
            os.remove(tmp_file_path)
    
    

            
    
    async def similarity_search(self, query: str, k: int = 4) -> List[dict]:
        """
        Effectue une recherche par similarité
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats à retourner
            
        Returns:
            Liste de dict, chaque dict contenant le texte et la metadata
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Please add documents first.")
            
        results = self.vector_store.similarity_search(query, k=k)
        
        # Return text + metadata for each chunk
        docs_with_metadata = []
        for doc in results:
            # print(f"Metadata document: {doc.metadata}")
            docs_with_metadata.append({
                "text": doc.page_content,
                "metadata": doc.metadata
            })
        return docs_with_metadata
        

    def clear(self) -> None:
        """
        Supprime toutes les données du vector store de manière sécurisée
        """
        try:
            if self.vector_store is not None:
                # Proper reset with allowed configuration
                self.vector_store.delete_collection()
                self.vector_store = None
                
            # Reinitialize with fresh client
            self._init_vector_store()
            
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            raise