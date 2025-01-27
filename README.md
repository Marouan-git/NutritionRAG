# NutrIA project - Conversational agents - M2IA2

Members : 
- Jaafar El Bakkali
- Marouan Boulli

## Purpose

Design a chatbot which provides nutrition advices based on a best nutrition practices knowledge base.


## Backend project structure

```
C:.
│   main.py                # Point d'entrée de l'application           
│
├───api
│   │   router.py          # Router principal regroupant tous les endpoints
│   │
│   └───endpoints
│           chat.py        # Endpoint pour les fonctionnalités de chat
│
├───core
│       config.py          # Configuration des éléments centraux de l'application
│
├───models
│       chat.py            # Modèles pour les requêtes/réponses de chat
│       conversation.py    # Modèles pour la gestion des messages et cnversations
│
└───services
        llm_service.py     # Service d'interaction avec le LLM
        memory.py          # Service de gestion de la mémoire
        mongo_service.py   # Service d'interaction avec la base de données Mongo
        rag_service.py     # Service pour le RAG
```

## Prerequisites

OpenAI API key and MongoDB connection information provided in an .env file.  
Environment varables names are provided in the **.env.template** file.  

## Run the project

1. **Clone the project**:
```bash
git clone https://github.com/Marouan-git/NutritionRAG.git
cd NutritionRAG
```

2. **Configure your .env file**  
Create a `.env` file at the root of the project, and put the following variables:
```
OPENAI_API_KEY=<your OpenAI API key>
MONGODB_URI=<your MongoDB URI for connection>
DATABASE_NAME=<database name on Mongo>
COLLECTION_NAME=<collection name on Mongo>
CHROMA_ALLOW_RESET=TRUE
```

### Using docker-compose

3. **Run**:
```
docker-compose up --build
```

### Without docker-compose

If you don't have docker and docker-compose installed or don't want to use it, you can run separately the backend and the frontend services:

- Install the virtual environment: 
 
If you don't have pipenv installed:
```
pip install pipenv 
```
Then:
```
pipenv install
pipenv shell
```

- Backend:
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Frontend:
```
cd chatbot-frontend
npm start
```



## Ressources

- [Canva presentation](https://www.canva.com/design/DAGdZqLb1Q4/Ghv_2bDXhYu2CN0WwFBABQ/edit?utm_content=DAGdZqLb1Q4&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation LangChain](https://python.langchain.com/)
- [API OpenAI](https://platform.openai.com/docs/api-reference)
