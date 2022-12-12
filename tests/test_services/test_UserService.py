from services.UserService import UserService


def test_properties():
    UserSv = UserService()

    assert hasattr(UserSv, 'UserId')
    assert hasattr(UserSv, 'FirstName')
    assert hasattr(UserSv, 'LastName')
    assert hasattr(UserSv, 'Email')
    assert hasattr(UserSv, 'YearPreviousExperience')

    assert hasattr(UserSv, 'created_at')
    assert hasattr(UserSv, 'updated_at')

def test_correct_table_name():
    UserSv = UserService()
    assert UserSv.__tablename__ == UserSv.__tablename__.lower()
