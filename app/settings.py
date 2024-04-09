from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")