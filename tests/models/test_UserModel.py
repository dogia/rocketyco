
from types import NoneType
import uuid
from models.UserModel import UserModel


def test_properties():
    User = UserModel(
        UserName="User Unit Test",
        FirstName="Unit Test",
        Email="unit@test.com",
        YearPreviousExperience=1
    )

    assert hasattr(User, 'UserId')
    assert hasattr(User, 'FirstName')
    assert hasattr(User, 'LastName')
    assert hasattr(User, 'Email')
    assert hasattr(User, 'YearPreviousExperience')
    assert hasattr(User, 'Skills')

    assert type(User.UserId) == uuid.UUID
    assert len(str(User.UserId)) == 36
