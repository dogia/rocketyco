from services.CompanyService import CompanyService


def test_properties():
    CompanySv = CompanyService()

    assert hasattr(CompanySv, 'CompanyId')
    assert hasattr(CompanySv, 'CompanyName')
    assert hasattr(CompanySv, 'CompanyWebsite')

    assert hasattr(CompanySv, 'created_at')
    assert hasattr(CompanySv, 'updated_at')

def test_correct_table_name():
    CompanySv = CompanyService()
    assert CompanySv.__tablename__ == CompanySv.__tablename__.lower()
