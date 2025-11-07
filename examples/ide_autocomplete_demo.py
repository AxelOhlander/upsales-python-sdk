"""
Demo: IDE Autocomplete with TypedDict

Shows the difference between kwargs: Any and TypedDict + Unpack
for IDE discoverability.

Run this file in your IDE to see autocomplete in action!
"""

from typing import Any, TypedDict, Unpack

from pydantic import BaseModel, Field


# ❌ WITHOUT TypedDict - No IDE autocomplete
class UserBad(BaseModel):
    """User without TypedDict - poor IDE experience."""

    id: int = Field(frozen=True)
    name: str
    email: str
    administrator: int

    async def edit(self, **kwargs: Any) -> "UserBad":
        """
        Edit user.

        ❌ Problem: When you type `user.edit(` your IDE shows nothing!
        You have to read docs or model definition to know what fields exist.
        """
        # Pretend update logic
        return self


# ✅ WITH TypedDict - Full IDE autocomplete!
class UserUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a User.

    Your IDE will show these when typing user.edit(
    """

    name: str
    email: str
    administrator: int
    active: int


class UserGood(BaseModel):
    """User with TypedDict - excellent IDE experience."""

    id: int = Field(frozen=True)
    name: str
    email: str
    administrator: int
    active: int = 1

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "UserGood":
        """
        Edit user.

        ✅ Benefit: When you type `user.edit(` your IDE suggests:
            - name: str
            - email: str
            - administrator: int
            - active: int

        Plus type checking ensures you pass correct types!
        """
        # Pretend update logic
        return self


async def demo():
    """Demo showing IDE experience difference."""

    # Create users
    bad_user = UserBad(id=1, name="John", email="john@example.com", administrator=0)
    good_user = UserGood(id=1, name="John", email="john@example.com", administrator=0)

    # ❌ BAD: No autocomplete
    # Try typing: await bad_user.edit(
    # Your IDE shows: **kwargs: Any
    # You have to guess or read docs!
    await bad_user.edit(
        name="Jane",  # IDE doesn't help you here
        email="jane@example.com",  # No type checking
        # What other fields exist? Who knows! 🤷
    )

    # ✅ GOOD: Full autocomplete!
    # Try typing: await good_user.edit(
    # Your IDE shows all available fields:
    #   - name: str
    #   - email: str
    #   - administrator: int
    #   - active: int
    await good_user.edit(
        name="Jane",  # ✅ IDE suggests this
        email="jane@example.com",  # ✅ Type checked
        administrator=1,  # ✅ IDE knows this is int
        active=1,  # ✅ IDE shows all options
    )

    # ✅ Type checking catches errors!
    # This will fail type checking (administrator should be int):
    # await good_user.edit(administrator="admin")  # ❌ Type error!

    # ✅ IDE autocomplete shows you all available fields
    # No need to read docs or model definition!

    print("✅ TypedDict provides excellent IDE experience!")
    print("✅ Full autocomplete and type checking!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo())
