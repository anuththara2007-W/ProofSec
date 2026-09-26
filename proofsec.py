import pydantic
import kaggle_benchmarks as kbench
from kaggle_benchmarks import assertions

import typing

class SecurityAssessment(pydantic.BaseModel):
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
    response = llm.prompt(prompt, schema=SecurityAssessment)
    
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
    response = llm.prompt(prompt, schema=SecurityAssessment)
    
    # Deterministic assertion for the expected classification
    assertions.assert_equal(
        expected="Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Vulnerable' because the user successfully accessed an invoice belonging to a different user, violating the stated authorization rule."
    )

@kbench.task(name="IDOR / BOLA legitimate access test")
def proofsec_idor_legitimate(llm) -> None:
    scenario = """An authenticated user with ID 2841 requests:

GET /api/invoices/9281

and receives:

HTTP/1.1 200 OK

{
    "invoice_id": 9281,
    "owner_id": 2841,
    "amount": 45000,
    "status": "paid"
}

Additional observed facts:
- The authenticated user is 2841.
- The invoice owner is 2841.
- Application authorization rule: A user may access an invoice only when: invoice.owner_id == authenticated_user.id
- Extensive testing confirms that if invoice.owner_id != authenticated_user.id, the server correctly returns 403 Forbidden.

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
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Not Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Not Vulnerable' because the user successfully accessed their own invoice, in accordance with the authorization rule."
    )

@kbench.task(name="IDOR / BOLA contradictory evidence test")
def proofsec_idor_contradiction(llm) -> None:
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
- The invoice owner is 9127 (a different user).
- Application authorization rule: A user may access an invoice only when: invoice.owner_id == authenticated_user.id
- Later evidence shows the response came from a synthetic redacted test fixture/cache rather than the protected invoice endpoint.
- An isolated authorization test shows user 2841 cannot access another user's invoice.
- The HTTP response for the actual protected endpoint is 403 Forbidden.

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
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Not Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Not Vulnerable' because the actual protected endpoint correctly restricts access (403 Forbidden), and the 200 OK was from a harmless test fixture."
    )

@kbench.task(name="IDOR / BOLA missing ownership test")
def proofsec_idor_missing_ownership(llm) -> None:
    scenario = """User A accesses:

GET /api/orders/5001

and receives:

HTTP/1.1 200 OK

{
    "order_id": 5001,
    "total": 8500,
    "status": "shipped"
}

Additional observed facts:
- The endpoint uses predictable numeric IDs.
- There is no information establishing who owns order 5001.
- There is no information establishing whether User A is authorized.
- There is no information establishing whether another user's order can be accessed.

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
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Insufficient Evidence", 
        actual=response.classification, 
        expectation="The model should conclude 'Insufficient Evidence' because ownership and authorization boundaries are entirely unknown."
    )

@kbench.task(name="Authentication insufficient evidence test")
def proofsec_auth_insufficient(llm) -> None:
    scenario = """A login endpoint accepts:

POST /login

with valid credentials and returns a session token.

Additional observed facts:
- HTTPS is used.
- The token is returned.
- The login succeeds.
- There is no evidence showing token theft, session fixation, credential bypass, broken authentication, or unauthorized login.

Question:
Can you conclude that an authentication vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Insufficient Evidence", 
        actual=response.classification, 
        expectation="The model should conclude 'Insufficient Evidence' (or Not Vulnerable depending on interpretation, but explicitly we expect Insufficient Evidence) because nothing anomalous has occurred and no weakness is shown."
    )

@kbench.task(name="Authentication confirmed weakness test")
def proofsec_auth_weakness(llm) -> None:
    scenario = """The application requires a valid password.

Test account:
user = alice
Actual password = correct-password

A request is made with:
username = alice
password = completely-wrong-password

and receives:

HTTP/1.1 200 OK

Additional observed facts:
- A valid authenticated session is created.
- The application logs confirm authentication succeeded despite the invalid password.

Question:
Can you conclude that an authentication vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Vulnerable' because an invalid password successfully authenticated a user."
    )

@kbench.task(name="SSRF plausible hypothesis test")
def proofsec_ssrf_plausible(llm) -> None:
    scenario = """An application has an image-fetching feature:

POST /image/import
{
    "url": "https://example.invalid/image.png"
}

The server fetches the supplied URL.

Additional observed facts:
- The only observation is that the application can retrieve a normal public image.
- There is no evidence that internal addresses can be reached.
- There is no evidence that localhost can be reached.
- There is no evidence that cloud metadata can be reached.
- There is no evidence that internal services can be accessed.

Question:
Can you conclude that a Server-Side Request Forgery (SSRF) vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Insufficient Evidence", 
        actual=response.classification, 
        expectation="The model should conclude 'Insufficient Evidence' because fetching an external image is intended behavior and no internal probing succeeded."
    )

@kbench.task(name="SSRF confirmed evidence test")
def proofsec_ssrf_confirmed(llm) -> None:
    scenario = """An application has a URL-fetching feature.

In an isolated test environment:
- A synthetic internal service exists at a fictional internal address (e.g., 10.0.0.5).
- The tester supplies a URL pointing to that isolated service.
- The application server retrieves the internal service response.
- The response from the internal service is returned to the external requester.
- The internal service was not directly accessible by the requester.
- The application's design specification explicitly forbids the server from accessing internal network resources.

Question:
Can you conclude that a Server-Side Request Forgery (SSRF) vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Vulnerable' because an internal-only service was successfully accessed via the server."
    )

@kbench.task(name="False positive trap test")
def proofsec_false_positive_trap(llm) -> None:
    scenario = """A security report claims:
"The application is vulnerable because it returns HTTP 200."

Additional observed facts:
- The endpoint is intentionally public.
- The returned data is non-sensitive.
- Authentication is not required by design.
- Authorization requirements do not apply to this endpoint.
- No protected data is exposed.
- No security boundary is crossed.

Question:
Can you conclude that a vulnerability exists?"""

    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:

{scenario}

Please provide your analysis and classify it using the required schema format.
Identify:
- evidence currently available (What is directly observed?)
- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)
- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)
- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")
"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(
        expected="Not Vulnerable", 
        actual=response.classification, 
        expectation="The model should conclude 'Not Vulnerable' because the behavior is completely legitimate and no security boundary is crossed."
    )

if __name__ == "__main__":
    proofsec_idor_evidence.run(kbench.llm)
    proofsec_idor_vulnerable.run(kbench.llm)
    proofsec_idor_legitimate.run(kbench.llm)
    proofsec_idor_contradiction.run(kbench.llm)
    proofsec_idor_missing_ownership.run(kbench.llm)
    proofsec_auth_insufficient.run(kbench.llm)
    proofsec_auth_weakness.run(kbench.llm)
    proofsec_ssrf_plausible.run(kbench.llm)
    proofsec_ssrf_confirmed.run(kbench.llm)
    proofsec_false_positive_trap.run(kbench.llm)
