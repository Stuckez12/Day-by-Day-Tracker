from src.core.database.db import get_db
from src.services import AuthService


def seed_db():
    db_gen = get_db()
    db = next(db_gen)

    try:
        AuthService(db=db).seed_user()

    finally:
        db_gen.close()
