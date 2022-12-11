import os
from fastapi import FastAPI, Response, status
from pydantic import UUID4

from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.CompanyModel import CompanyModel
from services.CompanyService import CompanyService

from apps.VacancyApp import create as create_vacancy, delete_from_company as delete_vacancies_from_company, list_from_company
from services.VacancyService import VacancyService

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

@CompanyApp.get('/', status_code=status.HTTP_200_OK)
async def list(
    response: Response,
    offset: int = 0,
    limit: int = 10,
    session=None
) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    try:
        if limit > 1000 or offset < 0 or limit < 0:
            raise Exception('La paginación no es correcta: limit & offset > 0 limit < 1001')

        if session is None:
            session = SessionLocal()

        result.payload = session.query(CompanyService).limit(limit).offset(offset).all()
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
    finally:
        return result


@CompanyApp.get('/{CompanyId}', status_code=status.HTTP_200_OK)
async def detail(response: Response, CompanyId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')

    try:
        if session is None:
            session = SessionLocal()

        CompanySv = session.query(CompanyService).filter(CompanyService.CompanyId == CompanyId).first()

        if CompanySv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        CompanyMd = CompanyModel(**CompanySv.dict())
        qvacancies = await list_from_company(
            response=response,
            companyId=CompanyMd.CompanyId,
            session=session
        )

        CompanyMd.Vacancies = qvacancies.payload
        result.payload = CompanyMd
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.payload=str(e)
    finally:
        return result


@CompanyApp.put('/', status_code=status.HTTP_200_OK)
async def update(response: Response, CompanyMd: CompanyModel, session=None) -> CommonApiResponse:
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
        CompanySv = session\
            .query(CompanyService)\
            .filter(CompanyService.CompanyId == CompanyMd.CompanyId)\
            .first()

        if CompanySv is None:
            raise Exception('No se ha encontrado ninguna compañía')

        if CompanyMd.CompanyName is not None:
            CompanySv.CompanyName = CompanyMd.CompanyName

        if CompanyMd.CompanyWebsite is not None:
            CompanySv.CompanyWebsite = CompanyMd.CompanyWebsite

        if CompanyMd.Vacancies is not None:
            # Solo agrega las vacantes nuevas y no las reemplaza
            for vacancy in CompanyMd.Vacancies:
                vacancy.CompanyId = CompanyMd.CompanyId
                vacancy_result = await create_vacancy(
                    VacancyMd=vacancy,
                    session=session
                )

                if not vacancy_result.success:
                    raise Exception('Falló la creación de una vacante.')

        result = (await detail(response, CompanyMd.CompanyId, session))

        # Parse to visible
        vacancies = []
        for i in result.payload.Vacancies:
            vacancies.append(i.dict())

        for vacancy in CompanyMd.Vacancies:
            del vacancy.RequiredSkills
            vacancies.append(vacancy.dict())

        result.payload.Vacancies = vacancies
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
        session.rollback()
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

@CompanyApp.delete('/{CompanyId}', status_code=status.HTTP_200_OK)
async def detail(response: Response, CompanyId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        CompanySv = session.query(CompanyService).filter(CompanyService.CompanyId == CompanyId)

        if CompanySv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        CompanyMd = CompanyModel(**CompanySv.first().dict())
        vacancies = (await delete_vacancies_from_company(
            response=response,
            companyId=CompanyId,
            session=session
        )).payload
        vacanciesdict = []
        for v in vacancies:
            print(v)
            vacanciesdict.append(v.dict())
        CompanyMd.Vacancies = vacanciesdict
        CompanySv.delete()

        result.payload = CompanyMd
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.payload=str(e)
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
