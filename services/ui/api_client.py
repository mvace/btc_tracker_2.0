import requests
import streamlit as st
import auth

API_URL = st.secrets["API_URL"]


def get_portfolio_list(token: str):
    try:
        response = requests.get(
            f"{API_URL}/portfolio/",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            return 200, response.json()
        else:
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                data = {"detail": response.text}
            return response.status_code, data

    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Connection to the API failed."}


def get_portfolio_details(token: str, portfolio_id):
    try:
        response = requests.get(
            f"{API_URL}/portfolio/{portfolio_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            return 200, response.json()
        else:
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                data = {"detail": response.text}
            return response.status_code, data

    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Connection to the API failed."}


def create_portfolio(token: str, portfolio_id):
    pass


def update_portfolio(token: str, portfolio_id):
    pass


def delete_portfolio(token: str, portfolio_id):
    pass


def get_transaction_list(token: str):
    pass


def get_transaction_details(token: str, transaction_id: int):
    pass


def post_transaction(token: str, payload: dict):
    try:
        response = requests.post(
            f"{API_URL}/transaction/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            data = {"detail": response.text}

        return response.status_code, data

    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Connection to the API failed."}


def update_transaction(token: str, transaction_id):
    pass


def delete_transaction(token: str, transaction_id):
    pass


def post_login(username: str, password: str):
    pass
