from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.ingestion import load_knowledge_base
from src.knowledge_base import parse_knowledge_base


class KnowledgeBaseParserTests(unittest.TestCase):
    def test_parser_groups_primary_and_secondary_documents_into_categories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()

            (primary / "manifesto.md").write_text("Brand manifesto", encoding="utf-8")
            (primary / "tone-and-voice.md").write_text("Brand voice", encoding="utf-8")
            (secondary / "competitor-analysis.md").write_text("Competitor notes", encoding="utf-8")

            snapshot = load_knowledge_base(root)
            parsed = parse_knowledge_base(snapshot)

            self.assertEqual([section.category for section in parsed.primary], ["manifesto", "tone_and_voice"])
            self.assertEqual([section.category for section in parsed.secondary], ["competitor_analysis"])
            self.assertEqual(parsed.primary[0].documents[0].content, "Brand manifesto")

    def test_parser_prepares_prompt_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            primary.mkdir()

            (primary / "values-and-beliefs.md").write_text("Core values", encoding="utf-8")

            snapshot = load_knowledge_base(root)
            parsed = parse_knowledge_base(snapshot)
            payload = parsed.to_prompt_payload()

            self.assertEqual(payload["primary"][0]["category"], "core_beliefs_and_values")
            self.assertIn("Core values", payload["primary"][0]["text"])


if __name__ == "__main__":
    unittest.main()
