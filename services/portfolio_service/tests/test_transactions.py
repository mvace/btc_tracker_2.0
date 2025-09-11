import pytest
from httpx import AsyncClient
from fastapi import status
from faker import Faker
from decimal import Decimal
from app.schemas.transactions import PriceData
from datetime import datetime

fake = Faker()


class TestCreateTransaction:

    mock_price_data = PriceData(
        unix_timestamp=1756908000,
        high=112545.3,
        low=111143.27,
        open=111491.96,
        close=112293.52,
        volumefrom=2809.0,
        volumeto=314166893.0,
    )

    @pytest.mark.anyio
    async def test_create_transaction_success(
        self, client: AsyncClient, auth_headers: dict, created_portfolio: dict, mocker
    ):
        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=self.mock_price_data,
        )

        transaction_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": "0.01",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.post(
            "/transaction/", json=transaction_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        transaction = response.json()
        assert transaction["portfolio_id"] == created_portfolio["id"]
        assert Decimal(transaction["btc_amount"]) == Decimal("0.01")
        assert Decimal(transaction["price_at_purchase"]) == Decimal("112293.52")
        assert Decimal(transaction["initial_value_usd"]) == (
            Decimal("0.01") * Decimal("112293.52")
        ).quantize(Decimal("0.01"))

    @pytest.mark.anyio
    async def test_create_transaction_unauthenticated_user_returns_401(
        self, client: AsyncClient, created_portfolio: dict
    ):
        transaction_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": "0.01",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.post("/transaction/", json=transaction_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_create_transaction_nonexistent_portfolio_returns_404(
        self, client: AsyncClient, auth_headers: dict, mocker
    ):
        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=self.mock_price_data,
        )

        transaction_data = {
            "portfolio_id": 9999,  # Non-existent portfolio ID
            "btc_amount": "0.01",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.post(
            "/transaction/", json=transaction_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_create_transaction_invalid_data_returns_422(
        self, client: AsyncClient, auth_headers: dict, created_portfolio: dict
    ):
        transaction_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": "invalid_amount",  # Invalid btc_amount
            "timestamp": "invalid_timestamp",  # Invalid timestamp
        }
        response = await client.post(
            "/transaction/", json=transaction_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_create_transaction_with_missing_data_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        transaction_data = {
            # Missing portfolio_id
            "btc_amount": "0.01",
            # Missing timestamp
        }
        response = await client.post(
            "/transaction/", json=transaction_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_create_transaction_when_price_service_fails(
        self, client: AsyncClient, auth_headers: dict, created_portfolio: dict, mocker
    ):
        # Mock the fetch_btc_price_data_for_timestamp function to raise an exception
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            side_effect=Exception("Price service unavailable"),
        )

        transaction_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": "0.01",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        # Use pytest.raises to assert that an Exception is raised
        with pytest.raises(Exception) as exc_info:
            await client.post(
                "/transaction/", json=transaction_data, headers=auth_headers
            )

        # Optionally, assert that the exception message is what you expect
        assert "Price service unavailable" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_create_transaction_for_other_users_portfolio_returns_404(
        self, client: AsyncClient, auth_headers: dict, created_portfolio: dict, mocker
    ):
        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=self.mock_price_data,
        )

        # Create second user and get their auth headers
        second_user_data = {
            "email": fake.email(),
            "password": fake.password(),
        }
        response = await client.post("/auth/register", json=second_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        login_data = {
            "username": second_user_data["email"],
            "password": second_user_data["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        second_user_token = login_response.json()["access_token"]
        second_user_headers = {"Authorization": f"Bearer {second_user_token}"}

        transaction_data = {
            "portfolio_id": created_portfolio["id"],  # Portfolio of the first user
            "btc_amount": "0.01",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.post(
            "/transaction/", json=transaction_data, headers=second_user_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetTransaction:
    @pytest.mark.anyio
    async def test_get_transaction_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_transaction: dict,
        created_portfolio: dict,
    ):
        transaction_id = created_transaction["id"]
        response = await client.get(
            f"/transaction/{transaction_id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        transaction = response.json()
        assert transaction["id"] == transaction_id
        assert transaction["portfolio_id"] == created_portfolio["id"]
        assert Decimal(transaction["btc_amount"]) == Decimal("0.01")

    @pytest.mark.anyio
    async def test_get_transaction_unauthenticated_user_returns_401(
        self, client: AsyncClient, created_transaction: dict
    ):
        transaction_id = created_transaction["id"]
        response = await client.get(f"/transaction/{transaction_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_get_transaction_nonexistent_id_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get("/transaction/9999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_get_transaction_other_users_transaction_returns_404(
        self, client: AsyncClient, created_transaction: dict
    ):

        transaction_id = created_transaction["id"]

        # Create second user and get their auth headers
        second_user_data = {
            "email": fake.email(),
            "password": fake.password(),
        }
        response = await client.post("/auth/register", json=second_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        login_data = {
            "username": second_user_data["email"],
            "password": second_user_data["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        second_user_token = login_response.json()["access_token"]
        second_user_headers = {"Authorization": f"Bearer {second_user_token}"}
        # Attempt to get the first user's transaction with the second user's auth headers
        response = await client.get(
            f"/transaction/{transaction_id}", headers=second_user_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_get_transaction_invalid_id_format_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get("/transaction/invalid_id", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListTransactions:

    @pytest.mark.anyio
    async def test_list_transactions_unauthenticated_user_returns_401(
        self, client: AsyncClient
    ):
        response = await client.get("/transaction/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_list_transactions_no_transactions_returns_empty_list(
        self, client: AsyncClient, auth_headers: dict
    ):

        response = await client.get("/transaction/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.anyio
    async def test_list_transactions_with_existing_transactions_returns_them(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_transaction: dict,
        created_portfolio: dict,
    ):

        list_response = await client.get("/transaction/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        transactions = list_response.json()
        assert len(transactions) == 1
        assert transactions[0]["portfolio_id"] == created_portfolio["id"]
        assert Decimal(transactions[0]["btc_amount"]) == Decimal("0.01")

    @pytest.mark.anyio
    async def test_list_transactions_does_not_return_other_users_transactions(
        self, client: AsyncClient, auth_headers: dict, created_transaction: dict
    ):
        """
        Tests that listing transactions does not return transactions belonging to other users.
        """
        # Create second user and get their auth headers
        second_user_data = {
            "email": fake.email(),
            "password": fake.password(),
        }
        response = await client.post("/auth/register", json=second_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        login_data = {
            "username": second_user_data["email"],
            "password": second_user_data["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        second_user_token = login_response.json()["access_token"]
        second_user_headers = {"Authorization": f"Bearer {second_user_token}"}

        list_response = await client.get("/transaction/", headers=second_user_headers)
        assert list_response.status_code == status.HTTP_200_OK
        transactions = list_response.json()
        assert len(transactions) == 0

    @pytest.mark.anyio
    async def test_list_transactions_returns_all_transactions_for_a_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_portfolio: dict,
        mocker,  # <-- 1. Add the mocker fixture here
    ):
        """
        Tests that listing transactions returns all transactions for the authenticated user.
        """

        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mock_price_data = PriceData(
            unix_timestamp=1756908000,
            high=112545.3,
            low=111143.27,
            open=111491.96,
            close=112293.52,
            volumefrom=2809.0,
            volumeto=314166893.0,
        )
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=mock_price_data,
        )
        # Create multiple transactions for the same portfolio
        for _ in range(3):
            transaction_data = {
                "portfolio_id": created_portfolio["id"],
                "btc_amount": "0.01",
                "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
            }
            create_response = await client.post(
                "/transaction/", json=transaction_data, headers=auth_headers
            )
            assert create_response.status_code == status.HTTP_201_CREATED
        # List transactions
        list_response = await client.get("/transaction/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        transactions = list_response.json()
        assert len(transactions) == 3  # Should return all 3 transactions

    @pytest.mark.anyio
    async def test_list_transactions_returns_transactions_from_multiple_portfolios(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_portfolio: dict,
        mocker,  # <-- 1. Add the mocker fixture here
    ):
        """
        Tests that listing transactions returns transactions from multiple portfolios of the authenticated user.
        """

        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mock_price_data = PriceData(
            unix_timestamp=1756908000,
            high=112545.3,
            low=111143.27,
            open=111491.96,
            close=112293.52,
            volumefrom=2809.0,
            volumeto=314166893.0,
        )
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=mock_price_data,
        )
        # Create a second portfolio for the same user
        portfolio_data2 = {"name": "Second Portfolio"}
        create_response2 = await client.post(
            "/portfolio/", json=portfolio_data2, headers=auth_headers
        )
        assert create_response2.status_code == status.HTTP_201_CREATED
        portfolio2 = create_response2.json()

        # Create transactions in both portfolios
        for portfolio in [created_portfolio, portfolio2]:
            for _ in range(2):
                transaction_data = {
                    "portfolio_id": portfolio["id"],
                    "btc_amount": "0.01",
                    "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
                }
                create_response = await client.post(
                    "/transaction/", json=transaction_data, headers=auth_headers
                )
                assert create_response.status_code == status.HTTP_201_CREATED

        # List transactions
        list_response = await client.get("/transaction/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        transactions = list_response.json()
        assert len(transactions) == 4

    @pytest.mark.anyio
    async def test_list_transactions_response_matches_schema(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_transaction: dict,
    ):
        """
        Tests that the response from listing transactions matches the TransactionRead schema.
        """
        list_response = await client.get("/transaction/", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        transactions = list_response.json()
        assert len(transactions) == 1

        transaction = transactions[0]
        # Check that all expected fields are present
        expected_fields = {
            "id",
            "portfolio_id",
            "btc_amount",
            "price_at_purchase",
            "initial_value_usd",
            "timestamp_hour_rounded",
        }
        assert expected_fields.issubset(transaction.keys())

        # Validate field types
        assert isinstance(transaction["id"], int)
        assert isinstance(transaction["portfolio_id"], int)
        assert isinstance(Decimal(transaction["btc_amount"]), Decimal)
        assert isinstance(Decimal(transaction["price_at_purchase"]), Decimal)
        assert isinstance(Decimal(transaction["initial_value_usd"]), Decimal)
        # Check that timestamp_hour_rounded is a valid ISO 8601 datetime string
        try:
            datetime.fromisoformat(
                transaction["timestamp_hour_rounded"].replace("Z", "+00:00")
            )
            is_valid_datetime = True
        except ValueError:
            is_valid_datetime = False
        assert is_valid_datetime


class TestUpdateTransaction:
    mock_price_data = PriceData(
        unix_timestamp=1756908000,
        high=112545.3,
        low=111143.27,
        open=111491.96,
        close=112293.52,
        volumefrom=2809.0,
        volumeto=314166893.0,
    )

    @pytest.mark.anyio
    async def test_update_transaction_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_transaction: dict,
        created_portfolio: dict,
        mocker,
    ):
        """
        Tests that updating a transaction works as expected.
        """

        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=self.mock_price_data,
        )

        transaction_id = created_transaction["id"]
        new_btc_amount = "0.02"
        new_timestamp = fake.date_time_this_year(tzinfo=None).isoformat()
        update_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": new_btc_amount,
            "timestamp": new_timestamp,
        }
        response = await client.put(
            f"/transaction/{transaction_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        updated_transaction = response.json()
        assert updated_transaction["id"] == transaction_id
        assert Decimal(updated_transaction["btc_amount"]) == Decimal(new_btc_amount)
        assert Decimal(updated_transaction["price_at_purchase"]) == Decimal("112293.52")
        assert Decimal(updated_transaction["initial_value_usd"]) == (
            Decimal(new_btc_amount) * Decimal("112293.52")
        ).quantize(Decimal("0.01"))

    @pytest.mark.anyio
    async def test_update_transaction_unauthenticated_user_returns_401(
        self, client: AsyncClient, created_transaction: dict, created_portfolio: dict
    ):
        """
        Tests that an unauthenticated user cannot update a transaction.
        """
        transaction_id = created_transaction["id"]
        update_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": "0.02",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.put(f"/transaction/{transaction_id}", json=update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_update_transaction_nonexistent_id_returns_404(
        self, client: AsyncClient, auth_headers: dict, created_portfolio: dict
    ):
        """
        Tests that updating a non-existent transaction returns 404.
        """
        update_data = {
            "portfolio_id": created_portfolio["id"],
            "btc_amount": "0.02",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.put(
            "/transaction/9999", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_update_transaction_invalid_data_returns_422(
        self, client: AsyncClient, auth_headers: dict, created_transaction: dict
    ):
        """
        Tests that updating a transaction with invalid data returns 422.
        """
        transaction_id = created_transaction["id"]
        update_data = {
            "portfolio_id": created_transaction["portfolio_id"],
            "btc_amount": "invalid_amount",  # Invalid btc_amount
            "timestamp": "invalid_timestamp",  # Invalid timestamp
        }
        response = await client.put(
            f"/transaction/{transaction_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_update_transaction_for_other_users_transaction_returns_404(
        self, client: AsyncClient, auth_headers: dict, created_transaction: dict, mocker
    ):
        """
        Tests that attempting to update another user's transaction returns 404.
        """
        # Mock the fetch_btc_price_data_for_timestamp function to avoid real HTTP calls
        mocker.patch(
            "app.routers.transactions.fetch_btc_price_data_for_timestamp",
            return_value=self.mock_price_data,
        )

        transaction_id = created_transaction["id"]

        # Create second user and get their auth headers
        second_user_data = {
            "email": fake.email(),
            "password": fake.password(),
        }
        response = await client.post("/auth/register", json=second_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        login_data = {
            "username": second_user_data["email"],
            "password": second_user_data["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        second_user_token = login_response.json()["access_token"]
        second_user_headers = {"Authorization": f"Bearer {second_user_token}"}

        update_data = {
            "portfolio_id": created_transaction["portfolio_id"],
            "btc_amount": "0.02",
            "timestamp": fake.date_time_this_year(tzinfo=None).isoformat(),
        }
        response = await client.put(
            f"/transaction/{transaction_id}",
            json=update_data,
            headers=second_user_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTransaction:
    @pytest.mark.anyio
    async def test_delete_transaction_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_transaction: dict,
    ):
        """
        Tests that deleting a transaction works as expected.
        """
        transaction_id = created_transaction["id"]
        response = await client.delete(
            f"/transaction/{transaction_id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify that the transaction is actually deleted
        get_response = await client.get(
            f"/transaction/{transaction_id}", headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_delete_transaction_unauthenticated_user_returns_401(
        self, client: AsyncClient, created_transaction: dict
    ):
        """
        Tests that an unauthenticated user cannot delete a transaction.
        """

        transaction_id = created_transaction["id"]
        response = await client.delete(f"/transaction/{transaction_id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.anyio
    async def test_delete_transaction_nonexistent_id_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that deleting a non-existent transaction returns 404.
        """
        response = await client.delete("/transaction/9999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_delete_transaction_other_users_transaction_returns_404(
        self, client: AsyncClient, created_transaction: dict
    ):
        """
        Tests that attempting to delete another user's transaction returns 404.
        """

        transaction_id = created_transaction["id"]

        # Create second user and get their auth headers
        second_user_data = {
            "email": fake.email(),
            "password": fake.password(),
        }
        response = await client.post("/auth/register", json=second_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        login_data = {
            "username": second_user_data["email"],
            "password": second_user_data["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        second_user_token = login_response.json()["access_token"]
        second_user_headers = {"Authorization": f"Bearer {second_user_token}"}

        # Attempt to delete the first user's transaction with the second user's auth headers
        response = await client.delete(
            f"/transaction/{transaction_id}", headers=second_user_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
