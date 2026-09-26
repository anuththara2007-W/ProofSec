# Threats to Validity

## Internal Validity

- **Task Construction**: ProofSec scenarios are synthetically constructed to isolate variables (One-Fact-Flips). However, they represent abstracted code snippets and logs, not fully compiling monolithic repositories.
- **Prompt Effects**: Zero-shot prompting with strict schema constraints may degrade standard LLM reasoning output depending on their instruction-tuning distributions.
- **Provider Behavior**: External backends (e.g. Kaggle/OpenAI proxies) have rate limits, opaque filtering, or transient network timeouts that can unevenly truncate executions.
- **Parsing**: Standard Pydantic schema extraction is used. Unusually structured responses might occasionally trigger fallback parsing logic, resulting in discarded outputs.

## External Validity

- **Evaluated Models**: Currently restricted to models exposed through specific supported backends.
- **Benchmark Size**: 110 tasks is highly specific but limits raw statistical power compared to 10k-sample leaderboards.
- **Domain Limits**: Primarily tests authorization logic, IDORs, weak configurations, and generic web application patterns rather than binary exploitation or cryptography.

## Statistical Validity

- **Partial Observations**: Executions blocked by external infrastructure (e.g., Gemini-3.5-Flash halted at 88 tasks) yield subgroup calculations with higher variance.
- **Subgroup Metrics**: Terminology Sensitivity (10 tasks) provides signal but cannot rule out small effects.
- **Uncertainty Estimates**: Bootstrap intervals correctly propagate sample size variance but assume the selected benchmark tasks represent an unbiased sample of general security scenarios (which is inherently impossible).

## Reproducibility

- **External Dependency**: Reproducibility requires a valid API token and backend availability, both subject to external vendor deprecation or failure.
- **Stochasticity**: While LLMs are configured to `temperature=0.0` where possible, true determinism is rarely guaranteed across commercial model backends.

## Construct Validity

- **Vulnerability vs Security Reasoning**: ProofSec does *not* claim to measure if an LLM is a "good hacker." It explicitly measures *evidence-sensitive deductive judgment*. An LLM might be technically capable of writing an exploit yet still fail ProofSec due to prematurely declaring Vulnerability on weak evidence.
