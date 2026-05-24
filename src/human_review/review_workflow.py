from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, Protocol, Any

from src.llm_integration import LLMGenerationResult
from src.output_uniqueness_testing import OutputUniquenessComparisonResult
from src.workflow import ContentGenerationResult


HumanReviewStatus = Literal["awaiting_review", "approved", "rejected", "needs_revision"]
HumanReviewItemType = Literal["generation", "comparison"]
HumanReviewDecisionStatus = Literal["approved", "rejected", "needs_revision"]


class ReviewableItem(Protocol):
    def to_dict(self) -> dict: ...


@dataclass(frozen=True)
class HumanReviewDecision:
    """A structured decision made by a human reviewer."""

    status: HumanReviewDecisionStatus
    reviewer_notes: str | None = None
    revision_feedback: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class HumanReviewRecord:
    """A reviewable record for one generated output or comparison result."""

    item_type: HumanReviewItemType
    item: ReviewableItem
    status: HumanReviewStatus = "awaiting_review"
    reviewer_notes: str | None = None
    revision_feedback: str | None = None
    decision: HumanReviewDecision | None = None

    def to_dict(self) -> dict:
        return {
            "item_type": self.item_type,
            "item": self.item.to_dict(),
            "status": self.status,
            "reviewer_notes": self.reviewer_notes,
            "revision_feedback": self.revision_feedback,
            "decision": self.decision.to_dict() if self.decision else None,
        }


class HumanReviewWorkflow:
    """Lightweight human review state management for generated content."""

    def review_generation(
        self,
        generation_result: ContentGenerationResult,
        *,
        decision: HumanReviewDecision | None = None,
    ) -> HumanReviewRecord:
        """Wrap a generated output in review state and optionally apply a decision."""

        return self._build_record(
            item_type="generation",
            item=generation_result,
            decision=decision,
        )

    def review_comparison(
        self,
        comparison_result: OutputUniquenessComparisonResult,
        *,
        decision: HumanReviewDecision | None = None,
    ) -> HumanReviewRecord:
        """Wrap a comparison result in review state and optionally apply a decision."""

        return self._build_record(
            item_type="comparison",
            item=comparison_result,
            decision=decision,
        )

    def apply_decision(
        self,
        record: HumanReviewRecord,
        decision: HumanReviewDecision,
    ) -> HumanReviewRecord:
        """Attach a human decision without triggering any regeneration."""

        return HumanReviewRecord(
            item_type=record.item_type,
            item=record.item,
            status=self._normalize_decision_status(decision.status),
            reviewer_notes=decision.reviewer_notes,
            revision_feedback=decision.revision_feedback,
            decision=decision,
        )

    def _build_record(
        self,
        *,
        item_type: HumanReviewItemType,
        item: ReviewableItem,
        decision: HumanReviewDecision | None,
    ) -> HumanReviewRecord:
        record = HumanReviewRecord(
            item_type=item_type,
            item=item,
            status="awaiting_review",
        )

        if decision is None:
            return record

        return self.apply_decision(record, decision)

    @staticmethod
    def _normalize_decision_status(status: HumanReviewDecisionStatus) -> HumanReviewStatus:
        return status
