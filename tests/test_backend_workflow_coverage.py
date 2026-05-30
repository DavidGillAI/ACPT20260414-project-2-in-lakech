from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

from src.llm_integration import LLMGenerationResult
from src.prompt_engineering import PromptInputBundle
from src.workflow import BrandAlignedContentGenerationWorkflow, ContentGenerationRequest


SUPPORTED_OUTPUT_TYPES = (
    "instagram_posts",
    "launch_copy",
    "product_descriptions",
    "creative_design_ideas",
)

TOTAL_RUNS = 100
REPORT_PATH = Path(__file__).resolve().parent / "output" / "backend_workflow_coverage_report.json"


class _FakeGenerator:
    def __init__(self) -> None:
        self.calls: list[dict[str, object | None]] = []

    def generate(self, assembly, *, model=None):  # noqa: ANN001
        self.calls.append({"assembly": assembly, "model": model})
        if not assembly.prompt_text.strip():
            raise AssertionError("Fake generator received an empty prompt.")

        return LLMGenerationResult(
            model="fake-test-model",
            text="fake generated output",
            prompt_text=assembly.prompt_text,
            response_id="fake-response-id",
        )


class BackendWorkflowCoverageTests(unittest.TestCase):
    def test_backend_workflow_covers_all_output_types_and_writes_report(self) -> None:
        # This is an automated backend coverage test, not a Streamlit UI test,
        # not a real OpenAI integration test, and it uses a fake generator to
        # keep the run fast, deterministic, and free.
        rng = random.Random(42)
        output_type_counts = {output_type: 0 for output_type in SUPPORTED_OUTPUT_TYPES}
        passed = 0
        failed = 0

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()

            (primary / "manifesto.md").write_text(
                "We create with purpose.\nBrand identity should remain grounded.",
                encoding="utf-8",
            )
            (secondary / "trend.md").write_text(
                "Cultural moments matter.\nMinimalism can still feel expressive.",
                encoding="utf-8",
            )

            generator = _FakeGenerator()
            workflow = BrandAlignedContentGenerationWorkflow(generator=generator)

            for _ in range(TOTAL_RUNS):
                output_type = rng.choice(SUPPORTED_OUTPUT_TYPES)
                output_type_counts[output_type] += 1

                request = ContentGenerationRequest(
                    output_type=output_type,
                    user_inputs=self._build_random_inputs(rng),
                    knowledge_base_root=root.as_posix(),
                    model=rng.choice([None, "fake-model-a", "fake-model-b"]),
                )

                try:
                    result = workflow.run(request)
                    self.assertTrue(result.generation.text.strip())
                    self.assertEqual(result.generation.model, "fake-test-model")
                    self.assertEqual(result.review_status, "awaiting_review")
                    self.assertIn("We create with purpose.", result.prompt_assembly.prompt_text)
                    self.assertIn("Cultural moments matter.", result.prompt_assembly.prompt_text)
                    self.assertEqual(result.generation.prompt_text, result.prompt_assembly.prompt_text)

                    for label, value in result.request.user_inputs.to_dict().items():
                        if value and str(value).strip():
                            self.assertIn(str(value).strip(), result.prompt_assembly.prompt_text, msg=label)

                    passed += 1
                except Exception:
                    failed += 1

            report = {
                "total_runs": TOTAL_RUNS,
                "passed": passed,
                "failed": failed,
                "output_type_counts": output_type_counts,
            }

            REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

            print("## Backend Workflow Coverage Report")
            print(f"Total Runs: {TOTAL_RUNS}")
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            for output_type in SUPPORTED_OUTPUT_TYPES:
                print(f"{output_type}: {output_type_counts[output_type]}")

            self.assertEqual(len(generator.calls), TOTAL_RUNS)
            self.assertTrue(all(count > 0 for count in output_type_counts.values()))

        self.assertEqual(failed, 0)
        self.assertTrue(all(count > 0 for count in output_type_counts.values()))

    @staticmethod
    def _build_random_inputs(rng: random.Random) -> PromptInputBundle:
        return PromptInputBundle(
            tone=BackendWorkflowCoverageTests._maybe_value(
                rng,
                ["warm", "confident", "minimal", "editorial", "bold"],
            ),
            platform=BackendWorkflowCoverageTests._maybe_value(
                rng,
                ["Instagram", "Website", "Email", "Product page"],
            ),
            cta=BackendWorkflowCoverageTests._maybe_value(
                rng,
                ["Shop now", "Learn more", "Explore the collection", "See details"],
            ),
            campaign_objective=BackendWorkflowCoverageTests._maybe_value(
                rng,
                [
                    "Launch the spring collection",
                    "Drive awareness for the new brand story",
                    "Support a product reveal",
                    "Introduce a limited release",
                ],
            ),
            target_audience=BackendWorkflowCoverageTests._maybe_value(
                rng,
                [
                    "Design-conscious founders",
                    "Creative professionals",
                    "Culture-led shoppers",
                    "Minimalist brand fans",
                ],
            ),
            word_count=BackendWorkflowCoverageTests._maybe_value(
                rng,
                ["50", "80", "120", "150"],
            ),
            example_content=BackendWorkflowCoverageTests._maybe_value(
                rng,
                [
                    "Short, premium caption with a strong opening line.",
                    "Clean, direct launch copy with a calm tone.",
                    "Concise product language that feels thoughtful.",
                ],
            ),
            detailed_instructions=BackendWorkflowCoverageTests._maybe_value(
                rng,
                [
                    "Avoid conversational closings and keep the output self-contained.",
                    "Keep the language restrained and brand-aligned.",
                    "Focus on clarity, symbolism, and practical usefulness.",
                ],
            ),
        )

    @staticmethod
    def _maybe_value(rng: random.Random, options: list[str]) -> str | None:
        choice = rng.choice([None, "", rng.choice(options)])
        return choice if choice and str(choice).strip() else None


if __name__ == "__main__":
    unittest.main()
