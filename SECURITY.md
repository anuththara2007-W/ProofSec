# Security Policy

## Supported Versions

Only the latest `main` branch and tagged releases are supported with security updates.

## Reporting a Vulnerability

If you discover a security vulnerability within ProofSec, please do not disclose it publicly. 

Instead, open a GitHub Issue with the label `security` (if the repository provides a private reporting feature) or contact the maintainers directly.

### Known Architectural Boundaries
ProofSec handles untrusted input (User Scenarios, Evidence). We treat all user input as **DATA**.
The prompt generation explicitly uses structural boundaries (e.g., `USER-PROVIDED SCENARIO`) to prevent Prompt Injection from affecting the System Instructions.

If you find a bypass that causes the model to ignore the `SYSTEM/DEVELOPER EVALUATION INSTRUCTIONS` block and execute user-provided commands, this is considered a critical boundary failure and should be reported.

### Out of Scope
- Denial of Service against the local HTTP server (`proofsec serve`), as it is meant for local developer use, not exposed to the public internet by default.
- Phishing/social engineering.
