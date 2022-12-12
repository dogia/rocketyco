import os
from uuid import uuid4
from fastapi import FastAPI, Response, status
from pydantic import UUID4
from apps.SkillApp import attach_to_vacancy, list_required_skills_from_vacancy, remove_required_skills_from_vacancy

from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.VacancyModel import VacancyModel
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

        if VacancyMd.CompanyId is None:
            raise Exception('No se ha vinculado la vacante a ninguna empresa')

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

@VacancyApp.get('/{VacancyId}', status_code=status.HTTP_200_OK)
async def detail(response: Response, VacancyId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')

    try:
        if session is None:
            session = SessionLocal()

        VacancySv = session.query(VacancyService).filter(VacancyService.VacancyId == VacancyId).first()

        if VacancySv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        VacancyMd = VacancyModel(**VacancySv.dict())
        required_skills = (await list_required_skills_from_vacancy(
            response=response,
            VacancyId=VacancyId,
            session=session
        )).payload
        
        required_skillsdict = []
        for v in required_skills:
            required_skillsdict.append(v.dict())
        VacancyMd.RequiredSkills = required_skillsdict

        result.payload = VacancyMd
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.payload=str(e)
    finally:
        return result

@VacancyApp.put('/', status_code=status.HTTP_200_OK)
async def update(response: Response, VacancyMd: VacancyModel, session=None) -> CommonApiResponse:
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

        # Save the vacancy
        VacancySv = session\
            .query(VacancyService)\
            .filter(VacancyService.VacancyId == VacancyMd.VacancyId)\
            .first()

        if VacancySv is None:
            raise Exception('No se ha encontrado ninguna vacante')

        if VacancyMd.CompanyId is not None:
            VacancySv.CompanyId = VacancyMd.CompanyId

        if VacancyMd.PositionName is not None:
            VacancySv.PositionName = VacancyMd.PositionName

        if VacancyMd.Salary is not None:
            VacancySv.Salary = float(VacancyMd.Salary)
        
        if VacancyMd.Currency is not None:
            VacancySv.Currency = VacancyMd.Currency

        if VacancyMd.VacancyLink is not None:
            VacancySv.VacancyLink = VacancyMd.VacancyLink

        if VacancyMd.RequiredSkills is not None:
            # Solo agrega las habiliades nuevas y no las reemplaza
            for required_skill in VacancyMd.RequiredSkills:
                required = await attach_to_vacancy(
                    SkillMd=required_skill,
                    vacancyId=VacancyMd.VacancyId,
                    session=session
                )

                if not required.success:
                    raise Exception('Falló la creación de una habilidad requerida.')

        result = (await detail(response, VacancyMd.VacancyId, session))

        print(result)
        # Parse to visible
        newRequired = []
        for i in result.payload.RequiredSkills:
            newRequired.append(i)

        if VacancyMd.RequiredSkills is not None:
            for i in VacancyMd.RequiredSkills:
                newRequired.append(i.dict())

        result.payload.RequiredSkills = newRequired
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

@VacancyApp.delete('/{VacancyId}', status_code=status.HTTP_200_OK)
async def delete_from_company(
    response: Response,
    VacancyId: str,
    session=None
) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        vacancies = session.query(VacancyService).filter(VacancyService.VacancyId == VacancyId)

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


# __________________________________ FROM COMPANY ______________________________________

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
