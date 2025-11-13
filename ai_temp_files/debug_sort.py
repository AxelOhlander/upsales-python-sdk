"""Debug sort validation."""
import asyncio
from upsales import Upsales

async def debug():
    async with Upsales.from_env() as upsales:
        # Get results with sort
        results = await upsales.companies.list(sort="name", limit=10)
        
        print(f"Got {len(results)} results\n")
        print("Full list of names:")
        for i, company in enumerate(results):
            print(f"  [{i}] {company.name}")
        
        # Check order
        print("\nSort check:")
        for i in range(len(results) - 1):
            current = results[i].name
            next_name = results[i+1].name
            is_correct = current <= next_name
            symbol = "✅" if is_correct else "❌"
            print(f"  {symbol} [{i}] '{current[:40]}' <= [{i+1}] '{next_name[:40]}'")

asyncio.run(debug())
