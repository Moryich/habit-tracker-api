import pytest
from sqlalchemy import select

from app.models.user import User
from app.core.security import decode_access_token, hash_password

# auth routes block
@pytest.mark.asyncio
async def test_registration_success(client_fixture, session_fixture):
    response = await client_fixture.post("/auth/registration", json={"username": "test", "email": "test@test.com", "password": "test"})
    assert response.status_code == 201

    data = response.json()
    
    user = (await session_fixture.execute(select(User).where(User.email == "test@test.com"))).scalar_one()
    
    assert user.email == "test@test.com"
    assert user.username == "test"
    assert user.hashed_password != "test"

    assert "access_token" in data

    payload = decode_access_token(data["access_token"])
    assert int(payload["sub"]) == user.user_id

@pytest.mark.asyncio
async def test_login_success(client_fixture, session_fixture):
    new_user = User(
        username = "test",
        email = "test@test.com",
        hashed_password = hash_password("test")
    )

    session_fixture.add(new_user)
    await session_fixture.commit()

    response = await client_fixture.post("/auth/login", json={"email": "test@test.com", "password": "test"})
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data

    payload = decode_access_token(data["access_token"])
    assert int(payload["sub"]) == new_user.user_id

# login brute-force protection block
@pytest.mark.asyncio
async def test_brute_force_exception(client_fixture, brute_force_email_fixture):
    response = await client_fixture.post("/auth/registration", json={"username": "test", "email": brute_force_email_fixture, "password": "test"})
    assert response.status_code == 201
    for _ in range(5):
        response = await client_fixture.post("/auth/login", json={"email": brute_force_email_fixture, "password": "fake"})
        assert response.status_code == 401

    response = await client_fixture.post("/auth/login", json={"email": brute_force_email_fixture, "password": "fake"})
    assert response.status_code == 429
