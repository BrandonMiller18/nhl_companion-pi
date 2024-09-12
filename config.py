import os
from datetime import date
from dotenv import load_dotenv
load_dotenv()

BASE_API_URL = 'https://api-web.nhle.com/v1/'
TODAY = date.today()

SECRET_KEY = os.getenv("SECRET_KEY")