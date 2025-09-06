import pytest
from httpx import AsyncClient
from fastapi import status
from faker import Faker

fake = Faker()


@pytest.mark.anyio
async def test_register_user_success(client: AsyncClient):
    """
    Tests successful user registration using dynamically generated data from Faker.
    """

    password = fake.password()
    email = fake.email()

    user_data = {"email": email, "password": password}

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["email"] == email
    assert "id" in response_data
    assert "created_at" in response_data
    assert "password_hash" not in response_data


@pytest.mark.anyio
async def test_register_user_duplicate_email(client: AsyncClient):
    """
    Tests that registering with a duplicate email fails.
    This version uses the API to set up the initial user.
    """

    user_data = {"email": fake.email(), "password": fake.password(length=12)}

    initial_response = await client.post("/auth/register", json=user_data)
    assert initial_response.status_code == status.HTTP_201_CREATED

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"
