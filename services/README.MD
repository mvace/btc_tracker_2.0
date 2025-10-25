# Bitcoin Portfolio Tracker

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

This service acts as the single source of truth for historical Bitcoin price data. It is a standalone application that fetches data from an external API and provides it to other internal services.

* **Technology:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic
* **Functionality:**
    * A recurring script uses the **CryptoCompare API** to fetch hourly Bitcoin price data.
    * This data is saved into its own dedicated PostgreSQL database.
    * It exposes a simple internal API for other services (like the Portfolio Service) to query prices based on a timestamp.

#### API Endpoints

```http
GET /prices/
# Description: Get all historical prices stored in the database.

GET /prices/{unix_timestamp}
# Description: Get the Bitcoin price for a specific hour, identified by a Unix timestamp.


### 2. Portfolio Service


### 3. UI