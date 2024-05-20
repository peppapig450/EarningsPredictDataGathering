from data_gathering.data import fetch_all_data
import asyncio


async def main():
    await fetch_all_data()


if __name__ == "__main__":
    asyncio.run(main())
