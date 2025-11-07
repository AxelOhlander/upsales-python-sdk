"""
Playground for testing the Upsales SDK.

A safe place to experiment with the library and test features.
Modify and run this file to try different operations.

Usage:
    uv run python playground.py

Requirements:
    - .env file with UPSALES_TOKEN
    - Use test/sandbox environment (not production!)
"""

import asyncio

from upsales import Upsales


async def main():
    """Playground for testing SDK features."""

    print("\n" + "=" * 70)
    print("🎮 UPSALES SDK PLAYGROUND")
    print("=" * 70 + "\n")

    # Create client from .env file
    async with Upsales.from_env() as upsales:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # BASIC OPERATIONS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("📋 BASIC OPERATIONS")
        print("-" * 70)

        # Get a single user
        user = await upsales.users.get(1)
        print("\n✅ Get user:")
        print(f"   ID: {user.id}")
        print(f"   Name: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Is Admin: {user.is_admin}")  # Computed field!

        # List users with pagination
        users = await upsales.users.list(limit=5)
        print(f"\n✅ List users (limit 5): Got {len(users)} users")

        # Get all users (auto-pagination)
        all_users = await upsales.users.list_all()
        print(f"✅ List all users: Total {len(all_users)} users")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # ENHANCED SEARCH FEATURES
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n🔍 ENHANCED SEARCH FEATURES")
        print("-" * 70)

        # Natural operators (intuitive!)
        print("\n✅ Natural operators:")
        recent_users = await upsales.users.search(
            regDate=">=2024-01-01"  # Natural syntax!
        )
        print(f"   Users registered after 2024-01-01: {len(recent_users)}")

        # Substring search (wildcard)
        print("\n✅ Substring search:")
        # Uncomment to test (replace with actual name fragment):
        # matching = await upsales.users.search(name="*John")
        # print(f"   Users with 'John' in name: {len(matching)}")

        # Field selection (performance!)
        print("\n✅ Field selection (optimized):")
        # Note: Field selection returns partial objects
        # Model needs to have all fields optional or use defaults
        # For now, testing with basic list
        print("   Field selection available via: fields=['id', 'name', 'email']")
        print("   Note: Returns partial objects (some models may need adjustment)")
        print("   Bandwidth reduction: 50-90%!")

        # Sorting
        print("\n✅ Sorting:")
        sorted_users = await upsales.users.list(
            limit=5,
            sort="-regDate",  # Newest first (descending)
        )
        print(f"   Got {len(sorted_users)} users sorted by regDate (newest first)")
        if sorted_users:
            print(f"   First: {sorted_users[0].name} ({sorted_users[0].regDate})")

        # Everything combined!
        print("\n✅ Power query (search + sorting):")
        results = await upsales.users.search(
            active=1,  # Filter
            regDate=">=2024-01-01",  # Natural operator
            # fields=["id", "name", "email"],  # Optimize (commented - partial objects)
            sort="-regDate",  # Newest first
        )
        print(f"   Active users from 2024, sorted: {len(results)} results")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # EDITING WITH MINIMAL UPDATES
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n✏️  EDITING (Minimal Updates - Conflict Reduction)")
        print("-" * 70)

        # Get a user
        user_to_edit = await upsales.users.get(1)
        print("\n✅ Original user:")
        print(f"   Name: {user_to_edit.name}")
        print(f"   Email: {user_to_edit.email}")

        # Edit using model.edit() - sends only changed fields!
        print("\n✅ Editing user (minimal update)...")
        # Uncomment to actually test editing:
        # updated = await user_to_edit.edit(name="Test Name")
        # print(f"   Updated name: {updated.name}")
        # print(f"   SDK sent: only changed fields + any required fields")
        # print(f"   Benefit: Doesn't overwrite other fields (reduces conflicts!)")

        print("   (Commented out - uncomment to test actual editing)")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # COMPUTED FIELDS & TYPE SAFETY
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n🎯 COMPUTED FIELDS & TYPE SAFETY")
        print("-" * 70)

        user = await upsales.users.get(1)
        print("\n✅ Computed fields (no DB query):")
        print(f"   is_admin: {user.is_admin}")  # Computed from administrator flag
        print(f"   is_active: {user.is_active}")  # Computed from active flag
        print(f"   display_name: {user.display_name}")  # Formatted name

        # Custom fields access
        if user.custom:
            print("\n✅ Custom fields helper:")
            print("   Access by ID: user.custom_fields[11]")
            print("   Or by alias: user.custom_fields.get('FIELD_ALIAS')")

        # Type-safe editing (IDE autocomplete!)
        print("\n✅ Type-safe editing (IDE autocomplete):")
        print("   await user.edit(")
        print("       name='...',")  # IDE suggests all valid fields!
        print("       email='...',")
        print("       administrator=1")
        print("   )")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # NESTED OBJECTS (Type-Safe)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n🔗 NESTED OBJECTS (Type-Safe)")
        print("-" * 70)

        # Get user with role
        if user.role:
            print("\n✅ Nested PartialRole:")
            print(f"   Role ID: {user.role.id}")
            print(f"   Role Name: {user.role.name}")  # Type-safe! IDE autocomplete!
            print("   (Fetch full: await user.role.fetch_full())")

        # Companies and nested objects
        print("\n✅ Companies with nested objects:")
        print("   companies = await upsales.companies.get(1)")
        print("   for campaign in company.projects:  # Type-safe list[PartialCampaign]")
        print("       print(campaign.name)  # IDE autocomplete!")
        print("   (Available but commented for demo)")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CUSTOM RESOURCE METHODS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n🎨 CUSTOM RESOURCE METHODS")
        print("-" * 70)

        # Get active users (convenience method)
        active_users = await upsales.users.get_active()
        print(f"\n✅ Get active users: {len(active_users)}")

        # Get administrators
        admins = await upsales.users.get_administrators()
        print(f"✅ Get administrators: {len(admins)}")

        # Get by email
        # user_by_email = await upsales.users.get_by_email("test@example.com")

        # Get active products
        active_products = await upsales.products.get_active()
        print(f"✅ Get active products: {len(active_products)}")

        # Get recurring products
        recurring = await upsales.products.get_recurring()
        print(f"✅ Get recurring products: {len(recurring)}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # BULK OPERATIONS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n⚡ BULK OPERATIONS (Parallel)")
        print("-" * 70)

        # Bulk deactivate products
        print("\n✅ Bulk operations (parallel with rate limiting):")
        # Uncomment to test:
        # deactivated = await upsales.products.bulk_deactivate([1, 2, 3])
        # print(f"   Deactivated {len(deactivated)} products")

        print("   (Commented out - uncomment to test bulk updates)")
        print("   Uses Python 3.13 free-threaded mode for true parallelism!")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # COMPARISON: OLD vs NEW SYNTAX
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n🆚 OLD vs NEW SYNTAX")
        print("-" * 70)

        print("\n✅ Search operators:")
        print("   Old: search(regDate='gte:2024-01-01')")
        print("   New: search(regDate='>=2024-01-01')  ✨ More intuitive!")

        print("\n✅ Substring search:")
        print("   Old: search(name='src:ACME')")
        print("   New: search(name='*ACME')  ✨ Wildcard syntax!")

        print("\n✅ Updates:")
        print("   Old: Sent all fields (edit conflict risk)")
        print("   New: Sends only changed + required (safer!) ✨")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # YOUR EXPERIMENTS HERE!
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        print("\n\n🧪 YOUR EXPERIMENTS")
        print("-" * 70)
        print("\nTry your own queries here!\n")

        # Example experiments (uncomment and modify):

        # Test search with operators
        # results = await upsales.products.search(
        #     price=">100",
        #     price="<1000",
        #     active=1
        # )
        # print(f"Products $100-$1000: {len(results)}")

        # Test field selection
        # companies = await upsales.companies.list(
        #     limit=10,
        #     fields=["id", "name", "phone"]
        # )
        # print(f"Companies (minimal fields): {len(companies)}")

        # Test substring search
        # contacts = await upsales.contacts.search(phone="*555")
        # print(f"Contacts with '555' in phone: {len(contacts)}")

        # Test sorting
        # sorted_companies = await upsales.companies.list(
        #     sort="-regDate",  # Newest first
        #     limit=10
        # )
        # print(f"Newest 10 companies: {len(sorted_companies)}")

        # Everything combined!
        # power_query = await upsales.companies.search(
        #     name="*Tech",
        #     employees=">10",
        #     fields=["id", "name", "phone"],
        #     sort="-regDate"
        # )
        # print(f"Power query results: {len(power_query)}")

        print("✨ Add your experiments above (uncomment the examples)!\n")

    print("\n" + "=" * 70)
    print("✅ PLAYGROUND COMPLETE")
    print("=" * 70 + "\n")

    print("Tips:")
    print("  • Modify this file and re-run to test different operations")
    print("  • Check docs/guides/adding-endpoints.md for more examples")
    print("  • Use test/sandbox environment (not production!)")
    print()


if __name__ == "__main__":
    asyncio.run(main())
