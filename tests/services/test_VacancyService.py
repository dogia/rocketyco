from services.VacancyService import VacancyService


def test_properties():
    VacancySv = VacancyService()

    assert hasattr(VacancySv, 'VacancyId')
    assert hasattr(VacancySv, 'CompanyId')
    assert hasattr(VacancySv, 'PositionName')
    assert hasattr(VacancySv, 'Salary')
    assert hasattr(VacancySv, 'Currency')
    assert hasattr(VacancySv, 'VacancyLink')

    assert hasattr(VacancySv, 'created_at')
    assert hasattr(VacancySv, 'updated_at')

def test_correct_table_name():
    VacancySv = VacancyService()
    assert VacancySv.__tablename__ == VacancySv.__tablename__.lower()
