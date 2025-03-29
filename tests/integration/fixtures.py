import pytest
import tempfile
from sqlmodel import SQLModel, create_engine, Session, select
from unittest.mock import patch

from src.app import database as db
from src.app.db_loading import AudioInfo


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    session = Session(engine)
    yield session


@pytest.fixture
def db_uri():
    file = tempfile.NamedTemporaryFile()
    uri = f"sqlite:///{file.name}"
    engine = create_engine(uri)
    SQLModel.metadata.create_all(engine)

    yield uri
