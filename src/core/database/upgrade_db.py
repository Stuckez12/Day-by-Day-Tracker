from alembic import command
from alembic.config import Config


def upgrade_db():
    alembic_conf = Config("alembic.ini")
    command.upgrade(alembic_conf, "head")

    alembic_conf = Config("alembic-backup.ini")
    command.upgrade(alembic_conf, "head")
