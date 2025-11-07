from upsales.models.activity_list_item import ActivityListItem


def test_activity_list_item_nested_partials():
    item = ActivityListItem(
        id=10,
        date="2025-11-01T12:00:00Z",
        userRemovable=True,
        userEditable=True,
        # Nested entities provided as dicts should become Partial models
        client={"id": 7, "name": "ACME"},
        project={"id": 42, "name": "Migration"},
        opportunity={"id": 1234, "description": "Upsell", "value": 10000, "probability": 60},
        regBy={"id": 2, "name": "Jane", "email": "jane@example.com"},
        templateId={"id": 5, "name": "Welcome"},
    )

    assert item.client is not None and item.client.id == 7
    assert item.project is not None and item.project.id == 42 and item.project.name == "Migration"
    assert item.opportunity is not None and item.opportunity.id == 1234
    assert item.regBy is not None and item.regBy.name == "Jane"
    assert item.templateId is not None and item.templateId.id == 5

