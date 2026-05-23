from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.ingestion import (
    discover_markdown_files,
    ensure_knowledge_base_structure,
    load_knowledge_base,
    load_markdown_document,
)


class MarkdownIngestionTests(unittest.TestCase):
    def test_ensure_structure_creates_primary_and_secondary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = ensure_knowledge_base_structure(temp_dir)

            self.assertTrue(paths["primary"].is_dir())
            self.assertTrue(paths["secondary"].is_dir())

    def test_discover_markdown_files_is_recursive_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "b.md").write_text("# B", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "a.md").write_text("# A", encoding="utf-8")

            discovered = discover_markdown_files(root)

            self.assertEqual(
                [path.name for path in discovered],
                ["a.md", "b.md"],
            )

    def test_load_markdown_document_reads_content_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "brand.md"
            path.write_text("# Brand\nHello world", encoding="utf-8")

            document = load_markdown_document(path, "primary")

            self.assertEqual(document.folder, "primary")
            self.assertEqual(document.name, "brand")
            self.assertEqual(document.content, "# Brand\nHello world")

    def test_load_knowledge_base_separates_primary_and_secondary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            primary = root / "primary"
            secondary = root / "secondary"
            primary.mkdir()
            secondary.mkdir()

            (primary / "manifesto.md").write_text("Primary content", encoding="utf-8")
            (secondary / "trends.md").write_text("Secondary content", encoding="utf-8")

            snapshot = load_knowledge_base(root)

            self.assertEqual(len(snapshot.primary), 1)
            self.assertEqual(len(snapshot.secondary), 1)
            self.assertEqual(snapshot.primary[0].folder, "primary")
            self.assertEqual(snapshot.secondary[0].folder, "secondary")
            self.assertEqual(snapshot.to_dict()["primary"][0]["content"], "Primary content")


if __name__ == "__main__":
    unittest.main()
