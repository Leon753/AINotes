import asyncio
from database.session import AsyncSessionLocal
from cleanup import cleanup_old_notes

async def run_cleanup():
    async with AsyncSessionLocal() as db:
        await cleanup_old_notes(db)

if __name__ == "__main__":
    asyncio.run(run_cleanup())
