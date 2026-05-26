from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine
from app.db.config import settings
from app.db.database import Base,get_db
from app.main import app
import pytest
from app.core.oauth2 import create_access_token

SQLALCHEMY_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_URL)
TestingSessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)



@pytest.fixture
def test_user(client):
    user_data = {
        "full_name":"N.Rakesh",
        "email":"rakesh@gmail.com",
        "password":"password123",
        "role":"admin"
    }

    response = client.post("/users/",json=user_data)

    assert response.status_code == 201
    new_user = response.json()
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id":test_user["id"]})


@pytest.fixture
def authorized_access(client,token):
    client.headers = {
        **client.headers,
        'Authorization':f'Bearer:{token}'
    }
    return client
