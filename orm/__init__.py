# ORM package

# Manager principal
from .manager import DBManager

# Modèle pur
from .model import Model
A= DBManager()

# Types pour conversion Python <-> SQL (optionnel pour l'utilisateur)
#from .types import sql_to_python, python_to_sql

# Database (optionnel, si l'utilisateur veut manipuler directement)
#from .database import Database
