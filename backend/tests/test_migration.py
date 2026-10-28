import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.base import Base
from sqlalchemy import create_engine, inspect


def test_migration_matches_model_columns(tmp_path, monkeypatch):
    database_path = tmp_path / "mig.db"
    url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    backend = Path(__file__).resolve().parents[1]
    previous = os.getcwd()
    os.chdir(backend)
    try:
        config = Config(str(backend / "alembic.ini"))
        command.upgrade(config, "head")
        engine = create_engine(url)
        inspector = inspect(engine)
        for table_name, table in Base.metadata.tables.items():
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            assert columns == set(table.columns.keys()), table_name
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        engine.dispose()
    finally:
        os.chdir(previous)
        get_settings.cache_clear()
