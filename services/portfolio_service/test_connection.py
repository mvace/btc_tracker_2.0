import asyncio
import os
import asyncpg


async def main():
    db_url = os.getenv("TEST_DB_URL")
    if not db_url:
        print("❌ ERROR: TEST_DB_URL environment variable not set.")
        return

    print(f"Attempting to connect to the database...")
    try:
        conn = await asyncpg.connect(dsn=db_url)
        print("✅ Connection successful!")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
