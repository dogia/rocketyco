
import uuid
from models.SkillModel import SkillModel
from models.VacancyModel import VacancyModel


def test_properties():
    Vacancy = VacancyModel(
        CompanyId=uuid.uuid4(),
        PositionName="Unit Tester",
        RequiredSkills=[
            SkillModel(
                SkillName="Python",
                SkillYearExperience=1
            ),
            SkillModel(
                SkillName="PyTest",
                SkillYearExperience=1
            )
        ]
    )

    assert hasattr(Vacancy, 'VacancyId')
    assert hasattr(Vacancy, 'CompanyId')
    assert hasattr(Vacancy, 'PositionName')
    assert hasattr(Vacancy, 'Salary')
    assert hasattr(Vacancy, 'Currency')
    assert hasattr(Vacancy, 'VacancyLink')
    assert hasattr(Vacancy, 'RequiredSkills')

    assert type(Vacancy.VacancyId) == uuid.UUID
    assert len(str(Vacancy.VacancyId)) == 36

    assert not (str(Vacancy.RequiredSkills[0].SkillId) == str(Vacancy.RequiredSkills[1].SkillId))
