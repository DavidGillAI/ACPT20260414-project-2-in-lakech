# Codex Rules for In Lak'ech

## Source of Truth
- Treat `PROJECT_REQUIREMENTS.md` as the source of truth.
- Do not work outside the documented MVP scope.
- If something is not in the requirements, treat it as out of scope unless explicitly approved.

## Scope Control
- Prevent scope creep.
- Do not add features that are not part of the MVP.
- Do not expand the project into adjacent product ideas.
- Do not implement out-of-scope functionality during MVP work.

## Prohibited Behaviours
- Do not create autonomous workflows.
- Do not introduce unnecessary frontend complexity.
- Do not design or implement RAG/vector database architecture.
- Do not make major architectural changes without approval.
- Do not create extra abstraction layers without a clear need.

## Development Discipline
- Keep changes small and reviewable.
- Prefer changes that can be understood and checked easily.
- Do not bundle unrelated work into one change.
- Avoid overengineering.

## Philosophy
- Preserve the human-guided philosophy of the project.
- Keep AI in a support role rather than a replacement role.
- Protect brand identity, creative integrity, and human judgment.

## Review and Change Control
- Require small reviewable commits.
- Do not make broad unreviewed transformations.
- When a change could alter direction, pause and request approval.
- Treat major changes as exceptions, not defaults.
