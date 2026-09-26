# ProofSec Developer Platform

ProofSec is an evidence-grounded AI evaluation platform for security reasoning. This is the productized version (Phase 9) that provides a robust API, interactive web dashboard, and CLI tool, transforming the core research benchmark into a developer-ready evaluation engine.

## Features

- **Frozen Research Benchmark (v0.2)**: 110 immutably hashed tasks for reliable historical comparisons.
- **Provider-Neutral SDK & CLI**: Evaluate custom scenarios securely without polluting the core benchmark.
- **Evidence Revision System**: Iteratively refine evaluations without overwriting history.
- **Local API & Web Dashboard**: A fully local HTTP API supporting standard operations, with a modern, glassmorphic UI.
- **Docker Ready**: Run the entire stack effortlessly with Docker Compose.
- **Strict Data Isolation**: Guarantees separation of Custom Evaluations from Research Data.

## Quick Start

### 1. Using Python / CLI
Ensure you have Python 3.12+ installed.
```bash
pip install -r requirements.txt
pip install -e .

# Evaluate a scenario
proofsec evaluate --file my_scenario.json

# Check provider health
proofsec health

# Start the local API server & Web Dashboard
proofsec serve --port 8000
```

### 2. Using Docker
```bash
docker-compose up -d
```
Access the web dashboard at: `http://localhost:8000`

## Developer Modes

### Standard (Productization)
Use `proofsec evaluate` and `proofsec serve` to run custom evaluations and view the dashboard. All evaluations are safely stored in `custom_evaluations/`.

### Researcher Mode
Analyze the immutable frozen benchmark results:
```bash
proofsec benchmark hash
proofsec benchmark status
proofsec research metrics
```

## API Specification
See `docs/openapi.yaml` for the full OpenAPI 3.0 specification.
