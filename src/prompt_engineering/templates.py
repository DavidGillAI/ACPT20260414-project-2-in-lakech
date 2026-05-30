from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from src.knowledge_base import ParsedKnowledgeBase


PromptOutputType = Literal[
    "instagram_posts",
    "launch_copy",
    "product_descriptions",
    "creative_design_ideas",
]


NO_CONVERSATIONAL_FOLLOWUP_INSTRUCTION = (
    "Return only the requested content itself.",
    "Do not add conversational follow-ups, offers of further help, questions, or closing remarks.",
)


@dataclass(frozen=True)
class PromptInputBundle:
    """Structured user inputs that shape prompt assembly."""

    tone: str | None = None
    platform: str | None = None
    cta: str | None = None
    campaign_objective: str | None = None
    target_audience: str | None = None
    word_count: str | None = None
    example_content: str | None = None
    detailed_instructions: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_prompt_lines(self) -> list[str]:
        lines: list[str] = []
        items = [
            ("Tone", self.tone),
            ("Platform", self.platform),
            ("CTA", self.cta),
            ("Campaign objective", self.campaign_objective),
            ("Target audience", self.target_audience),
            ("Word count", self.word_count),
            ("Example content", self.example_content),
            ("Detailed instructions", self.detailed_instructions),
        ]

        for label, value in items:
            if value and value.strip():
                lines.append(f"- {label}: {value.strip()}")

        return lines

    def has_content(self) -> bool:
        return any(value and value.strip() for value in self.to_dict().values())


@dataclass(frozen=True)
class PromptTemplateSpec:
    """Output-type context that keeps prompt assembly specification-driven."""

    output_type: PromptOutputType
    title: str
    purpose: str
    output_focus: str
    instructions: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PromptTemplate:
    """A reusable prompt template definition for one output type."""

    spec: PromptTemplateSpec
    system_prompt: str
    user_prompt_prefix: str
    output_requirements: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PromptAssembly:
    """Prompt-ready structure assembled from knowledge base content and user inputs."""

    template: PromptTemplate
    knowledge_base: dict
    user_inputs: PromptInputBundle
    prompt_text: str

    def to_dict(self) -> dict:
        return {
            "template": self.template.to_dict(),
            "knowledge_base": self.knowledge_base,
            "user_inputs": self.user_inputs.to_dict(),
            "prompt_text": self.prompt_text,
        }


PROMPT_TEMPLATES: dict[PromptOutputType, PromptTemplate] = {
    "instagram_posts": PromptTemplate(
        spec=PromptTemplateSpec(
            output_type="instagram_posts",
            title="Instagram Posts",
            purpose="Create brand-aligned Instagram copy that feels native to the platform.",
            output_focus="Short-form social captions with a clear hook, brand voice, and action.",
            instructions=(
                "Write for Instagram-native attention patterns.",
                "Keep the tone consistent with the brand knowledge base.",
                "Use the CTA only if it supports the post naturally.",
                *NO_CONVERSATIONAL_FOLLOWUP_INSTRUCTION,
            ),
        ),
        system_prompt="You are preparing brand-aligned Instagram post copy using the provided brand knowledge base. Return only the requested content itself.",
        user_prompt_prefix="Create an Instagram post using the following brief.",
        output_requirements=(
            "Lead with a strong opening line.",
            "Keep the copy concise and engaging.",
            "Make sure the result matches the brand voice.",
        ),
    ),
    "launch_copy": PromptTemplate(
        spec=PromptTemplateSpec(
            output_type="launch_copy",
            title="Launch Copy",
            purpose="Create launch messaging that clearly introduces a product, offer, or campaign.",
            output_focus="Launch-ready copy with clarity, momentum, and brand alignment.",
            instructions=(
                "Highlight the launch objective clearly.",
                "Balance excitement with brand credibility.",
                "Keep the structure easy to adapt into final marketing copy.",
                *NO_CONVERSATIONAL_FOLLOWUP_INSTRUCTION,
            ),
        ),
        system_prompt="You are preparing brand-aligned launch copy using the provided brand knowledge base. Return only the requested content itself.",
        user_prompt_prefix="Create launch copy using the following brief.",
        output_requirements=(
            "Make the launch objective easy to understand.",
            "Use persuasive but brand-safe language.",
            "Keep the copy adaptable for downstream use.",
        ),
    ),
    "product_descriptions": PromptTemplate(
        spec=PromptTemplateSpec(
            output_type="product_descriptions",
            title="Product Descriptions",
            purpose="Create clear product descriptions that foreground value and brand voice.",
            output_focus="Benefit-led product language that stays specific and readable.",
            instructions=(
                "Focus on benefits, features, and brand-aligned framing.",
                "Avoid generic e-commerce phrasing where possible.",
                "Keep the copy easy to scan.",
                *NO_CONVERSATIONAL_FOLLOWUP_INSTRUCTION,
            ),
        ),
        system_prompt="You are preparing brand-aligned product description copy using the provided brand knowledge base. Return only the requested content itself.",
        user_prompt_prefix="Create a product description using the following brief.",
        output_requirements=(
            "Describe the product in a specific and useful way.",
            "Keep the tone aligned with the brand identity.",
            "Write in a format that can be reused in marketing assets.",
        ),
    ),
    "creative_design_ideas": PromptTemplate(
        spec=PromptTemplateSpec(
            output_type="creative_design_ideas",
            title="Creative and Design Ideas",
            purpose="Generate creative directions that support brand-safe visual and conceptual exploration.",
            output_focus="Actionable design ideas, visual motifs, and campaign directions.",
            instructions=(
                "Focus on ideas rather than finished artwork.",
                "Use the brand knowledge base to anchor symbolism and tone.",
                "Keep recommendations practical enough to brief a designer.",
                *NO_CONVERSATIONAL_FOLLOWUP_INSTRUCTION,
            ),
        ),
        system_prompt="You are preparing brand-aligned creative and design ideas using the provided brand knowledge base. Return only the requested content itself.",
        user_prompt_prefix="Create creative and design ideas using the following brief.",
        output_requirements=(
            "Stay close to the brand identity and context.",
            "Offer ideas that a human can review and refine.",
            "Keep the output concrete and easy to act on.",
        ),
    ),
}


def get_prompt_template(output_type: PromptOutputType) -> PromptTemplate:
    """Return the template for a supported MVP output type."""

    try:
        return PROMPT_TEMPLATES[output_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported prompt output type: {output_type}") from exc


def assemble_prompt(
    parsed_knowledge_base: ParsedKnowledgeBase,
    user_inputs: PromptInputBundle,
    output_type: PromptOutputType,
) -> PromptAssembly:
    """Assemble a prompt-ready structure without calling an LLM."""

    template = get_prompt_template(output_type)
    knowledge_base_payload = parsed_knowledge_base.to_prompt_payload()
    prompt_text = _build_prompt_text(template, knowledge_base_payload, user_inputs)

    return PromptAssembly(
        template=template,
        knowledge_base=knowledge_base_payload,
        user_inputs=user_inputs,
        prompt_text=prompt_text,
    )


def _build_prompt_text(
    template: PromptTemplate,
    knowledge_base_payload: dict,
    user_inputs: PromptInputBundle,
) -> str:
    lines: list[str] = [
        template.system_prompt,
        "",
        template.user_prompt_prefix,
        "",
        f"Output type: {template.spec.title}",
        f"Purpose: {template.spec.purpose}",
        f"Focus: {template.spec.output_focus}",
        "",
        "Output requirements:",
    ]

    for requirement in template.output_requirements:
        lines.append(f"- {requirement}")

    lines.extend(["", "Template instructions:"])
    for instruction in template.spec.instructions:
        lines.append(f"- {instruction}")

    lines.extend(["", "Brand knowledge base:"])
    lines.extend(_format_knowledge_base_payload(knowledge_base_payload))

    if user_inputs.has_content():
        lines.extend(["", "User inputs:"])
        lines.extend(user_inputs.to_prompt_lines())

    return "\n".join(lines).strip()


def _format_knowledge_base_payload(knowledge_base_payload: dict) -> list[str]:
    lines: list[str] = []

    for section_name in ("primary", "secondary"):
        sections = knowledge_base_payload.get(section_name, [])
        if not sections:
            lines.append(f"- {section_name.title()}: none provided")
            continue

        lines.append(f"- {section_name.title()}:")
        for section in sections:
            lines.append(f"  - {section['category']}")
            text = section["text"].strip()
            if text:
                for block_line in text.splitlines():
                    lines.append(f"    {block_line}")

    return lines
