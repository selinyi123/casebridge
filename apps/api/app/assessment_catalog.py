SCHEMA_CATALOG = {
    "community-intake-v0.1.10": {
        "schema_id": "community-intake-v0.1.10",
        "domains": [
            "living_situation",
            "meal_nutrition",
            "mobility_home_safety",
            "family_social_support",
            "emotional_sleep",
            "client_wishes",
            "missing_information",
        ],
    }
}


def get_schema(schema_id: str) -> dict:
    if schema_id not in SCHEMA_CATALOG:
        raise ValueError("schema_not_found")
    return SCHEMA_CATALOG[schema_id]
