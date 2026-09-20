"""
Shared pytest fixtures.

Uses an in-memory SQLite database instead of the real Postgres instance
`database.py` points at, so the test suite runs anywhere with no external
services. Each test gets a fresh schema and a fresh session.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  
from database import Base, get_db


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


    @event.listens_for(eng, "connect")
    def _fk_pragma_on_connect(dbapi_con, _):
        dbapi_con.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(engine, monkeypatch):
    """A TestClient wired to the in-memory DB via dependency override.

    main.py runs `Base.metadata.create_all(bind=engine)` against the real
    Postgres engine at import time, so `database.engine` is patched to the
    in-memory engine *before* main is first imported.
    """
    import database as database_module
    monkeypatch.setattr(database_module, "engine", engine)

    from fastapi.testclient import TestClient
    from main import app

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
