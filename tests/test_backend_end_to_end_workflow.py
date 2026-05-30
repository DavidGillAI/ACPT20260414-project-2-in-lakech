from __future__ import annotations

import random
import tempfile
import unittest
from pathlib import Path

from src.human_review import HumanReviewWorkflow
from src.llm_integration import LLMGenerationResult
from src.prompt_engineering import PromptInputBundle
from src.workflow import (
    BrandAlignedContentGenerationWorkflow,
    ContentGenerationRequest,
    ContentGenerationResult,
)


SUPPORTED_OUTPUT_TYPES = (
    "instagram_posts",
    "launch_copy",
    "product_descriptions",
    "creative_design_ideas",
)


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


class BackendEndToEndWorkflowTests(unittest.TestCase):
    def test_backend_generation_workflow_runs_100_times_without_real_openai(self) -> None:
        # This is an automated backend end-to-end test, not a Streamlit UI test,
        # not a real OpenAI integration test, and it uses a fake generator to keep
        # the run fast, deterministic, and free.
        rng = random.Random(42)
        review_workflow = HumanReviewWorkflow()

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

            first_generation_result = None

            for index in range(100):
                request = ContentGenerationRequest(
                    output_type=rng.choice(SUPPORTED_OUTPUT_TYPES),
                    user_inputs=self._build_random_inputs(rng),
                    knowledge_base_root=root.as_posix(),
                    model=rng.choice([None, "fake-model-a", "fake-model-b"]),
                )

                result = workflow.run(request)

                self.assertIsInstance(result, ContentGenerationResult)
                self.assertTrue(result.generation.text.strip())
                self.assertEqual(result.generation.model, "fake-test-model")
                self.assertEqual(result.review_status, "awaiting_review")
                self.assertIn("We create with purpose.", result.prompt_assembly.prompt_text)
                self.assertIn("Cultural moments matter.", result.prompt_assembly.prompt_text)
                self.assertEqual(result.generation.prompt_text, result.prompt_assembly.prompt_text)

                for label, value in result.request.user_inputs.to_dict().items():
                    if value and str(value).strip():
                        self.assertIn(str(value).strip(), result.prompt_assembly.prompt_text, msg=label)

                if first_generation_result is None:
                    first_generation_result = result

            self.assertEqual(len(generator.calls), 100)
            self.assertIsNotNone(first_generation_result)

            review_record = review_workflow.review_generation(first_generation_result)
            self.assertEqual(review_record.item_type, "generation")
            self.assertEqual(review_record.status, "awaiting_review")
            self.assertIs(review_record.item, first_generation_result)

    @staticmethod
    def _build_random_inputs(rng: random.Random) -> PromptInputBundle:
        return PromptInputBundle(
            tone=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                ["warm", "confident", "minimal", "editorial", "bold"],
            ),
            platform=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                ["Instagram", "Website", "Email", "Product page"],
            ),
            cta=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                ["Shop now", "Learn more", "Explore the collection", "See details"],
            ),
            campaign_objective=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                [
                    "Launch the spring collection",
                    "Drive awareness for the new brand story",
                    "Support a product reveal",
                    "Introduce a limited release",
                ],
            ),
            target_audience=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                [
                    "Design-conscious founders",
                    "Creative professionals",
                    "Culture-led shoppers",
                    "Minimalist brand fans",
                ],
            ),
            word_count=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                ["50", "80", "120", "150"],
            ),
            example_content=BackendEndToEndWorkflowTests._maybe_value(
                rng,
                [
                    "Short, premium caption with a strong opening line.",
                    "Clean, direct launch copy with a calm tone.",
                    "Concise product language that feels thoughtful.",
                ],
            ),
            detailed_instructions=BackendEndToEndWorkflowTests._maybe_value(
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
