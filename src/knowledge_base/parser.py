from __future__ import annotations

from dataclasses import asdict, dataclass, field
from collections import OrderedDict
from typing import Iterable

from src.ingestion import KnowledgeBaseDocument, KnowledgeBaseSnapshot


@dataclass(frozen=True)
class ParsedKnowledgeDocument:
    """A knowledge document assigned to a category for prompt preparation."""

    folder: str
    category: str
    path: str
    name: str
    content: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ParsedKnowledgeSection:
    """A category containing one or more parsed knowledge documents."""

    folder: str
    category: str
    documents: list[ParsedKnowledgeDocument] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "folder": self.folder,
            "category": self.category,
            "documents": [document.to_dict() for document in self.documents],
        }

    def to_prompt_text(self) -> str:
        lines = [f"{self.category.replace('_', ' ').title()}:"]
        for document in self.documents:
            lines.append(f"- {document.name}")
            lines.append(document.content.strip())
        return "\n".join(lines).strip()


@dataclass(frozen=True)
class ParsedKnowledgeBase:
    """Structured knowledge grouped by folder and category."""

    primary: list[ParsedKnowledgeSection]
    secondary: list[ParsedKnowledgeSection]

    def to_dict(self) -> dict:
        return {
            "primary": [section.to_dict() for section in self.primary],
            "secondary": [section.to_dict() for section in self.secondary],
        }

    def to_prompt_payload(self) -> dict:
        return {
            "primary": [
                {
                    "category": section.category,
                    "text": section.to_prompt_text(),
                }
                for section in self.primary
            ],
            "secondary": [
                {
                    "category": section.category,
                    "text": section.to_prompt_text(),
                }
                for section in self.secondary
            ],
        }


PRIMARY_CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("manifesto", ("manifesto",)),
    ("philosophy", ("philosophy",)),
    ("core_beliefs_and_values", ("belief", "value", "values")),
    ("tone_and_voice", ("tone", "voice")),
    ("symbolism", ("symbol",)),
    ("audience_profile", ("audience profile", "audience")),
    ("existing_content", ("existing content", "past successful", "copy", "content")),
    ("terminology_and_messaging", ("terminology", "messaging")),
]

SECONDARY_CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("industry_trends", ("industry trend", "trend")),
    ("competitor_analysis", ("competitor",)),
    ("market_positioning", ("market positioning", "positioning")),
    ("consumer_sentiment", ("consumer sentiment", "sentiment")),
    ("cultural_references", ("cultural reference", "cultural")),
    ("emotionally_resonant_branding_examples", ("emotionally resonant", "branding example", "example")),
    ("audience_and_market_insights", ("insight", "market insight")),
]

DEFAULT_CATEGORY = "uncategorised"


def parse_knowledge_base(snapshot: KnowledgeBaseSnapshot) -> ParsedKnowledgeBase:
    """Group ingested Markdown documents into structured categories."""

    primary_sections = _group_documents(snapshot.primary, "primary", PRIMARY_CATEGORY_RULES)
    secondary_sections = _group_documents(snapshot.secondary, "secondary", SECONDARY_CATEGORY_RULES)

    return ParsedKnowledgeBase(
        primary=primary_sections,
        secondary=secondary_sections,
    )


def _group_documents(
    documents: Iterable[KnowledgeBaseDocument],
    folder: str,
    rules: list[tuple[str, tuple[str, ...]]],
) -> list[ParsedKnowledgeSection]:
    grouped: "OrderedDict[str, list[ParsedKnowledgeDocument]]" = OrderedDict()

    for document in documents:
        category = _categorize_document(document, rules)
        parsed_document = ParsedKnowledgeDocument(
            folder=folder,
            category=category,
            path=document.path,
            name=document.name,
            content=document.content,
        )
        grouped.setdefault(category, []).append(parsed_document)

    return [
        ParsedKnowledgeSection(folder=folder, category=category, documents=items)
        for category, items in grouped.items()
    ]


def _categorize_document(
    document: KnowledgeBaseDocument,
    rules: list[tuple[str, tuple[str, ...]]],
) -> str:
    name = document.name.lower().replace("-", " ").replace("_", " ")

    for category, keywords in rules:
        for keyword in keywords:
            if keyword in name:
                return category

    return DEFAULT_CATEGORY
