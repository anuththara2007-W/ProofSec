# Contributing to ProofSec

We love your input! We want to make contributing to ProofSec as easy and transparent as possible, whether it's:
- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Development Process
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes (`python -m unittest discover tests`).
5. Ensure you have not modified the frozen benchmark (`proofsec benchmark hash`).

## The Frozen Benchmark
ProofSec relies on an immutable dataset found in `tasks/`. 
**Do not submit Pull Requests that modify `tasks/` or `results/raw/`**. The integrity of the benchmark (hash `422501a4db...`) is critical for historical comparison.

If you believe a task is flawed, please open an Issue labeled `benchmark-errata`. Do not modify the JSON files directly.

## Adding a Provider
To add a new model provider:
1. Implement the `ModelProvider` interface in `src/proofsec/providers.py`.
2. Add it to the provider discovery logic.
3. Write a test case (if applicable, though do not commit real credentials).
4. Update `docs/PROVIDERS.md`.

## Code Style
Please follow PEP 8 guidelines. Keep the dependencies minimal.
