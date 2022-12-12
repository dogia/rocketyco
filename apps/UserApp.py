import os
from fastapi import FastAPI, Response, status
from pydantic import UUID4
from apps.SkillApp import attach_to_user, list_skills_from_user

from core.CommonApiResponse import CommonApiResponse
from core.db import SessionLocal
from models.SkillModel import SkillModel
from models.UserModel import UserModel
from models.VacancyModel import VacancyModel
from services.SkillService import SkillService, SkillUserService, SkillVacancyService
from services.UserService import UserService

from apps.VacancyApp import detail as detail_vacancy

UserApp = FastAPI(
    title=os.getenv('TITLE') + " | Company",
    debug=(os.getenv('DEBUG') == 'True')
)


@UserApp.post('/', status_code=200)
async def create(
    UserMd: UserModel,
    session=None
) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False

    try:
        if session is None:
            shouldCommit = True
            session = SessionLocal()


        UserDict = UserMd.dict()
        del UserDict['Skills']

        UserSv = UserService(**UserDict)
        session.add(UserSv)

        result.payload = UserMd

        if UserMd.Skills is not None:
            for skill in UserMd.Skills:
                await attach_to_user(
                    SkillMd=skill,
                    userId=UserSv.UserId,
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


@UserApp.get('/', status_code=status.HTTP_200_OK)
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

        result.payload = session.query(UserService).limit(limit).offset(offset).all()
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
    finally:
        return result

@UserApp.get('/{UserId}', status_code=status.HTTP_200_OK)
async def detail(response: Response, UserId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')

    try:
        if session is None:
            session = SessionLocal()

        UserSv = session.query(UserService).filter(UserService.UserId == UserId).first()

        if UserSv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        UserMd = UserModel(**UserSv.dict())
        required_skills = (await list_skills_from_user(
            response=response,
            UserId=UserId,
            session=session
        )).payload
        
        skillsdict = []
        for v in required_skills:
            skillsdict.append(v.dict())
        UserMd.Skills = skillsdict

        result.payload = UserMd
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.payload=str(e)
    finally:
        return result


@UserApp.delete('/{UserId}', status_code=status.HTTP_200_OK)
async def delete(response: Response, UserId: UUID4, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        UserSv = session.query(UserService).filter(UserService.UserId == UserId).first()

        if UserSv is None:
            response.status_code=status.HTTP_404_NOT_FOUND
            raise Exception('No se ha encontrado ningún registro')

        UserMd = UserModel(**UserSv.dict())
        required_skills = (await list_skills_from_user(
            response=response,
            UserId=UserId,
            session=session
        )).payload
        
        skillsdict = []
        for v in required_skills:
            skillsdict.append(v.dict())
        UserMd.Skills = skillsdict

        session.delete(UserSv)
        result.payload = UserMd
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


@UserApp.put('/', status_code=status.HTTP_200_OK)
async def update(response: Response, UserMd: UserModel, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        # It let us continue with a transaction
        if session is None:
            shouldCommit = True
            session = SessionLocal()

        # Prepare to parse to Service
        UserDict = UserMd.dict()
        del UserDict['Skills']

        # Save the vacancy
        UserSv = session\
            .query(UserService)\
            .filter(UserService.UserId == UserMd.UserId)\
            .first()


        if UserSv is None:
            raise Exception('No se ha encontrado ninguna vacante')

        if UserMd.FirstName is not None:
            UserSv.FirstName = UserMd.FirstName

        if UserMd.LastName is not None:
            UserSv.LastName = UserMd.LastName

        if UserMd.Email is not None:
            UserSv.Email = UserMd.Email
        
        if UserMd.YearPreviousExperience is not None:
            UserSv.YearPreviousExperience = UserMd.YearPreviousExperience

        if UserMd.Skills is not None:
            # Solo agrega las habiliades nuevas y no las reemplaza
            for required_skill in UserMd.Skills:
                required = await attach_to_user(
                    SkillMd=required_skill,
                    vacancyId=UserMd.UserId,
                    session=session
                )

                if not required.success:
                    raise Exception('Falló la creación de una habilidad requerida.')

        result = (await detail(response, UserMd.UserId, session))

        print(result)
        # Parse to visible
        newRequired = []
        for i in result.payload.Skills:
            newRequired.append(i)

        if UserMd.Skills is not None:
            for i in UserMd.Skills:
                newRequired.append(i.dict())

        result.payload.Skills = newRequired
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


@UserApp.get('/match/{id}', status_code=200)
async def detail(response: Response, id: str, session=None) -> CommonApiResponse:
    result = CommonApiResponse(message='Operación exitosa!')
    shouldCommit = False
    try:
        if len(id) != 36:
            raise Exception('Invalid ID')
        
        if session is None:
            shouldCommit = True
            session = SessionLocal()    
        UserSkillSv = session.query(SkillUserService).filter(SkillUserService.UserId == id).all()   
        UserSkillsMd = {}
        skills = []
        for s in UserSkillSv:
            UserSkillMd = SkillModel(
                SkillId=s.SkillId,
                SkillName=session.query(SkillService).filter(SkillService.SkillId == s.SkillId).first().SkillName,
                SkillYearExperience=s.SkillYearExperience
            )
            UserSkillsMd[str(s.SkillId)] = UserSkillMd
            skills.append(str(s.SkillId))

        PossibleVacancies = session\
            .query(SkillVacancyService)\
            .distinct(SkillVacancyService.VacancyId)\
            .filter(SkillVacancyService.SkillId.in_(skills))\
            .all()

        result.payload = [] 
        for pv in PossibleVacancies:
            RequiredSkills = session\
                .query(SkillVacancyService)\
                .filter(SkillVacancyService.VacancyId == str(pv.VacancyId))\
                .all()

            coeficiente = 0 
            for rs in RequiredSkills:
                if str(rs.SkillId) in UserSkillsMd:
                    UserExp = UserSkillsMd[str(rs.SkillId)].SkillYearExperience
                    if float(UserExp) >= float(rs.SkillYearExperience):
                        coeficiente += 1 / len(RequiredSkills)  
            if coeficiente >= 0.5:
                result.payload.append(
                    (await detail_vacancy(
                        response=response,
                        VacancyId=str(pv.VacancyId),
                        session=session
                    )).payload
                )
    except Exception as e:
        print(e)
        result.message="Ha ocurrido un error"
        result.success=False
        result.payload=str(e)
    finally:
        return result
