from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
import os

from src.prompt_engineering import PromptAssembly

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"


class LLMIntegrationError(RuntimeError):
    """Base error for the LLM integration subsystem."""


class LLMConfigurationError(LLMIntegrationError):
    """Raised when the OpenAI client cannot be configured."""


class LLMRequestError(LLMIntegrationError):
    """Raised when the OpenAI request fails or returns unusable output."""


@dataclass(frozen=True)
class LLMGenerationResult:
    """Structured text generation output returned by the integration layer."""

    model: str
    text: str
    prompt_text: str
    response_id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class OpenAITextGenerator:
    """Minimal OpenAI Responses API wrapper for prompt-to-text generation."""

    def __init__(
        self,
        *,
        client: Any | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self._client = client or self._build_client(api_key=api_key)

    def generate(
        self,
        assembly: PromptAssembly,
        *,
        model: str | None = None,
    ) -> LLMGenerationResult:
        """Send assembled prompt text to OpenAI and return the generated text."""

        prompt_text = assembly.prompt_text.strip()
        if not prompt_text:
            raise LLMRequestError("PromptAssembly.prompt_text cannot be empty.")

        resolved_model = model or self._model

        try:
            response = self._client.responses.create(
                model=resolved_model,
                input=prompt_text,
            )
        except Exception as exc:  # pragma: no cover - exercised with real SDK/runtime
            raise LLMRequestError(f"OpenAI request failed: {exc}") from exc

        output_text = getattr(response, "output_text", "")
        if not output_text or not str(output_text).strip():
            raise LLMRequestError("OpenAI response did not contain usable text output.")

        return LLMGenerationResult(
            model=resolved_model,
            text=str(output_text).strip(),
            prompt_text=prompt_text,
            response_id=getattr(response, "id", None),
        )

    def _build_client(self, api_key: str | None) -> Any:
        load_environment_file()

        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is required to create an OpenAI client."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on local installation
            raise LLMConfigurationError(
                "The openai package is required. Add it to requirements.txt and install dependencies."
            ) from exc

        return OpenAI(api_key=resolved_api_key)


def load_environment_file() -> None:
    """Load local .env values when python-dotenv is available."""

    if load_dotenv is not None:
        load_dotenv()
