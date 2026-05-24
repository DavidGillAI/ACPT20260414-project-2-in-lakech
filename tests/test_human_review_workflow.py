from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.human_review import HumanReviewDecision, HumanReviewWorkflow
from src.output_uniqueness_testing import (
    OutputUniquenessComparisonRequest,
    OutputUniquenessTestingWorkflow,
)
from src.prompt_engineering import PromptInputBundle
from src.workflow import BrandAlignedContentGenerationWorkflow, ContentGenerationRequest


class _FakeGeneration:
    def __init__(self, text: str) -> None:
        self.text = text

    def to_dict(self) -> dict:
        return {"text": self.text}


class _FakeGenerator:
    def generate(self, assembly, *, model=None):  # noqa: ANN001
        from src.llm_integration import LLMGenerationResult

        return LLMGenerationResult(
            model=model or "gpt-test",
            text="Generated text",
            prompt_text=assembly.prompt_text,
            response_id="resp_test",
        )


class HumanReviewWorkflowTests(unittest.TestCase):
    def test_reviews_generation_result_with_decision_and_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "primary").mkdir()
            (root / "secondary").mkdir()

            generation_workflow = BrandAlignedContentGenerationWorkflow(generator=_FakeGenerator())
            generation_result = generation_workflow.run(
                ContentGenerationRequest(
                    output_type="product_descriptions",
                    user_inputs=PromptInputBundle(tone="warm"),
                    knowledge_base_root=root.as_posix(),
                    model="gpt-test",
                )
            )

            review_workflow = HumanReviewWorkflow()
            review_record = review_workflow.review_generation(
                generation_result,
                decision=HumanReviewDecision(
                    status="needs_revision",
                    reviewer_notes="Good direction, but tighten the intro.",
                    revision_feedback="Shorten the opening and add one product benefit.",
                ),
            )

            self.assertEqual(review_record.status, "needs_revision")
            self.assertEqual(review_record.reviewer_notes, "Good direction, but tighten the intro.")
            self.assertEqual(review_record.revision_feedback, "Shorten the opening and add one product benefit.")
            self.assertEqual(review_record.decision.status, "needs_revision")
            self.assertEqual(review_record.item_type, "generation")

    def test_reviews_comparison_result_and_keeps_human_control(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()
            (primary / "manifesto.md").write_text("Brand manifesto", encoding="utf-8")

            comparison_workflow = OutputUniquenessTestingWorkflow(workflow=BrandAlignedContentGenerationWorkflow(generator=_FakeGenerator()))
            comparison_result = comparison_workflow.run(
                OutputUniquenessComparisonRequest(
                    output_type="launch_copy",
                    user_inputs=PromptInputBundle(tone="confident"),
                    brand_knowledge_base_root=root.as_posix(),
                    model="gpt-test",
                )
            )

            review_workflow = HumanReviewWorkflow()
            review_record = review_workflow.review_comparison(
                comparison_result,
                decision=HumanReviewDecision(
                    status="approved",
                    reviewer_notes="The brand version is clearly more distinctive.",
                ),
            )

            self.assertEqual(review_record.status, "approved")
            self.assertEqual(review_record.item_type, "comparison")
            self.assertIn("brand_aligned", review_record.item.to_dict())
            self.assertIn("generic_non_context", review_record.item.to_dict())
            self.assertEqual(review_record.decision.status, "approved")

    def test_pending_review_defaults_to_awaiting_review(self) -> None:
        workflow = HumanReviewWorkflow()
        review_record = workflow.review_generation(
            type(
                "Result",
                (),
                {"to_dict": lambda self: {"generation": "stub"}},
            )()
        )

        self.assertEqual(review_record.status, "awaiting_review")
        self.assertIsNone(review_record.decision)


if __name__ == "__main__":
    unittest.main()
