import os
from dotenv import load_dotenv
load_dotenv()

class Credits:
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL") 
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    MOVIES_DB_HOST = os.getenv("MOVIES_DB_HOST")
    MOVIES_DB_PORT = os.getenv("MOVIES_DB_PORT")
    MOVIES_DB_USER = os.getenv("MOVIES_DB_USER")
    MOVIES_DB_PASSWORD = os.getenv("MOVIES_DB_PASSWORD")

credits = Credits()
