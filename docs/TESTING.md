# Testing Guide — FIREWATCH v8.0.0

The v8 regression suite collects **4,995 pytest cases across 52 test modules**. The complete run passed all 4,995 cases with zero failures, errors, or skips. Coverage was run across eight balanced shards and combined to **85.29% statement coverage** for `backend/app`, exceeding the 80% release floor.

These numbers measure tests and coverage of FIREWATCH's own code. They are not a vulnerability-detection rate and do not prove that a target application is secure.

## Install and run

From the repository root:

```bash
python -m pip install -r backend/requirements-dev.txt
python scripts/build_test_manifest.py
python scripts/run_coverage_shards.py --shards 8 --min-coverage 80
```

To run all tests without coverage instrumentation (typically faster):

```bash
cd backend
PYTHONPATH=. python -m pytest tests -q -rA
```

To inspect a specific module:

```bash
cd backend
PYTHONPATH=. python -m pytest tests/test_v8_scope_fuzz_and_normalization.py -q
```

## What is covered

The 52 modules include legacy unit and API checks; a local-only end-to-end demo scan; worker lifecycle and cancellation; scope/URL normalization; DNS and IP policy; transport and exact-origin credential isolation; recursive secret redaction; schema and header protocol boundaries; OpenAPI/GraphQL discovery; crawler and JavaScript route heuristics; authorization review candidates; safe, low-impact probe policy; report output sinks (HTML, Markdown, CSV, JSON and SARIF); risk arithmetic; encrypted credential storage; ZAP plan serialization; and API response contracts.

The generated module list and collected counts are in [`TEST_MATRIX_V8.md`](TEST_MATRIX_V8.md) and [`TEST_MANIFEST_V8.json`](TEST_MANIFEST_V8.json). The coverage script balances modules by collected test count and appends coverage data from each shard before enforcing the combined threshold.

## Release verification

```bash
python scripts/verify_release.py
```

This runs compilation and available frontend/shell/YAML/repository checks, regenerates catalogs, then runs the full test/coverage gate. Bandit, `pip-audit`, Docker Engine, Playwright's browser binary, ZAP, hosted GitHub Actions and CodeQL may require installation, network access or an external environment. The verifier marks unavailable optional tools as unverified; it does not call them successful.

## Software tests vs. target assessment

The separate assessment catalog tracks **79 planned target-assessment cases**: 22 passive automated observations, 13 automated review candidates requiring validation, 38 manual/test-account/workflow cases, and 6 specialist-tool-required checks. These are not 79 guaranteed automated exploits. Business logic, BOLA/IDOR, exploitable injection, role-specific behavior and production deployment risks may require a dedicated test application/account and human review.
