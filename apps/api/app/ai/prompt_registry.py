from dataclasses import dataclass


@dataclass(frozen=True)
class PromptSpec:
    version: str
    capability: str
    provider_policy: str
    output_schema: str
    description: str


PROMPT_REGISTRY: dict[str, PromptSpec] = {
    "intake-v0.1.7": PromptSpec(
        version="intake-v0.1.7",
        capability="intake",
        provider_policy="mock_only_until_redaction_hardened",
        output_schema="IntakeDraftOutput",
        description="Extract conservative intake draft fields from a redacted case note. Draft only; human review required.",
    )
}


def get_prompt_spec(version: str) -> PromptSpec:
    try:
        return PROMPT_REGISTRY[version]
    except KeyError as exc:
        raise ValueError("prompt_version_not_registered") from exc
