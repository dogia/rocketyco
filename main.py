import os
from fastapi import FastAPI
from dotenv import load_dotenv

from apps.CompanyApp import CompanyApp
from apps.UserApp import UserApp
from apps.VacancyApp import VacancyApp
from core.CommonApiResponse import CommonApiResponse


load_dotenv()

app = FastAPI(
    title=os.getenv('TITLE') + " | Company",
    debug=(os.getenv('DEBUG') == 'True')
)

app.mount('/company', CompanyApp)
app.mount('/vacancy', VacancyApp)
app.mount('/user', UserApp)

@app.get('/')
async def home():
    commonResponse = CommonApiResponse(
        success=True,
        message='Bienvenido a RocketyCo',
        payload={}
    )

    commonResponse.payload = {
        'apps': {
            'descripción': 'Este folder contiene puntos de montaje del aplicativo',  # noqa: E501
            'usos': 'Contiene todos los metodos CRUD correspondientes a una funcionalidad'  # noqa: E501
        },
        'core': {
            'descripción': 'Archivos de configuración y modelo de respuesta común.',  # noqa: E501
            'usos': 'config.py permite administrar el middleware CORS y response.py contiene un modelo de respuesta común'  # noqa: E501
        },
        'errors': {
            'descripción': 'Contendría las excepciones descriptivas de casos particulares de error.',  # noqa: E501
            'usos': 'Junto a bloques try except permiten un manejo estander de errores'  # noqa: E501
        },
        'helpers': {
            'descripción': 'Contiene funciones de ayuda que permiten delegar responsabilidades a funciones específicas.',  # noqa: E501
            'usos': 'Módulo de funciones auxiliares'  # noqa: E501
        },
        'middlewares': {
            'descripción': 'Contendría todas las interceptaciones a las peticiones.',  # noqa: E501
            'usos': 'Permitiría filtrar por autenticación JWT y declarar middleware para las apps'  # noqa: E501
        },
        'models': {
            'descripción': 'Contiene los modelos REST de FastApi.',  # noqa: E501
            'usos': 'Modelar compañías, vacantes, habilidades y usuarios'  # noqa: E501
        },
        'postman': {
            'descripción': 'Contiene ejemplos exportados en postman del uso del API.',  # noqa: E501
            'documentaciones': ['/user/docs', '/company/docs']  # noqa: E501
        },
        'services': {
            'descripción': 'Contiene modelos del ORM que permiten interactuar con los datos.',  # noqa: E501
        },
        'tests': {
            'descripción': 'Algunos casos de prueba que se pueden ir mejorando, separados por cada folder.'  # noqa: E501
        },
        'scripts': {
            'pytest': 'Realiza de forma automatizada los test que están en el folder test',  # noqa: E501
            'isort .': 'Ordena los imports del proyecto',  # noqa: E501
            'flake8': 'Linter del proyecto, ayuda a escribir código legible.'  # noqa: E501
        }

    }

    return commonResponse
