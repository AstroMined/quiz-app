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
    # Get the actual foreign key column name, not the relationship name
    foreign_key_columns = list(relationship.local_columns)
    if not foreign_key_columns:
        return
    
    # Get the first foreign key column (most relationships have only one)
    fk_column = foreign_key_columns[0]
    fk_column_name = fk_column.key
    foreign_key_value = getattr(target, fk_column_name, None)
    
    if foreign_key_value is not None:
        try:
            # If the value is already a model instance, extract its ID
            if isinstance(foreign_key_value, Base):
                identity = inspect(foreign_key_value).identity
                if identity is None:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid {fk_column_name}: Object has no identity"
                    )
                foreign_key_value = identity[0]
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid {fk_column_name}: {str(e)}"
            ) from e

        # Validate that the foreign key value exists in the related table
        related_class = relationship.entity.class_
        related_object = (
            db.query(related_class)
            .filter(related_class.id == foreign_key_value)
            .first()
        )

        if not related_object:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid {fk_column_name}: {foreign_key_value}"
            )


def validate_multiple_foreign_keys(target, relationship, db):
    foreign_key = relationship.key
    foreign_key_values = getattr(target, foreign_key, [])

    if foreign_key_values:
        related_class = relationship.mapper.class_
        
        for i, foreign_key_value in enumerate(foreign_key_values):
            try:
                # For many-to-many relationships, objects may be new and not yet persisted
                # Only validate if we can extract a meaningful ID
                if isinstance(foreign_key_value, Base):
                    # Check if the object has a committed ID
                    if hasattr(foreign_key_value, 'id') and foreign_key_value.id is not None:
                        fk_id = foreign_key_value.id
                    else:
                        # Try to get identity from SQLAlchemy state
                        state = instance_state(foreign_key_value)
                        if state.key is None:
                            # Object has no identity - could be new in the same transaction
                            # Skip validation for objects that are part of the current session
                            # but don't have IDs yet (they'll be validated by database constraints)
                            continue
                        fk_id = state.key[1][0]  # Get the first primary key value
                else:
                    # Assume it's already an ID value
                    fk_id = foreign_key_value

                # Only validate if we have a valid ID
                if fk_id is not None:
                    # Validate that the foreign key exists in the database
                    related_object = (
                        db.query(related_class)
                        .filter(related_class.id == fk_id)
                        .first()
                    )

                    if not related_object:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid {foreign_key}[{i}]: {fk_id}",
                        )
            except HTTPException:
                # Re-raise HTTPExceptions as-is
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error validating {foreign_key}[{i}]: {str(e)}"
                ) from e


def validate_direct_foreign_keys(target, db):
    # Use SQLAlchemy introspection to find foreign key constraints
    table = target.__table__
    
    for fk_constraint in table.foreign_key_constraints:
        for fk_column in fk_constraint.columns:
            fk_value = getattr(target, fk_column.key, None)
            
            if fk_value is not None:
                # Get the referenced table and column
                referenced_table = fk_constraint.referred_table
                referenced_column = list(fk_constraint.elements)[0].column
                
                # Find the corresponding model class for the referenced table
                related_class = find_related_class_by_table(referenced_table.name)
                
                if related_class:
                    # Check if the foreign key value exists in the referenced table
                    related_object = (
                        db.query(related_class)
                        .filter(getattr(related_class, referenced_column.key) == fk_value)
                        .first()
                    )
                    
                    if not related_object:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Invalid {fk_column.key}: {fk_value}"
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


def find_related_class_by_table(table_name):
    """
    Maps table names to their corresponding SQLAlchemy model classes.
    Used by validate_direct_foreign_keys for dynamic foreign key validation.

    Args:
        table_name (str): The name of the database table.

    Returns:
        type: The corresponding SQLAlchemy model class, or None if no mapping is found.
    """
    table_to_class = {
        "questions": QuestionModel,
        "groups": GroupModel,
        "users": UserModel,
        "permissions": PermissionModel,
        "roles": RoleModel,
        "subjects": SubjectModel,
        "topics": TopicModel,
        "subtopics": SubtopicModel,
        "question_tags": QuestionTagModel,
        "leaderboard": LeaderboardModel,
        "user_responses": UserResponseModel,
        "answer_choices": AnswerChoiceModel,
        "question_sets": QuestionSetModel,
        "revoked_tokens": RevokedTokenModel,
    }

    return table_to_class.get(table_name)


def register_validation_listeners():
    if hasattr(Base, "_decl_class_registry"):
        model_classes = Base._decl_class_registry.values()
    else:
        model_classes = Base.registry._class_registry.values()

    for model_class in model_classes:
        if hasattr(model_class, "__tablename__"):
            event.listen(model_class, "before_insert", validate_foreign_keys)
            event.listen(model_class, "before_update", validate_foreign_keys)
