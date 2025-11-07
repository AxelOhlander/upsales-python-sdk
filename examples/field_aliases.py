"""
Demo: Pydantic Field Aliases for API/UI Name Mismatches

Shows how to map API field names to user-friendly Python property names.

Example: Upsales API returns "client" but we want Python users to use "company".
"""

from pydantic import BaseModel, Field


class PartialCompany(BaseModel):
    """Company model (simplified for demo)."""

    id: int
    name: str


class Contact(BaseModel):
    """
    Contact model showing field alias pattern.

    API sends field named "client", but we expose it as "company" for clarity.
    """

    id: int
    name: str
    email: str

    # API field: "client" → Python property: "company"
    company: PartialCompany = Field(alias="client")


def demo_reading_from_api():
    """Demo: Reading from API (deserialization)."""
    print("=" * 60)
    print("READING FROM API")
    print("=" * 60)

    # API response has "client" field
    api_response = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "client": {  # ← API uses "client"
            "id": 123,
            "name": "ACME Corporation",
        },
    }

    print("\n1. API Response:")
    print("   Field name: 'client'")
    print(f"   Value: {api_response['client']}")

    # Pydantic automatically maps "client" → company
    contact = Contact(**api_response)

    print("\n2. Python Object:")
    print("   Property name: 'company'")
    print("   Access via: contact.company")
    print(f"   Value: {contact.company.name}")

    print("\n✅ User-friendly! Users think in terms of 'company', not 'client'")


def demo_writing_to_api():
    """Demo: Writing to API (serialization)."""
    print("\n" + "=" * 60)
    print("WRITING TO API")
    print("=" * 60)

    # Create contact with company
    contact = Contact(
        id=1,
        name="Jane Doe",
        email="jane@example.com",
        company=PartialCompany(id=456, name="Tech Corp"),
    )

    print("\n1. Python Object:")
    print("   Property: contact.company")
    print(f"   Value: {contact.company.name}")

    # Serialize for API (use by_alias=True)
    api_data = contact.model_dump(by_alias=True)

    print("\n2. Serialized for API:")
    print("   Field name: 'client' (API expects this name)")
    print(f"   Data: {api_data}")

    print("\n✅ Automatically maps back to API field names!")


def demo_without_alias():
    """Demo: Default serialization without by_alias."""
    contact = Contact(
        id=1,
        name="Bob Smith",
        email="bob@example.com",
        company=PartialCompany(id=789, name="Startup Inc"),
    )

    print("\n" + "=" * 60)
    print("SERIALIZATION OPTIONS")
    print("=" * 60)

    # Without by_alias - uses Python property names
    python_data = contact.model_dump(by_alias=False)
    print("\n1. Python Format (by_alias=False):")
    print("   Uses: 'company' field")
    print(f"   Data: {python_data}")

    # With by_alias - uses API field names
    api_data = contact.model_dump(by_alias=True)
    print("\n2. API Format (by_alias=True):")
    print("   Uses: 'client' field")
    print(f"   Data: {api_data}")


def demo_benefits():
    """Show benefits of field aliases."""
    print("\n" + "=" * 60)
    print("BENEFITS")
    print("=" * 60)

    contact = Contact(
        id=1,
        name="Alice Johnson",
        email="alice@example.com",
        company=PartialCompany(id=100, name="Big Corp"),
    )

    print("\n✅ User-Friendly API:")
    print(f"   contact.company.name = '{contact.company.name}'")
    print("   ↑ Clear! Users understand 'company'")

    print("\n❌ If we used API naming directly:")
    print("   contact.client.name = 'Big Corp'")
    print("   ↑ Confusing! 'client' conflicts with UpsalesClient")

    print("\n✅ Automatic Mapping:")
    print("   Python: contact.company")
    print('   API:    {"client": {...}}')
    print("   ↑ Best of both worlds!")


if __name__ == "__main__":
    demo_reading_from_api()
    demo_writing_to_api()
    demo_without_alias()
    demo_benefits()

    print("\n" + "=" * 60)
    print("PATTERN FOR YOUR MODELS")
    print("=" * 60)
    print("""
When API field name differs from desired Python property name:

from pydantic import Field

class MyModel(BaseModel):
    id: int

    # Python property → API field name
    company: PartialCompany = Field(alias="client")
    owner: PartialUser = Field(alias="user")
    category: PartialCategory = Field(alias="cat")

# Reading from API: automatic
model = MyModel(**api_response)
print(model.company.name)  # Works!

# Writing to API: use by_alias=True
data = model.model_dump(by_alias=True)
# Returns: {"client": {...}, "user": {...}, "cat": {...}}
    """)
    print("=" * 60)
