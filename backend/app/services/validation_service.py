# filename: backend/app/services/validation_service.py

from fastapi import HTTPException
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.orm.base import instance_state

from backend.app.db.base import Base
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.groups import GroupModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel
from backend.app.services.logging_service import sqlalchemy_obj_to_dict


def validate_foreign_keys(mapper, connection, target):
    target_contents = sqlalchemy_obj_to_dict(target)
    db = Session(bind=connection)
    inspector = inspect(target.__class__)

    for relationship in inspector.relationships:
        if relationship.direction.name == "MANYTOONE":
            validate_single_foreign_key(target, relationship, db)
        elif relationship.direction.name in ["ONETOMANY", "MANYTOMANY"]:
            validate_multiple_foreign_keys(target, relationship, db)

    validate_direct_foreign_keys(target, db)


def validate_single_foreign_key(target, relationship, db):
    foreign_key = relationship.key
    foreign_key_value = getattr(target, foreign_key)

    if foreign_key_value is not None:
        try:
            if isinstance(foreign_key_value, Base):
                foreign_key_value = inspect(foreign_key_value).identity[0]
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="Invalid foreign key value"
            ) from e

        related_class = relationship.entity.class_
        related_object = (
            db.query(related_class)
            .filter(related_class.id == foreign_key_value)
            .first()
        )

        if not related_object:
            raise HTTPException(status_code=400, detail=f"Invalid {foreign_key}")


def validate_multiple_foreign_keys(target, relationship, db):
    foreign_key = relationship.key
    foreign_key_values = getattr(target, foreign_key)

    if foreign_key_values:
        for foreign_key_value in foreign_key_values:
            try:
                if isinstance(foreign_key_value, Base):
                    state = instance_state(foreign_key_value)
                    if state.key is None:
                        continue
                    foreign_key_value = state.key[1][
                        0
                    ]  # Get the first primary key value

                related_class = relationship.mapper.class_
                related_object = (
                    db.query(related_class)
                    .filter(related_class.id == foreign_key_value)
                    .first()
                )

                if not related_object:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid {foreign_key}: {foreign_key_value}",
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Error validating {foreign_key}: {str(e)}"
                ) from e


def validate_direct_foreign_keys(target, db):
    target_contents = sqlalchemy_obj_to_dict(target)

    # Iterate through each attribute in the target object
    for attribute, value in target_contents.items():
        if isinstance(value, int):  # Assuming foreign keys are integers
            related_class = find_related_class(attribute)
            if related_class:
                related_object = (
                    db.query(related_class).filter(related_class.id == value).first()
                )
                if not related_object:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid {attribute}: {value}"
                    )


def find_related_class(attribute_name):
    """
    Maps attribute names to their corresponding SQLAlchemy model classes.
    This function should be periodically reviewed and updated to ensure all mappings are current.

    Args:
        attribute_name (str): The name of the attribute to map.

    Returns:
        type: The corresponding SQLAlchemy model class, or None if no mapping is found.
    """
    related_classes = {
        "question_id": QuestionModel,
        "group_id": GroupModel,
        "user_id": UserModel,
        "permission_id": PermissionModel,
        "role_id": RoleModel,
        "subject_id": SubjectModel,
        "topic_id": TopicModel,
        "subtopic_id": SubtopicModel,
        "question_tag_id": QuestionTagModel,
        "leaderboard_id": LeaderboardModel,
        "user_response_id": UserResponseModel,
        "answer_choice_id": AnswerChoiceModel,
        "question_set_id": QuestionSetModel,
        "token_id": RevokedTokenModel,
        # We don't need to map the association tables here, as their columns
        # are already covered by the above mappings (e.g., 'user_id', 'group_id', etc.)
    }

    return related_classes.get(attribute_name)


def register_validation_listeners():
    if hasattr(Base, "_decl_class_registry"):
        model_classes = Base._decl_class_registry.values()
    else:
        model_classes = Base.registry._class_registry.values()

    for model_class in model_classes:
        if hasattr(model_class, "__tablename__"):
            event.listen(model_class, "before_insert", validate_foreign_keys)
            event.listen(model_class, "before_update", validate_foreign_keys)
