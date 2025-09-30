import requests


def get_portfolio_list(api_url: str, token: str):
    pass


def get_portfolio_details(api_url: str, token: str, portfolio_id):
    try:
        response = requests.get(
            f"{api_url}/portfolio/{portfolio_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            return response.json(), 200
        else:
            return None, response.status_code

    except requests.exceptions.ConnectionError:
        return None, 503


def create_portfolio(api_url: str, token: str, portfolio_id):
    pass


def update_portfolio(api_url: str, token: str, portfolio_id):
    pass


def delete_portfolio(api_url: str, token: str, portfolio_id):
    pass


def get_transaction_list(api_url: str, token: str):
    pass


def get_transaction_details(api_url: str, token: str, transaction_id: int):
    pass


def post_transaction(api_url: str, token: str, payload: dict):
    try:
        response = requests.post(
            f"{api_url}/transaction/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        return response.status_code

    except requests.exceptions.ConnectionError:
        return None, 503


def update_transaction(api_url: str, token: str, transaction_id):
    pass


def delete_transaction(api_url: str, token: str, transaction_id):
    pass


def post_login(api_url: str, username: str, password: str):
    pass
