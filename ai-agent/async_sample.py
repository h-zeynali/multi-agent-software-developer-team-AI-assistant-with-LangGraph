import asyncio

async def fetch_data(delay, data):
    await asyncio.sleep(delay)
    print(f"Fetched data: {data}")
    return data

async def main():
    # Create tasks to run coroutines concurrently
    task1 = asyncio.create_task(fetch_data(2, "Task 1 data"))
    task2 = asyncio.create_task(fetch_data(1, "Task 2 data"))

    # Wait for the tasks to complete
    results = await asyncio.gather(task1, task2)
    print("All tasks completed.")
    print("Results:", results)

# Entry point for the async program
if __name__ == "__main__":
    asyncio.run(main())