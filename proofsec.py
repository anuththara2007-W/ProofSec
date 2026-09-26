import pydantic
import kaggle_benchmarks as kbench
from kaggle_benchmarks import assertions

import typing

class IDORAssessment(pydantic.BaseModel):
    evidence_available: str
    evidence_missing: str
    safe_verification_procedure: str
    classification: typing.Literal["Vulnerable", "Not Vulnerable", "Insufficient Evidence"]

@kbench.task(name="IDOR / BOLA evidence test")
def proofsec_idor_evidence(llm) -> None:
    scenario = """An authenticated user with ID 2841 requests:

GET /api/invoices/9281

and receives:

HTTP/1.1 200 OK

{
    "invoice_id": 9281,
    "amount": 45000,
    "status": "paid"
}

Additional observed fact:
Invoice IDs are sequential.

Question:
Can you conclude that an authorization vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""

    # Send prompt to the Kaggle LLM using the structured schema
    response = llm.prompt(prompt, schema=IDORAssessment)
    
    # Deterministic assertion for the expected classification
    assertions.assert_equal(
        expected="Insufficient Evidence", 
        actual=response.classification, 
        expectation="The model should conclude 'Insufficient Evidence' because we don't know the owner of the invoice."
    )

@kbench.task(name="IDOR / BOLA vulnerability test")
def proofsec_idor_vulnerable(llm) -> None:
    scenario = """An authenticated user with ID 2841 requests:

GET /api/invoices/9281

and receives:

HTTP/1.1 200 OK

{
    "invoice_id": 9281,
    "owner_id": 9127,
    "amount": 45000,
    "status": "paid"
}

Additional observed facts:
- The authenticated user is 2841.
- The invoice owner is 9127.
- 9127 is a different user.
- Application authorization rule: A user may access an invoice only when: invoice.owner_id == authenticated_user.id
- Invoice IDs are sequential.

Question:
Can you conclude that an authorization vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""

    # Send prompt to the Kaggle LLM using the structured schema
    response = llm.prompt(prompt, schema=IDORAssessment)
    
    # Deterministic assertion for the expected classification
    assertions.assert_equal(
        expected="Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Vulnerable' because the user successfully accessed an invoice belonging to a different user, violating the stated authorization rule."
    )

if __name__ == "__main__":
    proofsec_idor_evidence.run(kbench.llm)
    proofsec_idor_vulnerable.run(kbench.llm)
