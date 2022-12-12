import os
from uuid import uuid4

from pydantic import UUID4
from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.SkillModel import SkillModel
from services.SkillService import SkillService, SkillVacancyService

from fastapi import FastAPI, Response, status

SkillApp = FastAPI(
    title=os.getenv('TITLE') + " | Skill",
    debug=(os.getenv('DEBUG') == 'True')
)


@SkillApp.post('/vacancy/{vacancyId}')
async def attach_to_vacancy(SkillMd: SkillModel, vacancyId: UUID4, session=None):
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        skill = get_or_create(SkillName=SkillMd.SkillName, session=session).payload
        requirement = SkillVacancyService(
            VacancyId=vacancyId,
            SkillId=skill.SkillId,
            SkillYearExperience=SkillMd.SkillYearExperience
        )
        session.add(requirement)
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


def get_or_create(SkillName, session=None):
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        skill = session.query(SkillService).filter(SkillService.SkillName == SkillName).first()
        
        if skill is None:
            skill = SkillService(SkillId=uuid4(), SkillName=SkillName)
            session.add(skill)
        result.payload=skill
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


@SkillApp.delete('/{VacancyId}', status_code=status.HTTP_200_OK)
async def remove_required_skills_from_vacancy(response: Response, VacancyId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        SkillSv = session.query(SkillVacancyService).filter(SkillVacancyService.VacancyId == VacancyId)

        if SkillSv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        SkillSv.delete()

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


@SkillApp.get('/{VacancyId}', status_code=status.HTTP_200_OK)
async def list_required_skills_from_vacancy(response: Response, VacancyId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    try:
        # It let us continue with a transaction
        if session is None:
            session = SessionLocal()

        SkillSv = session.query(SkillVacancyService).filter(SkillVacancyService.VacancyId == VacancyId)

        if SkillSv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        skillsSv = SkillSv.all()

        skills = []

        for s in skillsSv:
            name = session\
                .query(SkillService)\
                .filter(SkillService.SkillId == s.SkillId)\
                .first().SkillName
            SkillM = SkillModel(
                SkillId=s.SkillId,
                SkillName=name,
                SkillYearExperience=s.SkillYearExperience
            )
            skills.append(SkillM)

        result.payload = skills

    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.payload=str(e)
    finally:
        return result