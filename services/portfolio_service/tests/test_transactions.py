import pytest
from httpx import AsyncClient
from fastapi import status
from faker import Faker

fake = Faker()


class TestListTransactions:

    @pytest.mark.anyio
    async def test_list_transactions_unauthenticated_user_returns_401(
        self, client: AsyncClient
    ):
        response = await client.get("/transaction/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_list_transactions_no_transactions_returns_empty_list(
        self, client: AsyncClient, created_user: dict
    ):
        # First, log in to get the token
        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Now, use the token to access the protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/transaction/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.anyio
