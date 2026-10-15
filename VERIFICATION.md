# FIREWATCH v8.0.0 Verification Record

Release target: `FIREWATCH-WebSec-Agent-v8.0.0`  
Verification date: `2026-10-13`  
Test command: `python -m pytest tests -q -x --tb=short` (from `backend/`, with `PYTHONPATH=.`)  
Coverage command: eight balanced shards using `pytest-cov`, appending to one combined coverage dataset.

## Results measured in the build environment

- **4,995 / 4,995 collected pytest cases passed** across **52 test modules**; the complete non-instrumented run reached 100% with zero failures, errors, or skips.
- The entire same suite was then run under coverage in **8 separate balanced shards**. Every shard passed. Combined `backend/app` statement coverage measured **85.29%** (1,623 covered statements out of 1,903 statements); the combined report passed the 80% minimum.
- The v8 test matrix and machine-readable manifest were generated from pytest collection: [`docs/TEST_MATRIX_V8.md`](docs/TEST_MATRIX_V8.md) and [`docs/TEST_MANIFEST_V8.json`](docs/TEST_MANIFEST_V8.json).
- The 79-case target assessment plan was exported to [`docs/assessment-plan-v8.json`](docs/assessment-plan-v8.json), [`docs/assessment-plan-v8.csv`](docs/assessment-plan-v8.csv), and [`docs/ASSESSMENT_CATALOG.md`](docs/ASSESSMENT_CATALOG.md).
- Python compilation of scripts, application, tests and demo target succeeded. Dashboard JavaScript syntax validation, publisher shell syntax, Docker Compose YAML parsing and repository hygiene are checked by the release verifier.

## Reproduce locally

```bash
python -m pip install -r backend/requirements-dev.txt
python scripts/verify_release.py
```

Or run the suite without coverage instrumentation:

```bash
cd backend
PYTHONPATH=. python -m pytest tests -q -rA
```

Combined coverage gate:

```bash
python scripts/run_coverage_shards.py --shards 8 --min-coverage 80
```

## Not executed or requiring external verification

- **Bandit and `pip-audit`:** not installed in the local build environment; not run.
- **Docker image build/deployment:** Docker CLI/Engine unavailable; only Compose YAML syntax is checked locally.
- **Hosted GitHub Actions and CodeQL:** not run against the user's GitHub repository. These require publishing the repository and observing hosted results.
- **Live ZAP assessment and production-browser journey coverage:** not claimed as verified by these software tests. Playwright tests with mocked browser objects do not prove a Chromium install or deployment is healthy.
- **Publishing:** this archive has not been pushed to the user's GitHub account from this environment.

## Security coverage limitations

The separate 79-case assessment catalog marks manual workflows, test-account checks and specialist-tool cases explicitly. This version does not claim to automatically prove every vulnerability class. Business-logic flaws, BOLA/IDOR, exploitable injection, authorization failures, multi-step workflows and deployment/egress risks may require dedicated test fixtures and human review. Regression tests and a clean test run do not prove that a scanned target is secure. Scope validation should be paired with an outbound firewall/proxy policy because URL validation and DNS checks alone are not a complete network-isolation boundary. See [`docs/SECURITY_COVERAGE.md`](docs/SECURITY_COVERAGE.md) and [`SECURITY.md`](SECURITY.md).
