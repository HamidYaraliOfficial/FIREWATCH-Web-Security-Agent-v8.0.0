# FIREWATCH Web Security Agent v8.0.0

FIREWATCH v8 is a security-hardening and test-quality release. It expands boundary and adversarial matrices and tightens request input, authorization metadata, header construction, URL normalization and recursive evidence redaction.

## Highlights

- Strict request header validation: RFC token header names, case-insensitive duplicate rejection, value/control-character limits, transport-sensitive header exclusions, and validation before a scan can be queued.
- Earlier target URL refusal for URL user-info and credential-like query parameters; stricter root-target and discovery URL checks.
- Scheme-aware allow-list policy for explicitly declared additional hosts; case-insensitive exclusion checks; robust rejection of disallowed IP classes, including reserved/multicast ranges.
- Bounded multi-layer redaction for nested redirect/return/next URLs, and preserved benign values in redaction property matrices.
- Expanded tests for API discovery/OpenAPI security declarations/GraphQL classification, crawler/parser edge cases, exact-origin credential isolation, encrypted credential storage, safe report sinks, report schema contracts and low-impact HTTP policy.
- Generated v8 test inventory and 79-case assessment catalog kept distinct from one another.
- Release automation supports balanced test shards so combined coverage can be measured under constrained execution environments.

## Verification summary

- **4,995 / 4,995 tests passed**, across **52 test modules**, with zero failures/errors/skips in the complete regression run.
- **85.29% combined statement coverage** for `backend/app`, above the 80% minimum, measured by running the same test suite in eight coverage shards and combining coverage data.
- ZIP integrity, release metadata, generated inventories and source hygiene are checked before packaging.

These are software quality metrics, not vulnerability-detection rates. Bandit, `pip-audit`, Docker image builds and hosted GitHub/CodeQL execution were unavailable in the build environment and remain unverified. See [`VERIFICATION.md`](VERIFICATION.md) for details.
