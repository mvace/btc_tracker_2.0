import pytest
from httpx import AsyncClient
from fastapi import status
from faker import Faker

fake = Faker()


# _____ Register User Tests _____
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

    user_data = {"email": fake.email(), "password": fake.password()}

    initial_response = await client.post("/auth/register", json=user_data)
    assert initial_response.status_code == status.HTTP_201_CREATED

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_email",
    [
        "not-an-email",
        "test@test",
        "user@.com",
        "user@domain.",
        "@domain.com",
    ],
)
async def test_register_user_invalid_email_format(
    client: AsyncClient, invalid_email: str
):
    """
    Tests that registering with an invalid email format fails.
    """

    user_data = {"email": invalid_email, "password": fake.password()}

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_data = response.json()
    assert "value is not a valid email address" in error_data["detail"][0]["msg"]


@pytest.mark.anyio
async def test_register_user_missing_fields(client: AsyncClient):
    """
    Tests that registering with missing fields fails.
    """

    user_data = {"email": fake.email()}  # Missing password
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    user_data = {"password": fake.password()}  # Missing email
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_register_user_with_extra_fields(client: AsyncClient):
    """
    Tests that registering with extra fields ignores them and succeeds.
    """

    user_data = {
        "email": fake.email(),
        "password": fake.password(),
        "extra_field": "should be ignored",
    }

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert "extra_field" not in response_data


# _____ Login User Tests _____


@pytest.mark.anyio
async def test_login_user_success(client: AsyncClient):
    """
    Tests successful user login using dynamically generated data from Faker.
    """

    password = fake.password()
    email = fake.email()

    user_data = {"email": email, "password": password}

    register_response = await client.post("/auth/register", json=user_data)
    assert register_response.status_code == status.HTTP_201_CREATED

    login_data = {"username": email, "password": password}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access_token" in response_data
    assert isinstance(response_data["access_token"], str)
    assert response_data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_user_incorrect_password(client: AsyncClient):
    """
    Tests that logging in with an incorrect password fails.
    """

    password = fake.password()
    email = fake.email()

    user_data = {"email": email, "password": password}

    register_response = await client.post("/auth/register", json=user_data)
    assert register_response.status_code == status.HTTP_201_CREATED

    login_data = {"username": email, "password": fake.password()}  # Wrong password"}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_user_nonexistent_user(client: AsyncClient):
    """
    Tests that logging in with a nonexistent user fails.
    """

    login_data = {"username": fake.email(), "password": fake.password()}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_user_missing_fields(client: AsyncClient):
    """
    Tests that logging in with missing fields fails.
    """

    login_data = {"username": fake.email()}  # Missing password
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    login_data = {"password": fake.password()}  # Missing username
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_login_user_with_case_insensitive_email(client: AsyncClient):
    """
    Tests that logging in with an email that differs only in case succeeds.
    """

    password = fake.password()
    email = fake.email()

    user_data = {"email": email, "password": password}

    register_response = await client.post("/auth/register", json=user_data)
    assert register_response.status_code == status.HTTP_201_CREATED

    login_data = {"username": email.upper(), "password": password}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access_token" in response_data
    assert isinstance(response_data["access_token"], str)
    assert response_data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_user_with_leading_or_trailing_whitespace(client: AsyncClient):
    """
    Tests that logging in with an email that has leading or trailing whitespace succeeds.
    """

    password = fake.password()
    email = fake.email()

    user_data = {"email": email, "password": password}

    register_response = await client.post("/auth/register", json=user_data)
    assert register_response.status_code == status.HTTP_201_CREATED

    login_data = {"username": f"  {email}  ", "password": password}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "access_token" in response_data
    assert isinstance(response_data["access_token"], str)
    assert response_data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_user_login_with_empty_credentials(client: AsyncClient):
    """
    Tests that logging in with empty username and password fails.
    """

    login_data = {"username": "", "password": ""}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
