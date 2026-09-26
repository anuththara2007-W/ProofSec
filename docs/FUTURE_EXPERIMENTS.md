# Future Experiments

This document records the exact continuation path for completing the ProofSec multi-model campaign once external infrastructure constraints are resolved.

1. **Restore valid external credentials**: Obtain a valid Kaggle/OpenAI-compatible environment token.
2. **Verify backend**: Safely test connectivity without burning the full benchmark queue.
3. **Resume Gemini 3.5 Flash**: Run `python scripts/run_benchmark.py --model gemini-3.5-flash --resume` to natively identify the 88 completed tasks and launch precisely the remaining 22.
4. **Complete remaining 22 tasks**: Validate execution into `results/raw/gemini-3.5-flash`.
5. **Execute Gemini 2.5 Pro**: Run `python scripts/run_benchmark.py --model gemini-2.5-pro --fresh`.
6. **Execute Claude if genuinely supported**: Run `python scripts/run_benchmark.py --model claude-3-5-sonnet-20240620 --fresh`.
7. **Execute GPT-4o if genuinely supported**: Run `python scripts/run_benchmark.py --model gpt-4o --fresh`.
8. **Recalculate all metrics**: Execute `upgrade_metrics.py` to synthesize PVR and pairing data.
9. **Recalculate statistical intervals**: Execute `evaluation/statistics.py` to generate complete `statistics.json` bounds for all models.
10. **Perform cross-model analysis**: Generate a cross-model profile contrasting Accuracy vs PVR vs Terminology across the major providers.
11. **Freeze final experiment**: Lock the full dataset outputs as the definitive ProofSec Phase 3 repository asset.
