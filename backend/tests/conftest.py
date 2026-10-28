import os

os.environ["JWT_SECRET"] = "test-secret-key-for-cyberquest-32bytes"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["BCRYPT_ROUNDS"] = "4"
os.environ["AI_PROVIDER"] = "deterministic"
os.environ["HINT_LIMIT_PER_MISSION"] = "3"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest
from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.base import Base
from app.infrastructure.database.seed import seed_catalog
from app.infrastructure.database.session import get_db
from app.infrastructure.rate_limit import rate_limiter
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    rate_limiter.reset()
    yield
    rate_limiter.reset()


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    seed_catalog(session)
    session.commit()

    def override_db():
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(engine)
