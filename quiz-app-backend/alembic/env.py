from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import Base  # Update this import to match your project structure
from app.core.config import settings_core  # Import settings_core from the correct location

# Import all your model files
# pylint: disable=unused-import
from app.models.answer_choices import AnswerChoiceModel
from app.models.associations import (
    UserToGroupAssociation,
    QuestionSetToGroupAssociation,
    QuestionToTagAssociation,
    QuestionSetToQuestionAssociation,
    RoleToPermissionAssociation
)
from app.models.authentication import RevokedTokenModel
from app.models.concepts import ConceptModel
from app.models.disciplines import DisciplineModel
from app.models.domains import DomainModel
from app.models.groups import GroupModel
from app.models.leaderboard import LeaderboardModel
from app.models.permissions import PermissionModel
from app.models.question_sets import QuestionSetModel
from app.models.question_tags import QuestionTagModel
from app.models.questions import QuestionModel
from app.models.roles import RoleModel
from app.models.sessions import SessionQuestionModel, SessionQuestionSetModel, SessionModel
from app.models.subjects import SubjectModel
from app.models.subtopics import SubtopicModel
from app.models.time_period import TimePeriodModel
from app.models.topics import TopicModel
from app.models.user_responses import UserResponseModel
from app.models.users import UserModel

target_metadata = Base.metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings_core.DATABASE_URL  # Use DATABASE_URL from settings
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
