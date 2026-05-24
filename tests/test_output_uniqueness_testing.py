from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.llm_integration import LLMGenerationResult
from src.output_uniqueness_testing import (
    OutputUniquenessTestingWorkflow,
    OutputUniquenessComparisonRequest,
)
from src.prompt_engineering import PromptInputBundle


class _FakeWorkflow:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def run(self, request):  # noqa: ANN001
        self.calls.append(request.knowledge_base_root)
        prompt_text = f"Prompt for {request.knowledge_base_root}"
        root_path = Path(request.knowledge_base_root)
        has_brand_context = (root_path / "primary" / "manifesto.md").exists()
        text = "Brand-aware output" if has_brand_context else "Generic output"

        return type(
            "WorkflowResult",
            (),
            {
                "request": request,
                "knowledge_base": type("KB", (), {"to_dict": lambda self: {}})(),
                "parsed_knowledge_base": type("ParsedKB", (), {"to_dict": lambda self: {}})(),
                "prompt_assembly": type(
                    "PA",
                    (),
                    {
                        "to_dict": lambda self: {"prompt_text": prompt_text},
                        "prompt_text": prompt_text,
                    },
                )(),
                "generation": LLMGenerationResult(
                    model=request.model or "gpt-test",
                    text=text,
                    prompt_text=prompt_text,
                    response_id="resp_test",
                ),
                "to_dict": lambda self: {},
            },
        )()


class OutputUniquenessTestingTests(unittest.TestCase):
    def test_comparison_returns_side_by_side_results_and_criteria(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()
            (primary / "manifesto.md").write_text("Brand manifesto", encoding="utf-8")
            (secondary / "trend.md").write_text("Brand context", encoding="utf-8")

            fake_workflow = _FakeWorkflow()
            comparison_workflow = OutputUniquenessTestingWorkflow(workflow=fake_workflow)
            request = OutputUniquenessComparisonRequest(
                output_type="launch_copy",
                user_inputs=PromptInputBundle(tone="warm"),
                brand_knowledge_base_root=root.as_posix(),
                model="gpt-test",
            )

            result = comparison_workflow.run(request)

            self.assertEqual(result.review_status, "awaiting_human_review")
            self.assertEqual(result.brand_aligned.label, "brand_aligned")
            self.assertEqual(result.generic_non_context.label, "generic_non_context")
            self.assertEqual(result.brand_aligned.generation_result.generation.text, "Brand-aware output")
            self.assertEqual(result.generic_non_context.generation_result.generation.text, "Generic output")
            self.assertGreaterEqual(len(result.criteria), 4)
            self.assertEqual(
                [criterion.name for criterion in result.criteria],
                [
                    "tone_consistency",
                    "terminology_consistency",
                    "emotional_alignment",
                    "uniqueness_distinctiveness",
                ],
            )
            self.assertEqual(len(fake_workflow.calls), 2)


if __name__ == "__main__":
    unittest.main()
