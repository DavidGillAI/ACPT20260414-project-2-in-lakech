# Prompt Tracking Log

This log records representative Codex prompts and review decisions from the In Lak'ech MVP build. It is not a full transcript. The goal is to show how specification-driven prompting, human oversight, and iterative refinement shaped the implementation.

## 1. Prompting Phases

| Phase | Representative prompt intent | Purpose |
| --- | --- | --- |
| Prompt engineering subsystem | "Implement only the Prompt Engineering Templates subsystem... support Instagram posts, launch copy, product descriptions, and creative/design ideas." | Establish the prompt template layer and keep it separate from LLM execution. |
| Brand-agnostic wording correction | "Remove all hardcoded references to 'In Lak'ech brand' from prompt templates." | Keep templates reusable and aligned with provided brand context rather than a fixed brand name. |
| LLM API integration | "Implement only the LLM API Integration subsystem... accept assembled prompt text from PromptAssembly and return generated text." | Add a thin OpenAI wrapper with structured output and environment-based configuration. |
| End-to-end workflow | "Implement only the Brand-Aligned Content Generation Workflow subsystem." | Connect ingestion, parsing, prompting, and generation into one linear pipeline. |
| Output uniqueness testing | "Implement only the Output Uniqueness Testing subsystem." | Compare brand-aligned output against generic output without automated scoring. |
| Human review workflow | "Implement only the Human-in-the-Loop Review Workflow subsystem." | Formalize review states, reviewer notes, and revision feedback without regeneration. |
| Content type workflows | "Implement only the MVP Content Type Workflows subsystem." | Expose explicit entry points for each supported content type while reusing existing logic. |
| Supporting documentation | "Create a professional README.md for the In Lak'ech MVP." | Document the actual implemented architecture, constraints, and setup. |
| Research structure | "Create a structured secondary knowledge base for the MVP." | Split research notes into parser-friendly Markdown files. |
| Live verification | "Create a minimal live smoke test script" and "Create a minimal live uniqueness comparison script." | Produce real end-to-end evidence files for demonstration and evaluation. |

## 2. Human Review and Correction Decisions

| Decision | What changed | Why it mattered |
| --- | --- | --- |
| Removed fixed brand wording from prompt templates | Replaced "In Lak'ech brand" with neutral language about the provided brand knowledge base. | Made the template system brand-agnostic and reusable. |
| Kept generation linear | Added the workflow layer without retries, branching, orchestration, agents, or memory. | Preserved the human-guided MVP scope. |
| Reused existing subsystems | The content workflows, comparison layer, and review layer all wrap earlier code rather than replacing it. | Prevented duplication and kept the architecture readable. |
| Kept uniqueness evaluation human-guided | The comparison subsystem returns side-by-side outputs and review criteria, but no automated scoring. | Avoided false certainty and respected the evaluation constraint. |
| Kept review state explicit | Review records carry `awaiting_review`, `approved`, `rejected`, and `needs_revision` states. | Made human oversight visible in the data model. |

## 3. Scope Control Examples

| Scope control prompt | Outcome |
| --- | --- |
| "Do not implement RAG, embeddings, autonomous workflows, API integration, or frontend UI." | The prompt engineering and workflow layers were kept simple and non-autonomous. |
| "Do not add new architecture." | The content type workflows were implemented as thin wrappers around the existing generation pipeline. |
| "Do not implement automated scoring." | The uniqueness comparison subsystem stayed descriptive and review-oriented. |
| "Do not modify unrelated files unless tests require it." | Changes stayed localized to the relevant subsystem and its tests. |
| "Keep the implementation lightweight and readable." | The code uses small dataclasses and direct orchestration rather than a large abstraction stack. |

## 4. Architectural Guidance

| Architectural guidance prompt | Result |
| --- | --- |
| "Using PROJECT_REQUIREMENTS.md as the source of truth." | Every subsystem was implemented against the documented MVP scope. |
| "Work with the existing parser subsystem." | Prompt assembly consumes the parser output directly. |
| "Reuse the existing generation pipeline." | Content-type workflows and review layers wrap the same core generation flow. |
| "Use the OpenAI Python SDK." | The LLM integration became a thin SDK wrapper around the Responses API. |
| "Formalise the human review stage." | A dedicated review module now models status, notes, and revision feedback. |

## 5. Testing and Verification Before Commit

| Verification step | What was checked |
| --- | --- |
| Unit tests for ingestion and parsing | Markdown discovery, loading, and knowledge-base grouping behaved as expected. |
| Unit tests for prompt templates | All supported output types assembled prompt-ready structures correctly. |
| Unit tests for LLM integration | The OpenAI wrapper accepted prompt text and returned structured output using a fake client. |
| Unit tests for workflow layers | End-to-end generation, comparison, review, and content-type workflows all stayed compatible. |
| Syntax checks for live scripts | The smoke test and uniqueness comparison scripts compiled cleanly before use. |
| Live result files | The smoke test and uniqueness comparison scripts wrote Markdown evidence files for review. |

## 6. Iterative Refinement

| Iteration | Refinement |
| --- | --- |
| Prompt templates | Removed hardcoded brand references and kept wording generic. |
| Knowledge base structure | Split research into focused secondary Markdown notes instead of one large document. |
| LLM integration | Kept the API layer minimal, with environment-based configuration and a single generation call. |
| Comparison testing | Used side-by-side outputs and reviewer criteria instead of a scoring engine. |
| Human review | Added explicit review records rather than assuming approval inside the generation flow. |
| Content workflows | Added small dedicated entry points for each supported output type instead of a generic workflow registry. |
| Live evidence | Added Markdown result files so smoke tests and comparison runs leave an inspectable trail. |

## 7. Review Discipline Observed

- Prompts consistently referenced `PROJECT_REQUIREMENTS.md` as the source of truth.
- Scope was repeatedly narrowed when a request risked becoming broader than the MVP.
- Testing was used to validate each subsystem before moving to the next layer.
- Human decisions remained explicit in the data model instead of being implied by the code path.
- The build stayed focused on content generation support, not autonomous content operations.

## 8. Summary

The project was developed through a sequence of small, specification-driven prompts. Each step added one layer, validated it, and then moved upward. Human review was used to keep the system aligned with the MVP scope, preserve clarity, and prevent feature creep.
