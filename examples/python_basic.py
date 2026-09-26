import os
from proofsec import ProofSec

# Initialize client using the mock provider for testing
# In production, set PROOFSEC_PROVIDER="openai_compatible" and provide your API key.
os.environ["PROOFSEC_PROVIDER"] = "mock"

client = ProofSec()

# Check health
health = client.health()
print(f"Provider Status: {health.provider} is {health.status.name}")

# Evaluate a scenario
print("\nEvaluating Scenario...")
result = client.evaluate(
    scenario="The application concats user input into a SQL query.",
    evidence=["Database returns syntax error near quote", "Sleep payload delays response by 10s"]
)

print(f"Classification: {result.classification}")
print(f"Evidence State: {result.evidence_state}")
print(f"Reasoning: {result.reasoning}")

# Revise with more evidence
print("\nRevising Evaluation...")
revised = client.revise(
    evaluation_id=result.evaluation_id,
    evidence=["WAF blocked the payload."]
)

print(f"New Classification: {revised.classification}")
print(f"New Evidence State: {revised.evidence_state}")
print(f"Previous ID: {revised.previous_evaluation_id}")
