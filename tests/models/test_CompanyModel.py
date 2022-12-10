
import uuid
from models.CompanyModel import CompanyModel


def test_properties():
    Company = CompanyModel(
        CompanyName="Company Unit Test"
    )

    assert hasattr(Company, 'CompanyId')
    assert hasattr(Company, 'CompanyName')
    assert hasattr(Company, 'CompanyWebsite')

    assert type(Company.CompanyId) == uuid.UUID
    assert len(str(Company.CompanyId)) == 36
