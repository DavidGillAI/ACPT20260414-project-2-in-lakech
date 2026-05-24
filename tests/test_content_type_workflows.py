from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.content_type_workflows import (
    CreativeDesignIdeasWorkflow,
    InstagramContentWorkflow,
    LaunchCopyWorkflow,
    ProductDescriptionsWorkflow,
)
from src.llm_integration import LLMGenerationResult
from src.prompt_engineering import PromptInputBundle
from src.workflow import BrandAlignedContentGenerationWorkflow


class _FakeGenerator:
    def generate(self, assembly, *, model=None):  # noqa: ANN001
        return LLMGenerationResult(
            model=model or "gpt-test",
            text=f"Generated for {assembly.template.spec.output_type}",
            prompt_text=assembly.prompt_text,
            response_id="resp_test",
        )


class ContentTypeWorkflowTests(unittest.TestCase):
    def test_workflows_expose_distinct_output_types_and_review_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "primary").mkdir()
            (root / "secondary").mkdir()
            (root / "primary" / "manifesto.md").write_text("Brand manifesto", encoding="utf-8")

            generator = BrandAlignedContentGenerationWorkflow(generator=_FakeGenerator())
            user_inputs = PromptInputBundle(tone="warm", platform="Instagram")

            instagram_result = InstagramContentWorkflow(generator=generator).run(
                user_inputs,
                knowledge_base_root=root.as_posix(),
                model="gpt-test",
            )
            product_result = ProductDescriptionsWorkflow(generator=generator).run(
                user_inputs,
                knowledge_base_root=root.as_posix(),
                model="gpt-test",
            )
            launch_result = LaunchCopyWorkflow(generator=generator).run(
                user_inputs,
                knowledge_base_root=root.as_posix(),
                model="gpt-test",
            )
            creative_result = CreativeDesignIdeasWorkflow(generator=generator).run(
                user_inputs,
                knowledge_base_root=root.as_posix(),
                model="gpt-test",
            )

            self.assertEqual(instagram_result.metadata.output_type, "instagram_posts")
            self.assertEqual(product_result.metadata.output_type, "product_descriptions")
            self.assertEqual(launch_result.metadata.output_type, "launch_copy")
            self.assertEqual(creative_result.metadata.output_type, "creative_design_ideas")
            self.assertEqual(instagram_result.review_record.status, "awaiting_review")
            self.assertEqual(instagram_result.review_record.item_type, "generation")
            self.assertIn("instagram_posts", instagram_result.generation_result.generation.text)
            self.assertIn("product_descriptions", product_result.generation_result.generation.text)
            self.assertIn("launch_copy", launch_result.generation_result.generation.text)
            self.assertIn("creative_design_ideas", creative_result.generation_result.generation.text)


if __name__ == "__main__":
    unittest.main()
