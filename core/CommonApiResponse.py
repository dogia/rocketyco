import datetime
import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class CommonApiResponse(BaseModel):
    success: bool = True
    message: str | None
    payload: list | dict | bool | BaseModel | None = None
    datetime: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    webmaster: str = os.getenv('WEBMASTER_EMAIL')