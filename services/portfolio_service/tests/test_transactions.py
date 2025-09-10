import pytest
from httpx import AsyncClient
from fastapi import status
from faker import Faker
from decimal import Decimal
from app.schemas.transactions import PriceData
from datetime import datetime

fake = Faker()


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
        pass

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
