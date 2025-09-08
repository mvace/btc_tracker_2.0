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
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests successful retrieval of portfolios for an authenticated user.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a portfolio for the user
        portfolio_data = {"name": "My Portfolio"}
        create_response = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Now list portfolios
        response = await client.get("/portfolio/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        portfolios = response.json()
        assert isinstance(portfolios, list)
        assert len(portfolios) == 1
        assert portfolios[0]["name"] == "My Portfolio"

    @pytest.mark.anyio
    async def test_list_portfolios_returns_empty_list_for_user_with_no_portfolios(
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests that an authenticated user with no portfolios receives an empty list.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }

        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List portfolios without creating any
        response = await client.get("/portfolio/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        portfolios = response.json()
        assert isinstance(portfolios, list)
        assert len(portfolios) == 0

    @pytest.mark.anyio
    async def test_list_portfolios_does_not_show_other_users_portfolios(
        self,
        client: AsyncClient,
        created_user: dict,
    ):
        """
        Tests that a user cannot see portfolios belonging to another user.
        """

        # Create first user and their portfolio
        login_data1 = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response1 = await client.post("/auth/token", data=login_data1)
        assert login_response1.status_code == status.HTTP_200_OK
        token1 = login_response1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        portfolio_data1 = {"name": "User1 Portfolio"}
        create_response1 = await client.post(
            "/portfolio/", json=portfolio_data1, headers=headers1
        )
        assert create_response1.status_code == status.HTTP_201_CREATED

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
    async def test_get_portfolio_success(self, client: AsyncClient, created_user: dict):
        """
        Tests successful retrieval of a specific portfolio by its ID for an authenticated user.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a portfolio for the user
        portfolio_data = {"name": "My Portfolio"}
        create_response = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created_portfolio = create_response.json()
        portfolio_id = created_portfolio["id"]

        # Now retrieve the specific portfolio by ID
        response = await client.get(f"/portfolio/{portfolio_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        portfolio = response.json()
        assert portfolio["id"] == portfolio_id
        assert portfolio["name"] == "My Portfolio"

    @pytest.mark.anyio
    async def test_get_portfolio_not_found(
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests that retrieving a non-existent portfolio returns a 404 error.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to retrieve a portfolio with an ID that doesn't exist
        non_existent_portfolio_id = 9999
        response = await client.get(
            f"/portfolio/{non_existent_portfolio_id}", headers=headers
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
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests that a user cannot access a portfolio belonging to another user.
        """

        # Create first user and their portfolio
        login_data1 = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response1 = await client.post("/auth/token", data=login_data1)
        assert login_response1.status_code == status.HTTP_200_OK
        token1 = login_response1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        portfolio_data1 = {"name": "User1 Portfolio"}
        create_response1 = await client.post(
            "/portfolio/", json=portfolio_data1, headers=headers1
        )
        assert create_response1.status_code == status.HTTP_201_CREATED
        created_portfolio1 = create_response1.json()
        portfolio_id1 = created_portfolio1["id"]

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
            self, client: AsyncClient, created_user: dict
        ):
            """
            Tests that providing an invalid portfolio ID returns a 422 error.
            """

            login_data = {
                "username": created_user["email"],
                "password": created_user["password"],
            }
            login_response = await client.post("/auth/token", data=login_data)

            assert login_response.status_code == status.HTTP_200_OK
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Attempt to retrieve a portfolio with an invalid ID
            invalid_portfolio_id = "invalid_id"
            response = await client.get(
                f"/portfolio/{invalid_portfolio_id}", headers=headers
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreatePortfolio:
    @pytest.mark.anyio
    async def test_create_portfolio_success(
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests successful creation of a portfolio for an authenticated user.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a portfolio for the user
        portfolio_data = {"name": "My Portfolio"}
        create_response = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
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
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests that creating a portfolio with missing name field fails.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to create a portfolio without a name
        portfolio_data = {}  # Missing name
        response = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_create_portfolio_with_invalid_payload(
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests that creating a portfolio with invalid payload fails.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to create a portfolio with an invalid payload
        portfolio_data = {"name": 123}  # Name should be a string
        response = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.anyio
    async def test_create_portfolio_with_duplicate_name_for_same_user(
        self, client: AsyncClient, created_user: dict
    ):
        """
        Tests that creating a portfolio with a duplicate name for the same user fails.
        """

        login_data = {
            "username": created_user["email"],
            "password": created_user["password"],
        }
        login_response = await client.post("/auth/token", data=login_data)

        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create the first portfolio
        portfolio_data = {"name": "My Portfolio"}
        create_response1 = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
        )
        assert create_response1.status_code == status.HTTP_201_CREATED

        # Attempt to create a second portfolio with the same name
        create_response2 = await client.post(
            "/portfolio/", json=portfolio_data, headers=headers
        )
        assert create_response2.status_code == status.HTTP_409_CONFLICT
        assert (
            create_response2.json()["detail"]
            == "A portfolio with this name already exists"
        )
