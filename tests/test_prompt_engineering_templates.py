from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.ingestion import load_knowledge_base
from src.knowledge_base import parse_knowledge_base
from src.prompt_engineering import PromptInputBundle, assemble_prompt, get_prompt_template


class PromptEngineeringTemplatesTests(unittest.TestCase):
    def test_supported_output_types_have_templates(self) -> None:
        self.assertEqual(get_prompt_template("instagram_posts").spec.title, "Instagram Posts")
        self.assertEqual(get_prompt_template("launch_copy").spec.title, "Launch Copy")
        self.assertEqual(get_prompt_template("product_descriptions").spec.title, "Product Descriptions")
        self.assertEqual(get_prompt_template("creative_design_ideas").spec.title, "Creative and Design Ideas")

    def test_assemble_prompt_includes_knowledge_base_and_user_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()

            (primary / "manifesto.md").write_text("We create with purpose.", encoding="utf-8")
            (secondary / "trend.md").write_text("Cultural moments matter.", encoding="utf-8")

            parsed = parse_knowledge_base(load_knowledge_base(root))
            inputs = PromptInputBundle(
                tone="warm and confident",
                platform="Instagram",
                cta="Shop now",
                campaign_objective="Launch the new collection",
                target_audience="Design-conscious founders",
                word_count="80",
                example_content="Short brand-led caption",
                detailed_instructions="Keep it grounded and premium.",
            )

            assembly = assemble_prompt(parsed, inputs, "instagram_posts")

            self.assertIn("Instagram Posts", assembly.prompt_text)
            self.assertIn("We create with purpose.", assembly.prompt_text)
            self.assertIn("Cultural moments matter.", assembly.prompt_text)
            self.assertIn("Tone: warm and confident", assembly.prompt_text)
            self.assertIn("Return only the requested content itself.", assembly.prompt_text)
            self.assertIn("Do not add conversational follow-ups", assembly.prompt_text)
            self.assertEqual(assembly.template.spec.output_type, "instagram_posts")

    def test_assemble_prompt_handles_empty_user_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "primary").mkdir()
            (root / "secondary").mkdir()

            parsed = parse_knowledge_base(load_knowledge_base(root))
            assembly = assemble_prompt(parsed, PromptInputBundle(), "product_descriptions")

            self.assertIn("Product Descriptions", assembly.prompt_text)
            self.assertNotIn("User inputs:", assembly.prompt_text)
            self.assertIn("none provided", assembly.prompt_text)


if __name__ == "__main__":
    unittest.main()
