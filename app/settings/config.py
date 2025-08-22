import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')
PROJECT_NAME = os.getenv('PROJECT_NAME')
PROJECT_DESCRIPTION = os.getenv('PROJECT_DESCRIPTION')
PROJECT_VERSION = os.getenv('PROJECT_VERSION')
PROJECT_LICENSE = os.getenv('PROJECT_LICENSE')