from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from src.content_type_workflows import (  # noqa: E402
    CreativeDesignIdeasWorkflow,
    InstagramContentWorkflow,
    LaunchCopyWorkflow,
    ProductDescriptionsWorkflow,
)
from src.prompt_engineering import PromptInputBundle  # noqa: E402


RESULTS_PATH = REPO_ROOT / "docs" / "live_smoke_test_results.md"


def _format_markdown_results(run_timestamp: str, results: list[dict]) -> str:
    lines = [
        "# Live Smoke Test Results",
        "",
        f"- Timestamp: {run_timestamp}",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"## {result['name']}",
                "",
                f"- Workflow/output type: {result['workflow_type']}",
                f"- Model used: {result['model']}",
                f"- Review status: {result['review_status']}",
                "",
                "Generated output:",
                "",
                "```text",
                result["generated_output"].strip(),
                "```",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def _run_workflow(name: str, workflow, user_inputs: PromptInputBundle) -> None:  # noqa: ANN001
    print(f"\n=== {name} ===")
    result = workflow.run(user_inputs)

    print(f"Model: {result.generation_result.generation.model}")
    print(f"Review status: {result.review_record.status}")
    print("Generated output:")
    print(result.generation_result.generation.text)

    return {
        "name": name,
        "workflow_type": result.metadata.output_type,
        "model": result.generation_result.generation.model,
        "review_status": result.review_record.status,
        "generated_output": result.generation_result.generation.text,
    }


def main() -> None:
    instagram_inputs = PromptInputBundle(
        tone="calm, confident, and minimal",
        platform="Instagram",
        cta="Explore the drop",
        campaign_objective="Introduce the new capsule collection",
        target_audience="Design-conscious streetwear buyers",
        word_count="80",
        example_content="Short caption with symbolic language and a quiet tone.",
        detailed_instructions="Keep it text-only, concise, and brand-aligned.",
    )

    launch_inputs = PromptInputBundle(
        tone="clear and restrained",
        platform="Website",
        cta="Shop the launch",
        campaign_objective="Announce the launch collection",
        target_audience="Audience interested in minimalist fashion",
        word_count="120",
        example_content="Launch copy that feels premium without sounding loud.",
        detailed_instructions="Emphasize the launch intent and keep the language understated.",
    )

    product_inputs = PromptInputBundle(
        tone="precise and calm",
        platform="Product page",
        cta="Add to cart",
        campaign_objective="Describe a core product clearly",
        target_audience="People who value durable, minimal design",
        word_count="90",
        example_content="Benefit-led description with a subtle emotional angle.",
        detailed_instructions="Focus on usefulness, restraint, and brand voice.",
    )

    creative_inputs = PromptInputBundle(
        tone="reflective and symbolic",
        platform="Creative brief",
        campaign_objective="Generate visual and conceptual directions",
        target_audience="Creative collaborators and internal reviewers",
        word_count="100",
        example_content="Design ideas centered on motifs and atmosphere.",
        detailed_instructions="Keep the output text-only and actionable for a designer.",
    )

    run_timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    results = [
        _run_workflow("Instagram caption text", InstagramContentWorkflow(), instagram_inputs),
        _run_workflow("Launch copy", LaunchCopyWorkflow(), launch_inputs),
        _run_workflow("Product description", ProductDescriptionsWorkflow(), product_inputs),
        _run_workflow("Creative/design ideas", CreativeDesignIdeasWorkflow(), creative_inputs),
    ]

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(_format_markdown_results(run_timestamp, results), encoding="utf-8")
    print(f"\nSaved smoke test results to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
