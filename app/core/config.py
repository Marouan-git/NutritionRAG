import logging
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """Classe de configuration pour MongoDB."""
    mongodb_uri = os.getenv("MONGODB_URI", "")  # Valeur par défaut vide si non définie
    database_name = os.getenv("DATABASE_NAME", "default_db")  # Nom de base par défaut
    collection_name = os.getenv("COLLECTION_NAME", "default_db")  # Nom de base par défaut

settings = Config()