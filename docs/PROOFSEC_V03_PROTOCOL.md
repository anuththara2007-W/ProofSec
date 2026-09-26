# ProofSec v0.3 Protocol

## Next-Generation Benchmark Research Protocol

ProofSec v0.3 introduces advanced evaluation of evidence-grounded security reasoning. It builds on v0.2 by introducing complex edge cases and methodological safeguards to prevent model gaming.

### 1. New Methodologies

#### 1.1 One-Fact-Flip Quality Control
Every paired task in v0.3 is rigorously validated to ensure that it differs from its counterpart by exactly one decisive fact. 
- Metadata required: `task_id`, `paired_task_id`, `changed_fact`, `unchanged_facts`, `expected_transition`.
- Automated scripts (`proofsec.research.validator`) verify the integrity of the pair.

#### 1.2 Evidence Ladders
We measure whether the model escalates its confidence proportionally as evidence increases across the ladder:
- Level 0: No meaningful evidence
- Level 1: Suspicious symptom
- Level 2: Strong indicator
- Level 3: Reproducible behavior
- Level 4: Authorization failure
- Level 5: Confirmed unauthorized impact

#### 1.3 Contradictory Evidence
Tasks intentionally pair strong vulnerability indicators with contradicting environmental or log evidence. The model must prioritize and resolve the contradiction without jumping to unsupported conclusions.

#### 1.4 Temporal Reasoning
Events are introduced chronologically (e.g., Before Patch, After Patch, Subsequent Configuration Change).

#### 1.5 Evidence Relevance (Irrelevance Sensitivity)
We introduce "noise" facts that look like vulnerabilities but do not constitute evidence for the specific scenario in question.

### 2. Experiment Lifecycle
Every execution must generate an `ExperimentManifest` detailing:
- Benchmark version and SHA256 Hash
- Model and Provider details
- Completion and failure statistics

Experiments can be replayed using `proofsec research replay <id>`.

### 3. Inter-Annotator Agreement
To validate ground truth in v0.3, tasks support human annotation schema. If multiple annotators are available, Cohen's Kappa and Krippendorff's Alpha will be calculated. If unavailable, statistics correctly report "UNAVAILABLE".
