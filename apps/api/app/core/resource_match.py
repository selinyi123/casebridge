def match_resources(need_tag_codes: list[str], resources: list[dict], tag_catalog: dict) -> list[dict]:
    """Deterministic tag-rule resource matching.

    AI may later draft explanations, but candidate selection must remain auditable.
    """
    match_codes: set[str] = set()
    for tag in tag_catalog.get("needs", []):
        if tag.get("code") in need_tag_codes:
            match_codes.update(tag.get("match_codes", []))

    candidates: list[dict] = []
    for resource in resources:
        resource_codes = set(resource.get("match_codes", []))
        overlap = sorted(match_codes.intersection(resource_codes))
        if overlap and resource.get("status") == "active":
            candidates.append(
                {
                    "resource_code": resource.get("code"),
                    "resource_name": resource.get("name"),
                    "category": resource.get("category"),
                    "matched_codes": overlap,
                    "requires_human_verification": True,
                }
            )

    return candidates
