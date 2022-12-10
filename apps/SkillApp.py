import os
from uuid import uuid4

from pydantic import UUID4
from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.SkillModel import SkillModel
from services.SkillService import SkillService, SkillVacancyService

from fastapi import FastAPI

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
