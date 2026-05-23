"""Markdown ingestion subsystem for the In Lak'ech MVP."""

from .markdown_ingestion import (
    KnowledgeBaseDocument,
    KnowledgeBaseSnapshot,
    discover_markdown_files,
    ensure_knowledge_base_structure,
    load_knowledge_base,
    load_markdown_document,
)

__all__ = [
    "KnowledgeBaseDocument",
    "KnowledgeBaseSnapshot",
    "discover_markdown_files",
    "ensure_knowledge_base_structure",
    "load_knowledge_base",
    "load_markdown_document",
]
