# filename: tests/test_services/test_authorization_service.py

from app.services.authorization_service import get_user_permissions
from app.models.roles import RoleModel
from app.models.permissions import PermissionModel
from app.models.users import UserModel


def test_get_user_permissions(db_session):
    # Create a role and permissions
    role = RoleModel(name='Test Role', description='Test role description')
    permission1 = PermissionModel(name='Test Permission 1', description='Test permission 1 description')
    permission2 = PermissionModel(name='Test Permission 2', description='Test permission 2 description')
    role.permissions.extend([permission1, permission2])

    db_session.add(role)
    db_session.commit()

    # Create a user with the test role
    user = UserModel(username='testuser', email='testuser@example.com', role='Test Role')
    db_session.add(user)
    db_session.commit()

    # Retrieve the user's permissions
    permissions = get_user_permissions(db_session, user)
    assert len(permissions) == 2
    assert 'Test Permission 1' in permissions
    assert 'Test Permission 2' in permissions