# NutrIA project - Conversational agents - M2IA2

Members : 
- Jarod Acloque
- Jaafar El Bakkali
- Marouan Boulli

## Purpose

Design a chatbot with 2 main purposes:
1. Provide nutrition advices based on a best nutrition practices knowledge base.
2. Recommend dishes to suit the user profile.


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
        memory.py          # Service de gestion de la mémoire (utile pour la version sans persistance)
        mongo_service.py   # Service d'interaction avec la base de données Mongo
```
## Installation et Configuration

### Prerequisites

OpenAI API key and MongoDB connection information provided in an .env file.  
Environment varables names are provided in the **.env.template** file.

### Installation

1. **Clone the project**
```bash
git clone https://github.com/Marouan-git/NutritionRAG.git
cd NutritionRAG
```

2. **Create the virtual environment and install dependencies**
```bash
pipenv install
```

If you don't have pipenv installed, install it with:
```
pip install pipenv
```

3. **Activate the virtual environment**

```bash
pipenv shell
```


5. **Configure your .env file**
Create a `.env` file at the root of the project, and put the following variables:
```
OPENAI_API_KEY=<your OpenAI API key>
MONGODB_URI=<your MongoDB URI for connection>
DATABASE_NAME=<database name on Mongo>
COLLECTION_NAME=<collection name on Mongo>
```

## Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation LangChain](https://python.langchain.com/)
- [API OpenAI](https://platform.openai.com/docs/api-reference)