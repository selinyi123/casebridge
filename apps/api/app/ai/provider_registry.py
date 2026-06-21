from dataclasses import dataclass

from app.ai.mock_provider import generate_intake_draft
from app.ai.prompt_registry import PromptSpec
from app.schemas import IntakeDraftOutput


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    prompt_version: str
    output: IntakeDraftOutput


def generate_with_provider(provider: str, prompt: PromptSpec, clean_text: str) -> ProviderResult:
    if provider != "mock":
        raise ValueError("provider_not_enabled")
    if prompt.capability != "intake":
        raise ValueError("unsupported_capability")
    return ProviderResult(provider="mock", prompt_version=prompt.version, output=generate_intake_draft(clean_text))
