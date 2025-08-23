import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')
PROJECT_NAME = os.getenv('PROJECT_NAME')
PROJECT_DESCRIPTION = os.getenv('PROJECT_DESCRIPTION')
PROJECT_VERSION = os.getenv('PROJECT_VERSION')
PROJECT_LICENSE = os.getenv('PROJECT_LICENSE')
TOKEN_EXPIRY_IN_MINUTES = int(os.getenv('TOKEN_EXPIRY_IN_MINUTES'))
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')