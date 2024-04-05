from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import URL
import sys
from .config import settings

url_object = URL.create(
    "postgresql",
    username=settings.database_username,
    password=settings.database_password.get_secret_value(),
    host=settings.database_hostname,
    database=settings.database_name,
)

try:
    engine = create_engine(url_object)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit("Critical error: Unable to initialize database engine: Check URL object")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
