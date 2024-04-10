# filename: tests/test_crud_subjects.py

from app.schemas import SubjectCreateSchema
from app.crud import create_subject_crud

def test_create_subject(db_session):
    subject_data = SubjectCreateSchema(name="Test Subject")
    created_subject = create_subject_crud(db=db_session, subject=subject_data)
    assert created_subject.name == "Test Subject"
