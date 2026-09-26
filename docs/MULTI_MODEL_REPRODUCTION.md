# ProofSec Multi-Model Reproduction Guide

To run a multi-model campaign locally:

1. **Integrity Check**
   ```bash
   python evaluation/verify_frozen_benchmark.py
   ```

2. **Execute Multi-Model Run**
   ```bash
   python scripts/run_benchmark.py --all-models --fresh
   ```

3. **Resume Failed Model Execution**
   ```bash
   python scripts/run_benchmark.py --model gemini-3.5-flash --resume
   ```

4. **Generate Metrics (Including PVR)**
   ```bash
   python scratch/upgrade_metrics.py
   ```

5. **Run Statistical Analysis**
   ```bash
   python evaluation/statistics.py
   ```

6. **Generate Reports**
   ```bash
   python scripts/generate_report.py
   python evaluation/analyze_surprises.py
   ```
