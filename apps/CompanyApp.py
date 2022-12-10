import os
from fastapi import FastAPI, Response, status
from pydantic import UUID4

from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.CompanyModel import CompanyModel
from services.CompanyService import CompanyService

from apps.VacancyApp import create as create_vacancy

CompanyApp = FastAPI(
    title=os.getenv('TITLE') + " | Company",
    debug=(os.getenv('DEBUG') == 'True')
)


@CompanyApp.post('/', status_code=status.HTTP_201_CREATED)
async def create(CompanyMd: CompanyModel, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        # Prepare to parse to Service
        CompanyDict = CompanyMd.dict()
        del CompanyDict['Vacancies']

        # Save the company
        CompanySv = CompanyService(**CompanyDict)
        print(session.add(CompanySv))

        result.payload = CompanyMd

        if CompanyMd.Vacancies is not None:
            for vacancy in CompanyMd.Vacancies:
                vacancy.CompanyId = CompanyMd.CompanyId
                vacancy_result = await create_vacancy(
                    VacancyMd=vacancy,
                    session=session
                )

                if not vacancy_result.success:
                    raise Exception('Falló la creación de una vacante.')
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
        session.rollback()
    except:
        print('Error!')
    else:
        if shouldCommit:
            try:
                session.commit()
            except Exception as e:
                print(e)
                result.message="Ha ocurrido un error"
                result.success=False
                result.payload=str(e)
                session.rollback()
    finally:
        return result

@CompanyApp.get('/{CompanyId}', status_code=status.HTTP_200_OK)
async def detail(CompanyId: UUID4) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')

    try:
        result.message = CompanyId
        result.payload = CompanyModel(
            CompanyName="Hunty",
            CompanyWebsite="https://www.hunty.com/"
        )
        pass
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.payload=e.__dict__
    finally:
        return result