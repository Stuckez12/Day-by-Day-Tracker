from alembic import command
from alembic.config import Config


def upgrade_db():
    alembic_conf = Config("alembic.ini")
    command.upgrade(alembic_conf, "head")


if __name__ == "__main__":
    upgrade_db()
