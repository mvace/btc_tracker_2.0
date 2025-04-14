import pandas as pd
from sqlalchemy import create_engine

# import sys
# from pathlib import Path

# project_root = Path(__file__).resolve().parent.parent
# sys.path.append(str(project_root))
from core.settings import SYNC_DATABASE_URL, ASYNC_DATABASE_URL

DATABASE_URL = SYNC_DATABASE_URL

# Define connection details (adjust these as needed)
engine = create_engine(DATABASE_URL)

# Read the CSV file from within the container
df = pd.read_csv("crypto_data.csv")

# Insert data into PostgreSQL
df.to_sql("hourly_bitcoin_prices", engine, if_exists="append", index=False)
print("CSV data imported successfully!")
