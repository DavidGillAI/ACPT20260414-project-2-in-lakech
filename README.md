# In Lak'ech MVP

In Lak'ech is a human-guided AI brand storytelling and content generation MVP. The codebase is focused on a small, modular pipeline that ingests brand Markdown, structures that knowledge, assembles prompts, sends them to an LLM, and returns generated content for human review.

## Project Overview

The MVP is built around the idea that brand knowledge should shape generated output in a controlled and reviewable way. It does not attempt to automate the full content lifecycle. Instead, it provides a clear sequence of steps:

1. Load brand source material from Markdown documents.
2. Parse the knowledge base into primary and secondary brand context.
3. Assemble prompt-ready content using structured user inputs.
4. Send the assembled prompt to the OpenAI API.
5. Return generated text for human review.

The current implementation is intentionally lightweight and specification-driven.

## MVP Purpose

The MVP is meant to demonstrate:

- structured Markdown ingestion
- brand knowledge organization
- prompt engineering based on brand context
- OpenAI-based text generation
- human-in-the-loop review
- comparison testing for output uniqueness
- explicit content-type workflows

It is not intended to be a full production system.

## Architecture Summary

The repository is organized as a linear set of reusable subsystems:

- `src/ingestion/`
  - loads Markdown documents from `knowledge_base/primary` and `knowledge_base/secondary`
- `src/knowledge_base/`
  - parses and groups the loaded Markdown into structured categories
- `src/prompt_engineering/`
  - defines prompt templates and assembles prompt-ready structures
- `src/llm_integration/`
  - sends assembled prompt text to OpenAI and returns generated text
- `src/workflow/`
  - runs the end-to-end generation pipeline
- `src/output_uniqueness_testing/`
  - compares brand-aligned generation against a generic no-context run
- `src/human_review/`
  - models review decisions, notes, and revision feedback
- `src/content_type_workflows/`
  - provides explicit entry points for the supported MVP content types

The overall design is intentionally modular but not over-abstracted.

## Subsystem Overview

### Markdown Ingestion

The ingestion subsystem loads Markdown files from the knowledge base folders and returns a structured snapshot.

Implemented in:

- [src/ingestion/markdown_ingestion.py](src/ingestion/markdown_ingestion.py)

### Knowledge Base Parser

The parser groups documents into primary and secondary knowledge sections and prepares prompt-friendly payloads.

Implemented in:

- [src/knowledge_base/parser.py](src/knowledge_base/parser.py)

### Prompt Engineering

The prompt subsystem defines template metadata for the supported MVP output types:

- Instagram posts
- launch copy
- product descriptions
- creative/design ideas

It also collects structured user inputs such as tone, CTA, platform, word count, target audience, example content, and detailed instructions.

Implemented in:

- [src/prompt_engineering/templates.py](src/prompt_engineering/templates.py)

### LLM Integration

The LLM integration subsystem is a thin OpenAI wrapper. It accepts assembled prompt text, sends it to the OpenAI Responses API, and returns structured generated text.

Implemented in:

- [src/llm_integration/openai_integration.py](src/llm_integration/openai_integration.py)

### Generation Workflow

The generation workflow connects ingestion, parsing, prompt assembly, and LLM execution into one linear pipeline.

Implemented in:

- [src/workflow/content_generation.py](src/workflow/content_generation.py)

### Output Uniqueness Testing

This subsystem runs a brand-aligned generation and a generic no-context generation, then returns a side-by-side comparison for human review.

Implemented in:

- [src/output_uniqueness_testing/comparison.py](src/output_uniqueness_testing/comparison.py)

### Human-in-the-Loop Review

The review subsystem formalizes the human review stage with explicit statuses, reviewer notes, and revision feedback.

Implemented in:

- [src/human_review/review_workflow.py](src/human_review/review_workflow.py)

### Content Type Workflows

Dedicated workflows provide explicit entry points for each supported MVP output type while reusing the shared generation and review logic.

Implemented in:

- [src/content_type_workflows/content_type_workflows.py](src/content_type_workflows/content_type_workflows.py)

## Current Supported Workflows

The current codebase supports the following content-type workflows:

- Instagram content
- Product descriptions
- Launch copy
- Creative/design ideas

Each workflow:

- uses the shared generation pipeline
- uses the shared prompt templates
- returns a structured generation result
- creates a human review record

## Installation and Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Prepare the knowledge base

The repository expects this structure:

```text
knowledge_base/
  primary/
  secondary/
```

Markdown documents placed in those folders will be loaded by the ingestion subsystem.

## Environment Variables

The LLM integration reads environment variables from the local environment and, if available, from `.env`.

Required:

- `OPENAI_API_KEY`

Optional:

- `OPENAI_MODEL`

Example `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
```

## Test Instructions

Run the unit tests with the project virtual environment:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_markdown_ingestion tests.test_knowledge_base_parser tests.test_prompt_engineering_templates tests.test_llm_integration tests.test_workflow tests.test_output_uniqueness_testing tests.test_human_review_workflow tests.test_content_type_workflows
```

The tests are designed to be offline and deterministic. They use fake generators where real API calls would otherwise be required.

## Project Constraints and Philosophy

The MVP is intentionally constrained to preserve the human-guided design philosophy described in `PROJECT_REQUIREMENTS.md`.

Current constraints include:

- no autonomous workflows
- no agents
- no embeddings
- no vector database
- no RAG
- no automatic publishing
- no frontend UI
- no autonomous revision loops
- no automated evaluation scoring

The system is meant to support human judgment, not replace it.

## Current Project Status

Implemented subsystems:

- Markdown ingestion
- knowledge base parsing
- prompt engineering templates
- OpenAI LLM integration
- end-to-end generation workflow
- output uniqueness testing
- human-in-the-loop review workflow
- content-type-specific workflows

Current behavior:

- content is generated once
- outputs are returned in structured form
- human review is required after generation
- comparison testing is available for brand-aligned versus generic output

Not yet implemented:

- frontend UI
- publishing
- scheduling
- automated revision loops
- autonomous agents
- database persistence

## Example Workflow Flow

One typical flow looks like this:

1. A user provides structured inputs such as tone, CTA, platform, and target audience.
2. The workflow loads Markdown files from the knowledge base.
3. The parser organizes those documents into primary and secondary brand context.
4. The prompt subsystem assembles a prompt for the selected content type.
5. The LLM integration sends the prompt to OpenAI.
6. The system returns a structured generation result.
7. The human review subsystem records approval, rejection, or revision feedback.

For uniqueness testing, the system can also:

1. Generate one output with brand context.
2. Generate one output without brand context.
3. Present both outputs side by side for human comparison.

## Future Improvements

The following items are natural next steps, but they are not implemented yet:

- a lightweight reviewer interface
- persistence for review decisions
- richer metadata for comparison runs
- additional content-type workflows if approved by scope
- better developer documentation examples
- packaging or CLI entry points for running workflows interactively

Any future change should continue to follow the scope rules in `PROJECT_REQUIREMENTS.md`.
