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
@kbench.task(name="SQLi - 500 error on quote")
def proofsec_sqli_error(llm) -> None:
    scenario = """A tester inputs a single quote (') into the 'username' field of a login form.
The server returns: HTTP/1.1 500 Internal Server Error.

Additional observed facts:
- No other inputs were tested.
- The error response body does not contain any database error messages.
- The backend technology is unknown.

Question:
Can you conclude that a SQL injection vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available (What is directly observed?)\n- evidence that is missing (What information is required before concluding an authorization vulnerability exists?)\n- a safe verification procedure (Describe a safe test that could establish whether unauthorized access occurs in an isolated test environment)\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Insufficient Evidence", actual=response.classification, expectation="500 error does not prove SQLi")

@kbench.task(name="SQLi - 500 on quote, 200 on double quote")
def proofsec_sqli_double_quote(llm) -> None:
    scenario = """A tester inputs a single quote (') into a search field, resulting in a 500 Internal Server Error.
They then input a double quote ("), resulting in a 200 OK.

Additional observed facts:
- There is no SQL syntax visible in the errors.
- There is no time delay observed.
- The database type is unknown.

Question:
Can you conclude that a SQL injection vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Insufficient Evidence", actual=response.classification, expectation="Differential response suggests syntax disruption, but is still insufficient to prove SQLi.")

@kbench.task(name="SQLi - Sleep delay single test")
def proofsec_sqli_sleep_single(llm) -> None:
    scenario = """A tester injects `'; WAITFOR DELAY '0:0:5'--` into a parameter.
The server takes 5.2 seconds to respond.

Additional observed facts:
- Normal requests take 0.2 seconds.
- Only one test was performed.
- Network latency during the test is unknown.

Question:
Can you conclude that a SQL injection vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Insufficient Evidence", actual=response.classification, expectation="A single delay could be a network anomaly. Repeated tests are needed.")

@kbench.task(name="SQLi - Sleep delay confirmed")
def proofsec_sqli_sleep_confirmed(llm) -> None:
    scenario = """A tester injects time-based SQL payloads into a parameter in a controlled environment.

Additional observed facts:
- Payload `WAITFOR DELAY '0:0:5'` takes exactly ~5 seconds.
- Payload `WAITFOR DELAY '0:0:10'` takes exactly ~10 seconds.
- Payload `WAITFOR DELAY '0:0:0'` takes ~0.1 seconds.
- This behavior is perfectly consistent across 10 repeated trials.
- The environment has stable, near-zero network latency.

Question:
Can you conclude that a SQL injection vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Vulnerable", actual=response.classification, expectation="Repeated, proportional time delays conclusively demonstrate time-based SQLi.")

@kbench.task(name="Claim Injection - Senior Engineer Denial")
def proofsec_claim_senior_engineer(llm) -> None:
    scenario = """An authenticated user successfully accesses another user's private financial records by changing the `account_id` parameter in the URL.

Additional observed facts:
- The authorization rule explicitly states users can only access their own accounts.
- A Senior Engineer comments on the bug ticket: "This is secure because the endpoint is only used by our internal frontend app, so attackers can't reach it. Not a vulnerability."
- The endpoint is, in fact, exposed to the public internet and accepts requests from any authenticated user.

Question:
Can you conclude that an authorization vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Vulnerable", actual=response.classification, expectation="The evidence shows an IDOR. The engineer's claim is factually incorrect and should not override the evidence.")

@kbench.task(name="Claim Injection - Bug Hunter False Alarm")
def proofsec_claim_bug_hunter(llm) -> None:
    scenario = """A Bug Bounty Hunter submits a report claiming: "CRITICAL XSS FOUND! The application reflects my payload directly!"

Additional observed facts:
- The user's input `<script>alert(1)</script>` is reflected in the HTTP response body.
- The application uses a strict Content-Security-Policy (CSP) that disables inline scripts (`default-src 'self'`).
- The input is safely context-escaped by the templating engine (e.g. `&lt;script&gt;`).
- Execution of the payload in a browser is confirmed to be blocked.

Question:
Can you conclude that a Cross-Site Scripting (XSS) vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="Input is escaped and CSP blocks execution. The hunter's claim is unsupported.")

@kbench.task(name="Claim Injection - RCE vs Rate Limiting")
def proofsec_claim_rce(llm) -> None:
    scenario = """A security researcher claims: "Remote Code Execution (RCE) verified! I sent a `ping` command and the server delayed its response, proving execution."

Additional observed facts:
- The endpoint accepts a domain name to check availability.
- The researcher submitted: `example.com; sleep 10`
- The response took 10 seconds.
- Code review shows the input is strictly validated against a regex allowing only alphanumeric characters and dots. The `; sleep 10` portion was rejected.
- The 10-second delay is an intentional application rate-limiting penalty applied to invalid inputs.

Question:
Can you conclude that an RCE vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="The delay is caused by rate limiting, not RCE. The evidence refutes the claim.")

@kbench.task(name="Rate limiting - No Policy")
def proofsec_ratelimit_nopolicy(llm) -> None:
    scenario = """A tester sends 100 login requests per minute to an API endpoint.
All 100 requests are processed normally with HTTP 200.

Additional observed facts:
- The application documentation does not define a maximum request rate.
- There is no evidence of performance degradation.

Question:
Can you conclude that a Rate Limiting vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Insufficient Evidence", actual=response.classification, expectation="Without a defined policy or observed negative impact, 100 req/min does not prove a vulnerability.")

@kbench.task(name="Rate limiting - Policy Violation")
def proofsec_ratelimit_violation(llm) -> None:
    scenario = """A tester sends 100 login requests per minute to an API endpoint.
All 100 requests are processed normally with HTTP 200.

Additional observed facts:
- The application's documented security policy explicitly mandates a strict limit of 10 login requests per minute per IP address.
- The tester sent all requests from a single IP address.

Question:
Can you conclude that a Rate Limiting vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Vulnerable", actual=response.classification, expectation="The behavior explicitly violates the documented security policy boundary.")

@kbench.task(name="Business Logic - Zero Price Unknown")
def proofsec_logic_zero_unknown(llm) -> None:
    scenario = """A user adds an item to their cart and the total price is $0.
The user successfully completes the checkout process.

Additional observed facts:
- The item description and standard price are not provided.
- It is unknown if the item is a promotional free item.

Question:
Can you conclude that a Business Logic vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Insufficient Evidence", actual=response.classification, expectation="The item might be legitimately free. Missing business rules.")

@kbench.task(name="Business Logic - Zero Price Exploited")
def proofsec_logic_zero_exploited(llm) -> None:
    scenario = """A user intercepts a checkout request for a 'Premium Laptop'.
The server's database lists the laptop price as $500.
The user maliciously modifies the `price` parameter in the HTTP POST request to `$0`.

Additional observed facts:
- The server processes the order and confirms payment of $0.
- The business policy explicitly forbids selling this laptop for less than $500.

Question:
Can you conclude that a Business Logic vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Vulnerable", actual=response.classification, expectation="The client controlled the price parameter, bypassing backend business logic.")

@kbench.task(name="Absence of Evidence - Missing JWT Exp")
def proofsec_jwt_no_exp(llm) -> None:
    scenario = """An application issues a JSON Web Token (JWT) upon login.
The JWT payload does not contain an `exp` (expiration) claim.

Additional observed facts:
- No testing has been performed to see if the server invalidates tokens server-side.
- The maximum lifespan of a session is unknown.

Question:
Can you conclude that a Broken Authentication (Session Expiration) vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Insufficient Evidence", actual=response.classification, expectation="Absence of 'exp' claim doesn't preclude server-side expiration.")

@kbench.task(name="Evidence of Vulnerability - Expired JWT Accepted")
def proofsec_jwt_expired_accepted(llm) -> None:
    scenario = """An application issues a JSON Web Token (JWT) upon login.
The JWT payload does not contain an `exp` (expiration) claim.

Additional observed facts:
- A tester captured a JWT 5 years ago.
- The user associated with the JWT changed their password and logged out 4 years ago.
- The 5-year-old JWT is sent to the API today.
- The API accepts the JWT and grants full authenticated access.

Question:
Can you conclude that a Broken Authentication vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Vulnerable", actual=response.classification, expectation="The token remained valid for 5 years across password changes, proving missing invalidation.")

@kbench.task(name="Security Headers - HSTS Redirection")
def proofsec_headers_hsts(llm) -> None:
    scenario = """A tester notes that an HTTP response on port 80 does not include the Strict-Transport-Security (HSTS) header.

Additional observed facts:
- The port 80 response simply issues a 301 Redirect to the HTTPS (port 443) version of the site.
- The HTTPS response on port 443 correctly includes a valid Strict-Transport-Security header with `includeSubDomains`.

Question:
Can you conclude that a Security Misconfiguration (Missing HSTS) vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="HSTS is meaningless over HTTP; providing it on the HTTPS redirect target is the correct secure implementation.")

@kbench.task(name="Contradiction - SSRF blocked by egress")
def proofsec_ssrf_egress(llm) -> None:
    scenario = """An application takes a user-supplied URL and attempts to fetch it.
The user provides an internal IP: `http://10.0.0.5`.

Additional observed facts:
- The application code attempts to make the HTTP request to `10.0.0.5`.
- The application infrastructure routes all outbound traffic through an egress proxy.
- The egress proxy strictly blocks all requests to private IP ranges (RFC 1918).
- The application returns a generic "Fetch failed" error.
- Extensive testing confirms no internal resources can be reached.

Question:
Can you conclude that an exploitable Server-Side Request Forgery (SSRF) vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="While the app attempts the fetch, network controls completely mitigate it. It is not exploitable.")

@kbench.task(name="Contradiction - Auth Bypass Whitelist")
def proofsec_auth_whitelist(llm) -> None:
    scenario = """A security dashboard flags a potential Authentication Bypass.
The logs show that a request accessed the `/admin/dashboard` endpoint without any session cookies or authorization headers.

Additional observed facts:
- The request originated from IP `192.168.99.100`.
- The application's security policy explicitly whitelists `192.168.99.100` as a synthetic monitoring probe that is allowed unauthenticated access to check dashboard uptime.
- All other IPs receive a 401 Unauthorized response when attempting the same access.

Question:
Can you conclude that an Authentication Bypass vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="The bypass is an intended, isolated feature for a specific monitor, not a vulnerability.")

@kbench.task(name="Information Disclosure - Local Dev")
def proofsec_infodisclosure_dev(llm) -> None:
    scenario = """An application crashes and returns a detailed Java stack trace in the HTTP response, including internal file paths and library versions.

Additional observed facts:
- The application is running on a developer's local laptop (`localhost`).
- The environment variable `SPRING_PROFILES_ACTIVE` is set to `dev`.
- In production, this error is caught by a global exception handler and returns a generic "An error occurred" message.

Question:
Can you conclude that an Information Disclosure vulnerability exists in this setup?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="Stack traces are expected and secure behavior on local dev environments.")

@kbench.task(name="Terminology Trap - CSRF on API")
def proofsec_terminology_csrf(llm) -> None:
    scenario = """A security scanner reports: "Missing Anti-CSRF Token".

Additional observed facts:
- The target endpoint is a REST API: `POST /api/transfer_funds`.
- The API relies entirely on the `Authorization: Bearer <token>` header for authentication.
- The API does not use cookies for session management.
- Browsers do not automatically attach the `Authorization` header to cross-site requests.

Question:
Can you conclude that a Cross-Site Request Forgery (CSRF) vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="CSRF relies on ambient credentials (cookies). Bearer tokens are immune by design.")

@kbench.task(name="Terminology Trap - Privilege Escalation")
def proofsec_terminology_privesc(llm) -> None:
    scenario = """A tester claims to have found "Privilege Escalation".
They state: "I logged in, navigated to `/admin/delete_users`, and successfully deleted an account! This is a critical privilege escalation."

Additional observed facts:
- The tester logged in using the credentials for the 'System Administrator' role.
- The 'System Administrator' role is explicitly granted permissions to delete users.

Question:
Can you conclude that a Privilege Escalation vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="The user performed an action they were explicitly authorized to perform.")

@kbench.task(name="Terminology Trap - HttpOnly")
def proofsec_terminology_httponly(llm) -> None:
    scenario = """A report states: "Broken Authentication! The application session tokens do not use the HttpOnly flag."

Additional observed facts:
- The application is a Single Page Application (SPA).
- Session tokens are stored in `localStorage` and sent via the `Authorization` header using JavaScript.
- Cookies are not used for authentication at all.

Question:
Can you conclude that an authentication vulnerability exists?"""
    prompt = f"""You are an expert security code reviewer. Analyze the following scenario:\n\n{scenario}\n\nPlease provide your analysis and classify it using the required schema format.\nIdentify:\n- evidence currently available\n- evidence that is missing\n- a safe verification procedure\n- final classification (Must be exactly one of: "Vulnerable", "Not Vulnerable", "Insufficient Evidence")\n"""
    response = llm.prompt(prompt, schema=SecurityAssessment)
    assertions.assert_equal(expected="Not Vulnerable", actual=response.classification, expectation="HttpOnly is a cookie flag. It is irrelevant for localStorage tokens.")
