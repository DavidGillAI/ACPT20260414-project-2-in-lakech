from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.llm_integration import LLMGenerationResult
from src.prompt_engineering import PromptInputBundle
from src.workflow import (
    BrandAlignedContentGenerationWorkflow,
    ContentGenerationRequest,
)


class _FakeGenerator:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate(self, assembly, *, model=None):  # noqa: ANN001
        self.calls.append({"assembly": assembly, "model": model})
        return LLMGenerationResult(
            model=model or "gpt-test",
            text="Generated workflow output",
            prompt_text=assembly.prompt_text,
            response_id="resp_workflow",
        )


class WorkflowTests(unittest.TestCase):
    def test_run_executes_linear_pipeline_and_stops_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()

            (primary / "manifesto.md").write_text("Brand manifesto", encoding="utf-8")
            (secondary / "trend.md").write_text("Cultural reference", encoding="utf-8")

            generator = _FakeGenerator()
            workflow = BrandAlignedContentGenerationWorkflow(generator=generator)
            request = ContentGenerationRequest(
                output_type="instagram_posts",
                user_inputs=PromptInputBundle(
                    tone="warm",
                    cta="Shop now",
                ),
                knowledge_base_root=root.as_posix(),
                model="gpt-workflow",
            )

            result = workflow.run(request)

            self.assertEqual(result.review_status, "awaiting_review")
            self.assertEqual(result.generation.text, "Generated workflow output")
            self.assertEqual(generator.calls[0]["model"], "gpt-workflow")
            self.assertIn("Brand manifesto", result.prompt_assembly.prompt_text)
            self.assertIn("Cultural reference", result.prompt_assembly.prompt_text)
            self.assertEqual(result.request.output_type, "instagram_posts")


if __name__ == "__main__":
    unittest.main()
