"""Debug turnover sort."""
import asyncio
from upsales import Upsales

async def debug():
    async with Upsales.from_env() as upsales:
        # Get results with ascending turnover sort
        results = await upsales.companies.list(sort="turnover", limit=10)
        
        print(f"Got {len(results)} results\n")
        print("Full list of turnover values:")
        for i, company in enumerate(results):
            print(f"  [{i}] {company.name[:40]:<40} turnover: {company.turnover}")
        
        # Check order
        print("\nSort check (ascending - smallest to largest):")
        for i in range(len(results) - 1):
            current = results[i].turnover
            next_val = results[i+1].turnover
            
            # Handle None
            if current is None:
                symbol = "✅" if next_val is None or next_val is not None else "?"
                print(f"  {symbol} [{i}] None <= [{i+1}] {next_val}")
            elif next_val is None:
                symbol = "❌"  # None should come first, not after a value
                print(f"  {symbol} [{i}] {current} <= [{i+1}] None (WRONG: None should be first)")
            else:
                is_correct = current <= next_val
                symbol = "✅" if is_correct else "❌"
                print(f"  {symbol} [{i}] {current:>15,} <= [{i+1}] {next_val:>15,}: {is_correct}")

asyncio.run(debug())
