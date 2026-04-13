# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-13

### Added
- Initial Optivue scaffold across backend, frontend, infra, and docs.
- Cost intelligence adapters, recommendation scoring, governance approval flow, and action adapters.
- Core frontend pages/components for analyst, engineering, leadership, and chat experiences.
- CDK stacks and reusable constructs for infrastructure provisioning.
- Unit/integration/eval test baselines and DynamoDB seed tooling.
- `pyproject.toml` for backend with pytest-asyncio 0.24+ auto mode and ruff/mypy config.
- `.env.deploy.example` deployment environment variable template (safe to commit).
- `scripts/deploy/phase8-go-live.ps1` — Windows PowerShell deployment runbook with `-ZeroBudget`, `-SkipSmokeTests`, and `-SkipCognitoUsers` flags.
- `scripts/deploy/phase8-go-live.cmd` — CMD launcher for the PS1 runbook.
- `UpdateActionState` Lambda invoke step added to Step Functions workflow chain.
- Phase 8 deployment documentation in `docs/04-delivery/05-copilot-build-prompts.md`.

### Fixed
- pytest-asyncio 0.23.x collection crash (`AttributeError: 'Package' object has no attribute 'obj'`) — upgraded to `>=0.24.0`.
- `_build_recommendation` in `adapters/optimization/recommendations.py` now accepts both camelCase AWS API fields (`estimatedMonthlySavings`, `effort`, `risk`) and snake_case fixture fields (`estimated_monthly_savings`, `effort_level`, `risk_level`), ensuring P1 priority tier is computed correctly from fixture data.
- Eval `has_fields` check now handles semantic body-level fields (`recommendations`, `idle_resources`) correctly instead of treating them as per-recommendation dict keys.
- `bearerScheme` renamed to `bearer_scheme` in `auth_service.py` (ruff naming convention).
- `ApprovalRequestBody.approver_role` renamed to `environment` to match approval matrix semantics.
- `FinOpsApi` Lambda local asset bundling on Windows now copies backend sources with Node `fs.cpSync` filtering instead of `xcopy /EXCLUDE`, preventing false Docker fallback during `cdk synth` when Docker is unavailable.

### Changed
- All `datetime.timezone.utc` usages modernised to `datetime.UTC` (Python 3.11+ preferred form) across all adapter modules.
- `Optional[X]` type hints modernised to `X | None` (PEP 604) in all model files; unused `typing.Optional` imports removed.
- `requirements-dev.txt` pinned `pytest-asyncio>=0.24.0`.

### Validated (Phase 8 local gates — zero AWS spend)
- 26/26 backend unit tests pass (`pytest tests/unit/ -q`).
- CDK synth clean for all 6 stacks: `FinOpsFoundation`, `FinOpsData`, `FinOpsAgent`, `FinOpsApi`, `FinOpsWorkflow`, `FinOpsFrontend`.
- Agent eval gates: Safety 10/10 (100%), P1 Recall 8/8 (100%) — `DEMO_MODE=true`.
- Consolidated local rerun completed cleanly: frontend `vitest` 2/2, infra `jest` 9/9, backend `ruff` clean, backend `mypy` clean, backend unit tests 26/26, and backend eval gates Safety 10/10 + P1 Recall 8/8.


