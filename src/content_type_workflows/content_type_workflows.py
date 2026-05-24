from __future__ import annotations

from dataclasses import asdict, dataclass

from src.human_review import HumanReviewRecord, HumanReviewWorkflow
from src.prompt_engineering import PromptInputBundle, PromptOutputType
from src.workflow import BrandAlignedContentGenerationWorkflow, ContentGenerationRequest, ContentGenerationResult


@dataclass(frozen=True)
class ContentTypeWorkflowMetadata:
    """Lightweight metadata describing a dedicated content workflow."""

    name: str
    output_type: PromptOutputType
    description: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ContentTypeWorkflowResult:
    """Structured output from a dedicated content-type workflow."""

    metadata: ContentTypeWorkflowMetadata
    generation_result: ContentGenerationResult
    review_record: HumanReviewRecord

    def to_dict(self) -> dict:
        return {
            "metadata": self.metadata.to_dict(),
            "generation_result": self.generation_result.to_dict(),
            "review_record": self.review_record.to_dict(),
        }


class _BaseContentTypeWorkflow:
    """Shared implementation for the dedicated content-type workflows."""

    metadata: ContentTypeWorkflowMetadata

    def __init__(
        self,
        *,
        generator: BrandAlignedContentGenerationWorkflow | None = None,
        review_workflow: HumanReviewWorkflow | None = None,
    ) -> None:
        self._generation_workflow = generator or BrandAlignedContentGenerationWorkflow()
        self._review_workflow = review_workflow or HumanReviewWorkflow()

    def run(
        self,
        user_inputs: PromptInputBundle,
        *,
        knowledge_base_root: str = "knowledge_base",
        model: str | None = None,
    ) -> ContentTypeWorkflowResult:
        """Run one content-type-specific generation flow and prepare review."""

        generation_result = self._generation_workflow.run(
            ContentGenerationRequest(
                output_type=self.metadata.output_type,
                user_inputs=user_inputs,
                knowledge_base_root=knowledge_base_root,
                model=model,
            )
        )
        review_record = self._review_workflow.review_generation(generation_result)

        return ContentTypeWorkflowResult(
            metadata=self.metadata,
            generation_result=generation_result,
            review_record=review_record,
        )


class InstagramContentWorkflow(_BaseContentTypeWorkflow):
    metadata = ContentTypeWorkflowMetadata(
        name="instagram_content",
        output_type="instagram_posts",
        description="Dedicated workflow for Instagram content generation.",
    )


class ProductDescriptionsWorkflow(_BaseContentTypeWorkflow):
    metadata = ContentTypeWorkflowMetadata(
        name="product_descriptions",
        output_type="product_descriptions",
        description="Dedicated workflow for product description generation.",
    )


class LaunchCopyWorkflow(_BaseContentTypeWorkflow):
    metadata = ContentTypeWorkflowMetadata(
        name="launch_copy",
        output_type="launch_copy",
        description="Dedicated workflow for launch copy generation.",
    )


class CreativeDesignIdeasWorkflow(_BaseContentTypeWorkflow):
    metadata = ContentTypeWorkflowMetadata(
        name="creative_design_ideas",
        output_type="creative_design_ideas",
        description="Dedicated workflow for creative and design idea generation.",
    )
