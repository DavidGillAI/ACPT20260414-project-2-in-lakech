from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


KnowledgeBaseFolder = Literal["primary", "secondary"]


@dataclass(frozen=True)
class KnowledgeBaseDocument:
    """A single Markdown document loaded from the knowledge base."""

    folder: KnowledgeBaseFolder
    path: str
    name: str
    content: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeBaseSnapshot:
    """Structured in-memory representation of the loaded knowledge base."""

    primary: list[KnowledgeBaseDocument]
    secondary: list[KnowledgeBaseDocument]

    def to_dict(self) -> dict:
        return {
            "primary": [document.to_dict() for document in self.primary],
            "secondary": [document.to_dict() for document in self.secondary],
        }


def ensure_knowledge_base_structure(root: str | Path = "knowledge_base") -> dict[str, Path]:
    """Create the expected knowledge base folder structure if it is missing."""

    root_path = Path(root)
    primary_path = root_path / "primary"
    secondary_path = root_path / "secondary"

    primary_path.mkdir(parents=True, exist_ok=True)
    secondary_path.mkdir(parents=True, exist_ok=True)

    return {
        "root": root_path,
        "primary": primary_path,
        "secondary": secondary_path,
    }


def discover_markdown_files(folder: str | Path) -> list[Path]:
    """Return all Markdown files in a folder, recursively, in stable order."""

    folder_path = Path(folder)
    if not folder_path.exists():
        return []

    markdown_files = [
        path
        for path in folder_path.rglob("*.md")
        if path.is_file()
    ]
    return sorted(
        markdown_files,
        key=lambda path: (
            path.name.lower(),
            path.relative_to(folder_path).as_posix().lower(),
        ),
    )


def load_markdown_document(path: str | Path, folder: KnowledgeBaseFolder) -> KnowledgeBaseDocument:
    """Read a Markdown file into the structured document format."""

    file_path = Path(path)
    content = file_path.read_text(encoding="utf-8-sig")
    return KnowledgeBaseDocument(
        folder=folder,
        path=str(file_path),
        name=file_path.stem,
        content=content,
    )


def load_knowledge_base(root: str | Path = "knowledge_base") -> KnowledgeBaseSnapshot:
    """
    Discover and load all Markdown documents under knowledge_base/primary
    and knowledge_base/secondary into a simple structured Python object.
    """

    paths = ensure_knowledge_base_structure(root)
    primary_documents = [
        load_markdown_document(path, "primary")
        for path in discover_markdown_files(paths["primary"])
    ]
    secondary_documents = [
        load_markdown_document(path, "secondary")
        for path in discover_markdown_files(paths["secondary"])
    ]

    return KnowledgeBaseSnapshot(
        primary=primary_documents,
        secondary=secondary_documents,
    )
