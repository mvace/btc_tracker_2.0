# Bitcoin Portfolio Tracker

You can view the project's UI here: [https://bitfolio.up.railway.app/](https://bitfolio.up.railway.app/)

This project is a comprehensive Bitcoin Portfolio Tracker built using a microservices architecture. It allows users to register, log in, create multiple investment portfolios, and track their Bitcoin transactions. The application automatically calculates key performance metrics for each transaction and portfolio, such as total value, net result, and ROI, by fetching historical and current price data.

The entire application is decoupled into three distinct services, each containerized with Docker and deployed on Railway.

## Project Architecture

The application is divided into three core services that communicate via REST APIs:

1.  **UI Service (Streamlit):** The user-facing frontend. It handles user interactions (login, register, create portfolio) and communicates *only* with the Portfolio Service.
2.  **Portfolio Service (FastAPI):** The central "brain" of the application. It manages all user data, authentication, portfolios, and transactions. It is the only service the UI interacts with.
3.  **Price Service (FastAPI):** A specialized data service. Its sole responsibility is to fetch, store, and provide historical Bitcoin price data. The Portfolio Service queries this service to value transactions.



---

## Services

Here is a detailed breakdown of each microservice.

### 1. Price Service

[https://priceservice.up.railway.app/docs](https://priceservice.up.railway.app/docs)


The Price Service is a specialized microservice built with FastAPI, PostgreSQL, SQLAlchemy, and Pydantic, acting as the single source of truth for historical Bitcoin price data. Its primary function is to fetch hourly price data from the external CryptoCompare API using a script and store this information in its own dedicated PostgreSQL database. It then exposes a simple internal API, allowing other services, such as the Portfolio Service, to query and retrieve prices based on a specific Unix timestamp.

### 2. Portfolio Service


[https://apibitfolio.up.railway.app/docs](https://apibitfolio.up.railway.app/docs)

The Portfolio Service is the central backbone of the application, developed using FastAPI, PostgreSQL, SQLAlchemy, and Pydantic. It manages all core business logic, including user registration and authentication via JWT tokens, as well as all CRUD operations for user portfolios and transactions. When a new transaction is created, this service communicates with the Price Service to fetch the correct historical price, calculates key performance metrics for both the transaction (like ROI and net result) and the parent portfolio (like average price and total value), and persists this data.

### 3. UI

[https://bitfolio.up.railway.app/](https://bitfolio.up.railway.app/)

The UI is a simple, user-facing web interface built with Streamlit. It serves as the single entry point for end-users, handling interactions like registration, login, portfolio creation, and adding new transactions. It communicates exclusively with the Portfolio Service's API to send user data and retrieve information. Its main purpose is to present a clean dashboard where users can view their portfolios and transactions along with all the calculated performance metrics, such as ROI and current value.