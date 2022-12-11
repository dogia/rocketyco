import os
from uuid import uuid4
from fastapi import FastAPI, Response, status
from apps.SkillApp import attach_to_vacancy, remove_required_skills_from_vacancy

from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.VacancyModel import VacancyModel
from services.SkillService import SkillVacancyService
from services.VacancyService import VacancyService

VacancyApp = FastAPI(
    title=os.getenv('TITLE') + " | Vacancy",
    debug=(os.getenv('DEBUG') == 'True')
)

@VacancyApp.post('/', status_code=status.HTTP_201_CREATED)
async def create(VacancyMd: VacancyModel, session = None):
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        # Prepare to parse to Service
        VacancyDict = VacancyMd.dict()
        del VacancyDict['RequiredSkills']

        VacancySv = VacancyService(**VacancyDict)
        session.add(VacancySv)

        result.payload = VacancyMd

        if VacancyMd.RequiredSkills is not None:
            for required_skill in VacancyMd.RequiredSkills:
                await attach_to_vacancy(
                    SkillMd=required_skill,
                    vacancyId=VacancyMd.VacancyId,
                    session=session
                )

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

@VacancyApp.get('/', status_code=status.HTTP_200_OK)
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

        result.payload = session.query(VacancyService).limit(limit).offset(offset).all()
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
    finally:
        return result

@VacancyApp.get('/fromCompany/{companyId}', status_code=status.HTTP_200_OK)
async def list_from_company(
    response: Response,
    companyId: str,
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

        result.payload = session.query(VacancyService).filter(VacancyService.CompanyId == companyId).limit(limit).offset(offset).all()
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
    finally:
        return result

@VacancyApp.delete('/fromCompany/{companyId}', status_code=status.HTTP_200_OK)
async def delete_from_company(
    response: Response,
    companyId: str,
    session=None
) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        vacancies = session.query(VacancyService).filter(VacancyService.CompanyId == companyId)

        # TODO: Delete required skills
        for v in vacancies:
            await remove_required_skills_from_vacancy(
                response=response,
                VacancyId=v.VacancyId,
                session=session
            )

        result.payload = vacancies
        vacancies.delete()
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
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