from __future__ import annotations

from dataclasses import asdict, dataclass, field
import tempfile
from typing import Literal, Protocol

from src.prompt_engineering import PromptInputBundle, PromptOutputType
from src.workflow import (
    BrandAlignedContentGenerationWorkflow,
    ContentGenerationRequest,
    ContentGenerationResult,
)


HumanReviewStatus = Literal["awaiting_human_review"]


class GenerationWorkflow(Protocol):
    def run(self, request: ContentGenerationRequest) -> ContentGenerationResult: ...


@dataclass(frozen=True)
class OutputUniquenessComparisonCriterion:
    """A lightweight human-review criterion for comparing two outputs."""

    name: str
    description: str
    brand_notes: str | None = None
    generic_notes: str | None = None
    reviewer_notes: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class OutputUniquenessComparisonRequest:
    """Structured input for one brand-versus-generic comparison run."""

    output_type: PromptOutputType
    user_inputs: PromptInputBundle
    brand_knowledge_base_root: str = "knowledge_base"
    model: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class OutputVariantResult:
    """One side of the comparison table."""

    label: Literal["brand_aligned", "generic_non_context"]
    generation_result: ContentGenerationResult

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "generation_result": self.generation_result.to_dict(),
        }


@dataclass(frozen=True)
class OutputUniquenessComparisonResult:
    """Structured comparison output for human review."""

    request: OutputUniquenessComparisonRequest
    brand_aligned: OutputVariantResult
    generic_non_context: OutputVariantResult
    criteria: list[OutputUniquenessComparisonCriterion] = field(default_factory=list)
    review_status: HumanReviewStatus = "awaiting_human_review"

    def to_dict(self) -> dict:
        return {
            "request": self.request.to_dict(),
            "brand_aligned": self.brand_aligned.to_dict(),
            "generic_non_context": self.generic_non_context.to_dict(),
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "review_status": self.review_status,
        }


DEFAULT_UNIQUENESS_CRITERIA: list[OutputUniquenessComparisonCriterion] = [
    OutputUniquenessComparisonCriterion(
        name="tone_consistency",
        description="Check whether the brand-aligned output keeps the requested tone more consistently than the generic output.",
    ),
    OutputUniquenessComparisonCriterion(
        name="terminology_consistency",
        description="Check whether brand-specific terms and phrasing appear more clearly in the brand-aligned output.",
    ),
    OutputUniquenessComparisonCriterion(
        name="emotional_alignment",
        description="Check whether the brand-aligned output feels more emotionally aligned with the brand knowledge base.",
    ),
    OutputUniquenessComparisonCriterion(
        name="uniqueness_distinctiveness",
        description="Check whether the brand-aligned output is meaningfully distinct from a generic AI-style response.",
    ),
]


class OutputUniquenessTestingWorkflow:
    """Run a brand-versus-generic comparison using the existing workflow."""

    def __init__(
        self,
        *,
        workflow: GenerationWorkflow | None = None,
        criteria: list[OutputUniquenessComparisonCriterion] | None = None,
    ) -> None:
        self._workflow = workflow or BrandAlignedContentGenerationWorkflow()
        self._criteria = criteria or DEFAULT_UNIQUENESS_CRITERIA

    def run(self, request: OutputUniquenessComparisonRequest) -> OutputUniquenessComparisonResult:
        """Generate a brand-aligned and a generic output once each, then stop."""

        brand_result = self._workflow.run(
            ContentGenerationRequest(
                output_type=request.output_type,
                user_inputs=request.user_inputs,
                knowledge_base_root=request.brand_knowledge_base_root,
                model=request.model,
            )
        )

        with tempfile.TemporaryDirectory() as empty_root:
            generic_result = self._workflow.run(
                ContentGenerationRequest(
                    output_type=request.output_type,
                    user_inputs=request.user_inputs,
                    knowledge_base_root=empty_root,
                    model=request.model,
                )
            )

        return OutputUniquenessComparisonResult(
            request=request,
            brand_aligned=OutputVariantResult(
                label="brand_aligned",
                generation_result=brand_result,
            ),
            generic_non_context=OutputVariantResult(
                label="generic_non_context",
                generation_result=generic_result,
            ),
            criteria=list(self._criteria),
        )
