# PROJECT_REQUIREMENTS.md

## 1. Project Overview
**Project Name:** In Lak'ech

In Lak'ech is a human-guided AI brand storytelling and content generation system. Its purpose is to help brands scale AI-assisted content while preserving identity, voice, symbolism, values, and creative integrity.

The system is based on the principle that AI should reflect and preserve authentic brand identity rather than produce generic or homogenised content.

## 2. MVP Goals
The MVP must:

- ingest brand source material from Markdown documents
- store brand knowledge in a structured knowledge base
- use prompt engineering to shape generation
- integrate with an LLM for content generation
- produce brand-aligned content outputs
- keep a human review step in the workflow

The MVP must support specification-driven development and remain focused on understanding architecture, workflow, and implementation.

## 3. In Scope
The following are in scope for the MVP:

- Markdown document ingestion
- structured brand knowledge base
- prompt engineering workflow
- LLM integration
- brand-aligned content generation
- human-in-the-loop review workflow
- planned output types:
  - Instagram posts
  - launch copy
  - product descriptions
  - creative/design ideas
- user input collection through:
  - tick boxes
  - dropdown menus
  - free text fields
- support for inputs such as:
  - target audience
  - tone
  - platform
  - CTA
  - campaign objective
  - word count
  - example content
  - detailed generation instructions
- a knowledge base that distinguishes between:
  - primary brand information
  - secondary contextual information
- a workflow structure that supports Trello-style task tracking:
  - Backlog
  - Doing
  - Review
  - Done
  - Discarded

## 4. Out of Scope
The following are explicitly out of scope for the MVP:

- full RAG/vector database architecture
- autonomous publishing
- fully autonomous content generation
- advanced frontend development
- social media API integration
- autonomous posting
- complex image generation pipelines

Anything not explicitly listed in scope should be treated as out of scope unless added through a documented scope change.

## 5. Inputs
The system must accept user-configured generation inputs through a combination of tick boxes, dropdown menus, and free text fields.

Supported input examples include:

- target audience
- tone
- platform
- CTA
- campaign objective
- word count
- example content
- detailed generation instructions

The input system must allow the user to select desired outputs and provide enough context for brand-aligned generation.

## 6. Knowledge Base Structure
The knowledge base must be structured into two parts:

### Primary Database
The primary database contains the unchangeable aspects of the brand:

- manifesto
- philosophy
- core beliefs and values
- tone and voice
- symbolism
- audience profile
- existing content
- past successful copy/content
- terminology and messaging

### Secondary Database
The secondary database contains contextual and evolving information:

- industry trends
- competitor analysis
- market positioning
- consumer sentiment
- cultural references
- emotionally resonant branding examples
- audience and market insights

The knowledge base structure must preserve the distinction between stable brand identity and changing context.

## 7. Output Types
The MVP must support the following output types:

- Instagram posts
- launch copy
- product descriptions
- creative/design ideas

Each output type must be generated in a way that remains aligned with the brand knowledge base and user-supplied instructions.

## 8. Human Review Workflow
Human review is mandatory in the MVP workflow.

Workflow expectations:

- AI assists generation
- a human reviews the output before it is considered complete
- major decisions remain under human control
- the system supports creativity rather than replacing it

Human-guided review should ensure that output quality, tone, and brand alignment are checked before acceptance.

## 9. Technical Requirements
The MVP must satisfy the following technical requirements:

- support Markdown document ingestion
- organise brand knowledge into a structured folder or data model
- support prompt engineering templates
- connect to an LLM for generation
- support the defined output types
- support a human-in-the-loop review step
- keep the implementation specification-driven
- avoid unnecessary frontend complexity
- avoid architecture that depends on full RAG/vector search

Suggested project structure:

- `codex/`
  - `instructions.md`
  - `rules.md`
- `knowledge_base/`
  - `primary/`
  - `secondary/`
- `src/`
- `config/`
- `README.md`
- `PROJECT_REQUIREMENTS.md`
- `requirements.txt`
- `.env`
- `.gitignore`

Workflow and delivery requirements:

- Trello columns must remain:
  - Backlog
  - Doing
  - Review
  - Done
  - Discarded
- only 3 to 4 tasks may be active in Doing at once
- Done means implemented, tested, and reviewed
- Discarded means consciously removed from MVP scope
- major scope changes must be logged in this file

## 10. Success Criteria
The MVP is successful if it can:

- ingest Markdown brand documents
- store and organise brand knowledge
- use that knowledge in prompt engineering
- generate content through an LLM
- produce outputs that stay aligned with the brand identity
- support human review before completion
- keep the system focused on the defined MVP scope

Quality expectation:

- outputs should feel brand-specific rather than generic
- the workflow should preserve the brand's identity, voice, symbolism, values, and creative integrity

## 11. Scope Control Rules
These rules govern changes to the MVP:

- do not add new features without approval
- do not expand the scope beyond the sections in this document
- do not implement out-of-scope items during MVP work
- treat missing functionality as out of scope unless explicitly added here
- log major scope changes in `PROJECT_REQUIREMENTS.md`
- keep work aligned with the human-guided philosophy
- prefer small, reviewable changes over broad autonomous implementation
- if a proposed task pushes beyond MVP scope, move it to Discarded or defer it

Any future change must be assessed against the MVP goals, in-scope items, and out-of-scope items before implementation.
