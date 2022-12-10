import os
from fastapi import FastAPI
from dotenv import load_dotenv

from apps.CompanyApp import CompanyApp


load_dotenv()

RocketyApi = FastAPI(
    title=os.getenv('TITLE') + " | Company",
    debug=(os.getenv('DEBUG') == 'True')
)

RocketyApi.mount('/company', CompanyApp)