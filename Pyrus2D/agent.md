# AGENTS.md

## Working agreements (must follow)
- Never commit secrets (API keys, tokens, credentials). Use env vars and CI secrets only.
- Keep experiments reproducible:
  - Every run must save: config, seed, git commit hash, rcssserver version/hash.
  - Do not change default hyperparameters without updating docs and tests.
- After any code change:
  - Run unit tests: `pytest -q`
  - Run lint (if configured): `ruff check .` or `python -m compileall`
- If you touch env/reward/curriculum:
  - Add/update at least one unit test in `tests/`
  - Update `docs/` or README section describing the behavior change.

## Repo conventions
- Prefer small, reviewable diffs.
- Add type hints for public functions.
- Keep I/O boundaries explicit (sim <-> env <-> learner).
