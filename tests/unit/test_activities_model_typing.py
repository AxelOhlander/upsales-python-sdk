from upsales.models.activities import Activity


def test_activity_nested_dot_access_for_partial_models():
    activity = Activity(
        id=1,
        regDate="2025-11-01T00:00:00Z",
        modDate="2025-11-01T00:00:00Z",
        description="Follow-up call",
        date="2025-11-01T09:00:00Z",
        # Required nested user (PartialUser)
        regBy={
            "id": 2,
            "name": "Agent Smith",
            "email": "smith@example.com",
        },
        # Linked entities as dicts should parse into Partial models
        opportunity={"id": 123, "description": "Big Deal", "value": 50000, "probability": 50},
        project={"id": 99, "name": "Onboarding"},
        # Optional fields
        client={"id": 3, "name": "ACME"},
    )

    assert activity.opportunity is not None
    assert activity.opportunity.id == 123
    # PartialOrder exposes common fields when present
    assert activity.opportunity.description == "Big Deal"

    assert activity.project is not None
    assert activity.project.id == 99
    assert activity.project.name == "Onboarding"

    # PartialUser for regBy
    assert activity.regBy.id == 2
    assert activity.regBy.name == "Agent Smith"
