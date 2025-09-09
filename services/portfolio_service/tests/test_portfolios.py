import pytest
from httpx import AsyncClient
from fastapi import status
from faker import Faker

fake = Faker()


class TestListPortfolios:
    @pytest.mark.anyio
    async def test_list_portfolios_unauthenticated(self, client: AsyncClient):
        """
        Tests that accessing the list portfolios endpoint without authentication fails.
        """
        response = await client.get("/portfolio/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_list_portfolios_success_as_authenticated_user(
        self, client: AsyncClient, created_portfolio: dict, auth_headers: dict
    ):
        """
        Tests successful retrieval of portfolios for an authenticated user.
        """
        # List portfolios
        response = await client.get("/portfolio/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        portfolios = response.json()
        assert isinstance(portfolios, list)
        assert len(portfolios) == 1
        assert portfolios[0]["name"] == "Test Portfolio"

    @pytest.mark.anyio
    async def test_list_portfolios_returns_empty_list_for_user_with_no_portfolios(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that an authenticated user with no portfolios receives an empty list.
        """
        # List portfolios without creating any
        response = await client.get("/portfolio/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        portfolios = response.json()
        assert isinstance(portfolios, list)
        assert len(portfolios) == 0

    @pytest.mark.anyio
    async def test_list_portfolios_does_not_show_other_users_portfolios(
        self,
        client: AsyncClient,
        created_portfolio: dict,
    ):
        """
        Tests that a user cannot see portfolios belonging to another user.
        """

        # Create second user
        password2 = fake.password()
        email2 = fake.email()
        user_data2 = {"email": email2, "password": password2}
        register_response2 = await client.post("/auth/register", json=user_data2)
        assert register_response2.status_code == status.HTTP_201_CREATED
        login_data2 = {"username": email2, "password": password2}
        login_response2 = await client.post("/auth/token", data=login_data2)
        assert login_response2.status_code == status.HTTP_200_OK
        token2 = login_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # List portfolios as the second user
        response = await client.get("/portfolio/", headers=headers2)
        assert response.status_code == status.HTTP_200_OK
        portfolios = response.json()
        assert isinstance(portfolios, list)
        assert len(portfolios) == 0


class TestGetPortfolio:
    @pytest.mark.anyio
    async def test_get_portfolio_success(
        self, client: AsyncClient, created_portfolio: dict, auth_headers: dict
    ):
        """
        Tests successful retrieval of a specific portfolio by its ID for an authenticated user.
        """

        portfolio_id = created_portfolio["id"]

        # Now retrieve the specific portfolio by ID
        response = await client.get(f"/portfolio/{portfolio_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        portfolio = response.json()
        assert portfolio["id"] == portfolio_id
        assert portfolio["name"] == "Test Portfolio"

    @pytest.mark.anyio
    async def test_get_portfolio_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that retrieving a non-existent portfolio returns a 404 error.
        """

        # Attempt to retrieve a portfolio with an ID that doesn't exist
        non_existent_portfolio_id = 9999
        response = await client.get(
            f"/portfolio/{non_existent_portfolio_id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Portfolio not found"

    @pytest.mark.anyio
    async def test_get_portfolio_unauthenticated(self, client: AsyncClient):
        """
        Tests that accessing the get portfolio endpoint without authentication fails.
        """
        response = await client.get("/portfolio/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_get_portfolio_forbidden_access(
        self, client: AsyncClient, created_portfolio: dict
    ):
        """
        Tests that a user cannot access a portfolio belonging to another user.
        """

        # First user's portfolio
        portfolio_id1 = created_portfolio["id"]

        # Create second user
        password2 = fake.password()
        email2 = fake.email()
        user_data2 = {"email": email2, "password": password2}
        register_response2 = await client.post("/auth/register", json=user_data2)
        assert register_response2.status_code == status.HTTP_201_CREATED
        login_data2 = {"username": email2, "password": password2}
        login_response2 = await client.post("/auth/token", data=login_data2)
        assert login_response2.status_code == status.HTTP_200_OK
        token2 = login_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Attempt to retrieve the first user's portfolio as the second user
        response = await client.get(f"/portfolio/{portfolio_id1}", headers=headers2)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Portfolio not found"

        @pytest.mark.anyio
        async def test_get_portfolio_invalid_id(
            self, client: AsyncClient, auth_headers: dict
        ):
            """
            Tests that providing an invalid portfolio ID returns a 422 error.
            """
            # Attempt to retrieve a portfolio with an invalid ID
            invalid_portfolio_id = "invalid_id"
            response = await client.get(
                f"/portfolio/{invalid_portfolio_id}", headers=auth_headers
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreatePortfolio:
    @pytest.mark.anyio
    async def test_create_portfolio_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests successful creation of a portfolio for an authenticated user.
        """
        # Create a portfolio for the user
        portfolio_data = {"name": "My Portfolio"}
        create_response = await client.post(
            "/portfolio/", json=portfolio_data, headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created_portfolio = create_response.json()
        assert created_portfolio["name"] == "My Portfolio"
        assert "id" in created_portfolio

    @pytest.mark.anyio
    async def test_create_portfolio_unauthenticated(self, client: AsyncClient):
        """
        Tests that creating a portfolio without authentication fails.
        """
        portfolio_data = {"name": "My Portfolio"}
        response = await client.post("/portfolio/", json=portfolio_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.anyio
    async def test_create_portfolio_missing_name(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that creating a portfolio with missing name field fails.
        """

        # Attempt to create a portfolio without a name
        portfolio_data = {}  # Missing name
        response = await client.post(
            "/portfolio/", json=portfolio_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_create_portfolio_with_invalid_payload(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that creating a portfolio with invalid payload fails.
        """
        # Attempt to create a portfolio with an invalid payload
        portfolio_data = {"name": 123}  # Name should be a string
        response = await client.post(
            "/portfolio/", json=portfolio_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_create_portfolio_with_duplicate_name_for_same_user(
        self, client: AsyncClient, created_portfolio: dict, auth_headers: dict
    ):
        """
        Tests that creating a portfolio with a duplicate name for the same user fails.
        """

        # First portfolio
        portfolio_data = {"name": created_portfolio["name"]}

        # Attempt to create a second portfolio with the same name
        create_response = await client.post(
            "/portfolio/", json=portfolio_data, headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_409_CONFLICT
        assert (
            create_response.json()["detail"]
            == "A portfolio with this name already exists"
        )

    @pytest.mark.anyio
    async def test_create_portfolio_with_extra_fields(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that creating a portfolio with extra fields ignores those fields and succeeds.
        """

        # Create a portfolio with extra fields
        portfolio_data = {"name": "My Portfolio", "extra_field": "should be ignored"}
        create_response = await client.post(
            "/portfolio/", json=portfolio_data, headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created_portfolio = create_response.json()
        assert created_portfolio["name"] == "My Portfolio"
        assert "extra_field" not in created_portfolio

    @pytest.mark.anyio
    async def test_create_portfolio_with_name_exceeding_max_length(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Tests that creating a portfolio with a name exceeding the maximum length fails.
        """

        # Attempt to create a portfolio with a name longer than 100 characters
        long_name = "P" * 101
        portfolio_data = {"name": long_name}
        response = await client.post(
            "/portfolio/", json=portfolio_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            "String should have at most 100 characters"
            in response.json()["detail"][0]["msg"]
        )
