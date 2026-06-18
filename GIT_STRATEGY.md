# Git Strategy — PitchMind AI

**Version:** 0.2 (Active)
**Status:** Approved — in force from Phase 1

This document is binding for both the human contributor and any AI assistant working in the repository.

---

## 1. Hard Rules (Assistant Behaviour)

The assistant **MUST NOT** execute any of the following automatically. It may **suggest** commands and **wait for explicit approval** before any of them are run:

- `git init`, `git remote add`, any change to git configuration.
- `git add`, `git commit`, `git commit --amend`.
- `git push`, `git push --force`, `git push --tags`.
- `git tag`, `git branch`, `git checkout -b`, `git switch -c`.
- `git merge`, `git rebase`, `git cherry-pick`.
- `git reset` (any mode), `git restore`, `git clean -f`.
- Any destructive operation (history rewrite, branch / tag deletion).

For every action the assistant proposes, it will provide:

1. The exact command(s).
2. A summary of what will change and what the impact is.
3. Risks and how to reverse if needed.
4. A request for explicit approval (`yes / no`).

---

## 2. Git Identity (Critical Pre-Flight)

Before any git operation, verify identity:

```bash
git config user.name
git config user.email
```

If incorrect or unset, the assistant will:

1. Ask the user for their **GitHub username** and **commit email**.
2. Display the configuration commands:

   ```bash
   git config user.name  "<USERNAME>"
   git config user.email "<EMAIL>"
   ```

3. Wait for approval.
4. After running, re-verify with `git config user.name && git config user.email`.
5. Record the approved identity in `PROJECT_PROGRESS.md` under "Git Identity".

All commits must use this exact identity. No placeholders, no generated identities, no anonymous identities.

---

## 3. Branching Model

Trunk-based with short-lived feature branches.

- `main` — always green, deployable.
- `feat/<area>-<short-slug>` — features.
- `fix/<area>-<short-slug>` — bug fixes.
- `chore/<short-slug>` — tooling, deps, docs.
- `docs/<short-slug>` — documentation only.
- `refactor/<area>-<short-slug>` — non-functional restructuring.
- `test/<area>-<short-slug>` — test additions.

Lifetime target: ≤ 3 days per branch.

Direct commits to `main` are not allowed once Phase 1 ships. During Phase 0 the only commits to `main` are these planning docs and the initial scaffold.

---

## 4. Commit Convention

Conventional Commits with a scope:

```
<type>(<scope>): <summary>

[optional body — wrap at 72 cols, explain *why*]

[optional footers — refs, breaking changes]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`, `style`.

**Scopes (examples):** `cv`, `ml`, `agent`, `api`, `ui`, `db`, `infra`, `docs`, `repo`.

### Examples

```
feat(cv): implement YOLOv11 player detection stage

fix(api): reject zero-byte uploads with 422

docs(architecture): add ADR-0003 (tracker interface)

refactor(agents): extract tool registry into typed module

test(ml): add time-respecting CV harness for outcome model

chore(repo): pin python to 3.11 in CI

perf(cv): batch inference at 16 frames; 1.7x throughput on 3060
```

### Rules

- Subject ≤ 72 chars, imperative mood, no trailing period.
- Body explains the *why*. The diff explains the *what*.
- One logical change per commit. No mixed concerns.
- No commits that knowingly break `main`.

---

## 5. Pull Request Workflow

1. Branch from latest `main`.
2. Small commits while iterating; squash optional at merge.
3. Open PR with the template (`.github/PULL_REQUEST_TEMPLATE.md`):

   ```
   ## Summary
   ## Changes
   ## Why
   ## Screens / Recordings
   ## Test Plan
   ## Risks / Rollback
   ## Linked Issues
   ## Checklist
   ```

4. CI must be green.
5. At least one self-review pass before requesting human review.
6. Merge strategy: **squash-and-merge** by default; merge commits only for cross-phase integration branches.

---

## 6. Release & Tagging

- Semantic versioning: `MAJOR.MINOR.PATCH`.
- Pre-MVP: `0.x.y`. MVP launch: `1.0.0`.
- Tags created **only after explicit approval**, with a release note in `CHANGELOG.md`.
- Suggested tag commands are shown; the assistant never executes them.

---

## 7. Commit / Push Approval Loop

Every time the assistant has work ready to commit, it will:

1. Show files modified (path + brief description).
2. Suggest the staging set (specific files, not `git add .`).
3. Suggest commit message(s).
4. Suggest the commands:

   ```bash
   git add backend/src/pitchmind/cv/detectors/yolov11.py \
           backend/tests/unit/cv/test_yolov11.py
   git commit -m "feat(cv): implement YOLOv11 player detection stage"
   ```

5. Ask: **"Do you want me to proceed with this commit? (yes/no)"** — and wait.

After the commit:

1. Show `git status` and the commit SHA.
2. Suggest push if appropriate:

   ```bash
   git push origin main
   ```

3. Ask: **"Do you want to push this commit? (yes/no)"** — and wait.

---

## 8. Authorship Requirements

- All commits use the **exact** git identity recorded in `PROJECT_PROGRESS.md`.
- `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` footer is appended to commits where the assistant generated the bulk of the code. This was agreed by the user from Phase 1.
- No author override flags.
- No `--no-verify`, no signature bypass, no hook skip, unless the user has explicitly asked for it in this session.

---

## 9. Repository Safety

Destructive or hard-to-reverse operations require an extra confirmation step where the assistant:

1. Names the operation and the affected refs.
2. Explains the **impact** (data lost, history rewritten, force-push consequences).
3. Explains the **risks** (lost work, broken downstream clones).
4. Offers safer alternatives (revert commit, new branch, soft reset).
5. Lists **recovery options** (`reflog`, backup branch).
6. Awaits explicit `yes` before suggesting the command.

The assistant will refuse a force-push to `main`/`master` outright and warn the user when asked.

---

## 10. .gitignore Principles

- Never commit secrets (`.env`, credentials).
- Never commit large binaries (use object store).
- Never commit generated data (`data/raw`, `data/interim`).
- Commit small fixtures (`data/samples/*` under a size cap).
- Commit generated TS API client (for diff visibility).

---

## 11. Hooks (Phase 1)

- **pre-commit:** `ruff check` (lint) + `ruff format` (format, replaces black/isort) + `mypy` (BE); `eslint` + `prettier` + `tsc` (FE).
- **commit-msg:** conventional-commit linter.
- **pre-push:** unit tests on changed packages (best-effort, fast).

Hooks may not be bypassed by default.

---

## 12. Reviewing Assistant Suggestions

When the assistant suggests a git command, the user reviewer should check:

- Identity is correct (`git config user.name && git config user.email`).
- Scope of staged files matches the described change.
- No secret or large binary slipped in.
- Commit message follows convention.
- Target branch is correct.

If anything is off, **deny** and ask the assistant to revise.
