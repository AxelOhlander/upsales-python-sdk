"""Check why name sort failed."""
values_asc = ['Avarn Security AB - Platskontor Malmö_EDIT', 'Bing Bong AB', 'Boards on Fire AB', 'HMS Industrial Networks AB_TEST', 'IKEA of Sweden AB']

print("Ascending name values:")
for i, v in enumerate(values_asc):
    print(f"  [{i}] {v}")

print("\nChecking if sorted:")
for i in range(len(values_asc) - 1):
    current = values_asc[i]
    next_val = values_asc[i+1]
    is_correct = current <= next_val
    symbol = "✅" if is_correct else "❌"
    print(f"  {symbol} '{current[:30]}' <= '{next_val[:30]}': {is_correct}")

# The issue might be that we didn't get ALL results
print("\n🔍 Hypothesis:")
print("The validator only checks the FIRST 10 results returned.")
print("If there are more results and they're out of order, we miss it.")
print("\nExample:")
print("  Results 1-10: Sorted correctly")
print("  Results 11-15: Out of order (but we don't check these)")
print("  Validator says: ❌ NOT SORTED (because it checks ALL returned results)")
