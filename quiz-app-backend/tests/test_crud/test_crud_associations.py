# filename: tests/test_crud/test_crud_associations.py

from app.crud.crud_question_tag_associations import add_tag_to_question, get_question_tags, get_questions_by_tag
from app.crud.crud_role_permission_associations import add_permission_to_role, get_role_permissions, get_roles_by_permission


def test_question_tag_association(db_session, test_question, test_tag):
    add_tag_to_question(db_session, test_question.id, test_tag.id)
    
    question_tags = get_question_tags(db_session, test_question.id)
    assert len(question_tags) == 1
    assert question_tags[0].id == test_tag.id

    questions_with_tag = get_questions_by_tag(db_session, test_tag.id)
    assert len(questions_with_tag) == 1
    assert questions_with_tag[0].id == test_question.id

def test_role_permission_association(db_session, test_role, test_permission):
    initial_role_permissions = get_role_permissions(db_session, test_role.id)
    initial_count = len(initial_role_permissions)

    add_permission_to_role(db_session, test_role.id, test_permission.id)
    
    role_permissions = get_role_permissions(db_session, test_role.id)
    assert len(role_permissions) == initial_count + 1
    assert test_permission in role_permissions
