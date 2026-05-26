from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from src.output_uniqueness_testing import OutputUniquenessComparisonRequest, OutputUniquenessTestingWorkflow  # noqa: E402
from src.prompt_engineering import PromptInputBundle  # noqa: E402


RESULTS_PATH = REPO_ROOT / "docs" / "live_uniqueness_comparison_results.md"


def _format_markdown_results(run_timestamp: str, result) -> str:  # noqa: ANN001
    lines = [
        "# Live Uniqueness Comparison Results",
        "",
        f"- Timestamp: {run_timestamp}",
        f"- Model: {result.request.model or 'default model'}",
        f"- Output type: {result.request.output_type}",
        "",
        "## Review Criteria",
        "",
    ]

    for criterion in result.criteria:
        lines.extend(
            [
                f"### {criterion.name}",
                "",
                criterion.description,
                "",
            ]
        )

    lines.extend(
        [
            "## Brand-Aligned Output",
            "",
            f"- Review status: {result.brand_aligned.generation_result.review_status}",
            "",
            "```text",
            result.brand_aligned.generation_result.generation.text.strip(),
            "```",
            "",
            "## Generic Output",
            "",
            f"- Review status: {result.generic_non_context.generation_result.review_status}",
            "",
            "```text",
            result.generic_non_context.generation_result.generation.text.strip(),
            "```",
            "",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    user_inputs = PromptInputBundle(
        tone="calm, confident, and minimal",
        platform="Instagram",
        cta="Explore the drop",
        campaign_objective="Compare brand-aligned output with generic output",
        target_audience="Design-conscious streetwear buyers",
        word_count="80",
        example_content="Short caption with symbolic language and a quiet tone.",
        detailed_instructions="Keep it text-only, concise, and brand-aligned.",
    )

    comparison_request = OutputUniquenessComparisonRequest(
        output_type="instagram_posts",
        user_inputs=user_inputs,
        model=None,
    )

    run_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    workflow = OutputUniquenessTestingWorkflow()
    result = workflow.run(comparison_request)

    print("\n=== Brand-Aligned Output ===")
    print(f"Model: {result.brand_aligned.generation_result.generation.model}")
    print(f"Review status: {result.brand_aligned.generation_result.review_status}")
    print(result.brand_aligned.generation_result.generation.text)

    print("\n=== Generic Output ===")
    print(f"Model: {result.generic_non_context.generation_result.generation.model}")
    print(f"Review status: {result.generic_non_context.generation_result.review_status}")
    print(result.generic_non_context.generation_result.generation.text)

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(_format_markdown_results(run_timestamp, result), encoding="utf-8")
    print(f"\nSaved comparison results to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
