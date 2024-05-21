import cProfile
import asyncio
from data_gathering.data import fetch_all_data


async def main():
    await fetch_all_data()


if __name__ == "__main__":
    # Create a cProfile object
    profiler = cProfile.Profile()
    # Enable profiling
    profiler.enable()

    # Run the main coroutine
    asyncio.run(main())

    # Disable profiling
    profiler.disable()

    # Save profiling results to a file
    profiler.dump_stats("profile_results.prof")
