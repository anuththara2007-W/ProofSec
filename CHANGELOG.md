# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Productization Release
### Added
- **Python SDK**: `ProofSec` client class for programmatic evaluation.
- **Web Dashboard**: Modern, glassmorphic UI for evaluating scenarios and viewing history.
- **HTTP API**: Versioned REST API with `/api/v1/evaluate`, `/api/v1/health`, etc.
- **Rate Limiting**: Basic in-memory rate limiting for the local API.
- **CLI Subcommands**: `proofsec serve`, `proofsec benchmark`, `proofsec research`.
- **Docker Support**: `Dockerfile` and `docker-compose.yml`.
- **OpenAPI Specification**: `docs/openapi.yaml`.

### Changed
- Replaced legacy standalone scripts (`api.py`, `evaluate.py`) with integrated CLI architecture.
- Enforced strict separation between Custom User Evaluations and the Frozen Research Benchmark.

## [Research Benchmark v0.2]
- 110-task frozen benchmark.
- Evidence-grounded evaluation schemas.
- KaggleProvider integration.
