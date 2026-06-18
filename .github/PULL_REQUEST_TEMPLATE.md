## Summary

<!-- 1-3 bullet points: what this PR does -->

-
-

## Why

<!-- The motivation: bug fix, feature, refactor, perf, etc. Link to an issue if one exists. -->

## Changes

<!-- Notable implementation choices or non-obvious decisions -->

-

## Test Plan

- [ ] Unit tests pass (`cd backend && uv run pytest tests/unit -v`)
- [ ] Integration tests pass (`cd backend && uv run pytest tests/integration -v`)
- [ ] Lint clean (`cd backend && uv run ruff check src/ tests/`)
- [ ] Type check clean (`cd backend && uv run mypy src/pitchmind`)
- [ ] Frontend checks pass (`cd frontend && npm run lint && npm run typecheck`)
- [ ] Manual smoke: infra up (`docker compose up db cache minio -d`), API starts, key flow tested
- [ ] Edge cases considered:

## Screenshots / Recordings

<!-- For UI changes: before/after screenshots or a short Loom. Delete if not applicable. -->

## Risks & Rollback

<!-- What could go wrong? How do we roll back if needed? -->

## Checklist

- [ ] Follows commit convention (`feat/fix/docs/refactor/test/chore`)
- [ ] No secrets or large binaries committed
- [ ] `PROJECT_PROGRESS.md` and `TODO.md` updated if applicable
- [ ] `CHANGELOG.md` updated if this closes a milestone
- [ ] ADR written if a cross-cutting architectural decision was made
