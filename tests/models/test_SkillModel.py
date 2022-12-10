
import uuid
from models.SkillModel import SkillModel


def test_properties():
    Skill = SkillModel(
        SkillName="Skill Unit Test",
        SkillYearExperience=1
    )

    assert hasattr(Skill, 'SkillId')
    assert hasattr(Skill, 'SkillName')
    assert hasattr(Skill, 'SkillYearExperience')

    assert type(Skill.SkillId) == uuid.UUID
    assert len(str(Skill.SkillId)) == 36