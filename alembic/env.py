import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app.core.config import settings_core
from backend.app.db.base import Base
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.associations import (DisciplineToSubjectAssociation,
                                             DomainToDisciplineAssociation,
                                             QuestionSetToGroupAssociation,
                                             QuestionSetToQuestionAssociation,
                                             QuestionToAnswerAssociation,
                                             QuestionToConceptAssociation,
                                             QuestionToSubjectAssociation,
                                             QuestionToSubtopicAssociation,
                                             QuestionToTagAssociation,
                                             QuestionToTopicAssociation,
                                             RoleToPermissionAssociation,
                                             SubjectToTopicAssociation,
                                             SubtopicToConceptAssociation,
                                             TopicToSubtopicAssociation,
                                             UserToGroupAssociation)
from backend.app.models.authentication import RevokedTokenModel
from backend.app.models.concepts import ConceptModel
from backend.app.models.disciplines import DisciplineModel
from backend.app.models.domains import DomainModel
from backend.app.models.groups import GroupModel
from backend.app.models.leaderboard import LeaderboardModel
from backend.app.models.permissions import PermissionModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel
from backend.app.models.questions import QuestionModel
from backend.app.models.roles import RoleModel
from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.time_period import TimePeriodModel
from backend.app.models.topics import TopicModel
from backend.app.models.user_responses import UserResponseModel
from backend.app.models.users import UserModel

# Import all your model files
# pylint: disable=unused-import
# In your Alembic env.py file


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
