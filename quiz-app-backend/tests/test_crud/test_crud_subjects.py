# filename: tests/test_crud_subjects.py

from app.schemas.subjects import SubjectCreateSchema
from app.crud.crud_subjects import create_subject


def test_create_subject(db_session, test_discipline):
    subject_data = SubjectCreateSchema(
        name="Test Subject",
        discipline_id=test_discipline.id
    )
    created_subject = create_subject(db=db_session, subject=subject_data)
    assert created_subject.name == "Test Subject"
    assert created_subject.discipline_id == test_discipline.id
