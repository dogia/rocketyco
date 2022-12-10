import os
from uuid import uuid4
from fastapi import FastAPI, Response, status
from apps.SkillApp import attach_to_vacancy

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