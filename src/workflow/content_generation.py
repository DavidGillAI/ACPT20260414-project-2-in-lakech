from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, Protocol

from src.ingestion import KnowledgeBaseSnapshot, load_knowledge_base
from src.knowledge_base import ParsedKnowledgeBase, parse_knowledge_base
from src.llm_integration import LLMGenerationResult, OpenAITextGenerator
from src.prompt_engineering import (
    PromptAssembly,
    PromptInputBundle,
    PromptOutputType,
    assemble_prompt,
)


HumanReviewStatus = Literal["awaiting_review"]


class PromptGenerator(Protocol):
    def generate(self, assembly: PromptAssembly, *, model: str | None = None) -> LLMGenerationResult: ...


@dataclass(frozen=True)
class ContentGenerationRequest:
    """Structured input for one linear generation run."""

    output_type: PromptOutputType
    user_inputs: PromptInputBundle
    knowledge_base_root: str = "knowledge_base"
    model: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ContentGenerationResult:
    """End-to-end workflow result ready for human review."""

    request: ContentGenerationRequest
    knowledge_base: KnowledgeBaseSnapshot
    parsed_knowledge_base: ParsedKnowledgeBase
    prompt_assembly: PromptAssembly
    generation: LLMGenerationResult
    review_status: HumanReviewStatus = "awaiting_review"

    def to_dict(self) -> dict:
        return {
            "request": self.request.to_dict(),
            "knowledge_base": self.knowledge_base.to_dict(),
            "parsed_knowledge_base": self.parsed_knowledge_base.to_dict(),
            "prompt_assembly": self.prompt_assembly.to_dict(),
            "generation": self.generation.to_dict(),
            "review_status": self.review_status,
        }


class BrandAlignedContentGenerationWorkflow:
    """Linear brand-aligned generation pipeline with a human review stop."""

    def __init__(self, *, generator: PromptGenerator | None = None) -> None:
        self._generator = generator or OpenAITextGenerator()

    def run(self, request: ContentGenerationRequest) -> ContentGenerationResult:
        """Execute the workflow once and stop after generation."""

        knowledge_base = load_knowledge_base(request.knowledge_base_root)
        parsed_knowledge_base = parse_knowledge_base(knowledge_base)
        prompt_assembly = assemble_prompt(
            parsed_knowledge_base,
            request.user_inputs,
            request.output_type,
        )
        generation = self._generator.generate(prompt_assembly, model=request.model)

        return ContentGenerationResult(
            request=request,
            knowledge_base=knowledge_base,
            parsed_knowledge_base=parsed_knowledge_base,
            prompt_assembly=prompt_assembly,
            generation=generation,
        )
