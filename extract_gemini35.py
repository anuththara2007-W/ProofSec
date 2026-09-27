import ast
import json
from pathlib import Path


# ============================================================
# ProofSec — Gemini 3.5 Kaggle Result Extraction
# ============================================================

ROOT = Path.cwd()

TASK_FILE = (
    ROOT
    / "kaggle"
    / "tasks"
    / "proofsec_v0_2.py"
)

ATIF_FILE = (
    ROOT
    / "proofsec-v0-2"
    / "4"
    / "gemini-3.5-flash"
    / "3261606"
    / "proofsec-v0-2-run_id_Run_1_google_gemini-3.5-flash.atif.json"
)

OUT_DIR = (
    ROOT
    / "results"
    / "raw"
    / "gemini-3.5-flash_kaggle"
)

VALID_CLASSES = {
    "Vulnerable",
    "Not Vulnerable",
    "Insufficient Evidence",
}


# ============================================================
# Load canonical ProofSec tasks
# ============================================================

def load_canonical_tasks():
    text = TASK_FILE.read_text(encoding="utf-8")
    tree = ast.parse(text)

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "ALL_TASKS_JSON"
            ):
                raw = ast.literal_eval(node.value)

                if not isinstance(raw, str):
                    raise RuntimeError(
                        "ALL_TASKS_JSON is not a JSON string."
                    )

                tasks = json.loads(raw)

                if not isinstance(tasks, list):
                    raise RuntimeError(
                        "Decoded ALL_TASKS_JSON is not a list."
                    )

                return tasks

    raise RuntimeError(
        "Could not find ALL_TASKS_JSON in canonical task file."
    )


# ============================================================
# Decode Gemini response
# ============================================================

def decode_message(message):
    """
    Gemini ATIF agent messages are strings.

    Expected structured response contains:
        classification

    Handles:
      - JSON object
      - double-encoded JSON
      - plain text containing a valid classification
    """

    if isinstance(message, dict):
        return message

    if not isinstance(message, str):
        return {}

    text = message.strip()

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:
        obj = json.loads(text)

        # Handle double-encoded JSON
        if isinstance(obj, str):
            try:
                obj = json.loads(obj)
            except Exception:
                pass

        if isinstance(obj, dict):
            return obj

    except Exception:
        pass

    # --------------------------------------------------------
    # Fallback: classification text
    # --------------------------------------------------------

    for classification in [
        "Insufficient Evidence",
        "Not Vulnerable",
        "Vulnerable",
    ]:
        if classification.lower() in text.lower():
            return {
                "classification": classification
            }

    return {}


# ============================================================
# ATIF source
# ============================================================

def get_source(step):
    source = step.get("source")

    if isinstance(source, str):
        return source.lower()

    return ""


# ============================================================
# Main extraction
# ============================================================

def main():

    print("=" * 70)
    print("ProofSec — Gemini 3.5 Kaggle Result Extraction")
    print("=" * 70)
    print()

    print("Canonical task file:")
    print(TASK_FILE)
    print()

    print("ATIF run:")
    print(ATIF_FILE)
    print()

    print("Output directory:")
    print(OUT_DIR)
    print()

    # ========================================================
    # Validate input paths
    # ========================================================

    if not TASK_FILE.exists():
        raise FileNotFoundError(
            f"Canonical task file not found:\n{TASK_FILE}"
        )

    if not ATIF_FILE.exists():
        raise FileNotFoundError(
            f"ATIF file not found:\n{ATIF_FILE}"
        )

    # ========================================================
    # Load benchmark
    # ========================================================

    tasks = load_canonical_tasks()

    print(f"Canonical tasks: {len(tasks)}")

    if len(tasks) != 110:
        raise RuntimeError(
            f"Expected 110 canonical tasks, found {len(tasks)}"
        )

    # Verify canonical task IDs are unique
    canonical_ids = [task["id"] for task in tasks]

    if len(canonical_ids) != len(set(canonical_ids)):
        raise RuntimeError(
            "Canonical benchmark contains duplicate task IDs."
        )

    # ========================================================
    # Load ATIF
    # ========================================================

    with ATIF_FILE.open("r", encoding="utf-8") as f:
        atif = json.load(f)

    steps = atif.get("steps", [])

    print(f"ATIF steps: {len(steps)}")

    if len(steps) != 220:
        raise RuntimeError(
            f"Expected 220 ATIF steps, found {len(steps)}"
        )

    # ========================================================
    # Identify user / agent steps
    # ========================================================

    user_steps = [
        step
        for step in steps
        if get_source(step) == "user"
    ]

    agent_steps = [
        step
        for step in steps
        if get_source(step) == "agent"
    ]

    print(f"User steps: {len(user_steps)}")
    print(f"Agent steps: {len(agent_steps)}")

    if len(user_steps) != 110:
        raise RuntimeError(
            f"Expected 110 user steps, found {len(user_steps)}"
        )

    if len(agent_steps) != 110:
        raise RuntimeError(
            f"Expected 110 agent steps, found {len(agent_steps)}"
        )

    # ========================================================
    # Verify alternating ATIF structure
    # ========================================================

    for i, step in enumerate(steps):
        expected_source = (
            "user"
            if i % 2 == 0
            else "agent"
        )

        actual_source = get_source(step)

        if actual_source != expected_source:
            raise RuntimeError(
                f"ATIF ordering problem at index {i}: "
                f"expected {expected_source}, "
                f"found {actual_source}"
            )

    print()
    print("ATIF alternating user/agent structure: VERIFIED")

    # ========================================================
    # Verify step IDs
    # ========================================================

    user_ids = [
        step["step_id"]
        for step in user_steps
    ]

    agent_ids = [
        step["step_id"]
        for step in agent_steps
    ]

    print()
    print("First 5 user step IDs :", user_ids[:5])
    print("First 5 agent step IDs:", agent_ids[:5])
    print("Last user step ID     :", user_ids[-1])
    print("Last agent step ID    :", agent_ids[-1])

    # ========================================================
    # Prepare clean output directory
    # ========================================================

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # IMPORTANT:
    # Only clean the dedicated Gemini 3.5 Kaggle directory.
    # The old contaminated directory remains untouched.

    for file in OUT_DIR.glob("*.json"):
        file.unlink()

    # ========================================================
    # Extract all 110 results
    # ========================================================

    written_ids = []

    print()
    print("-" * 70)

    for index, (task, agent_step) in enumerate(
        zip(tasks, agent_steps),
        start=1
    ):

        task_id = task["id"]

        # ----------------------------------------------------
        # Ground truth is:
        # task["ground_truth"]["classification"]
        # ----------------------------------------------------

        try:
            expected = task["ground_truth"]["classification"]
        except (KeyError, TypeError):
            raise RuntimeError(
                f"Missing ground_truth.classification "
                f"for {task_id}"
            )

        if expected not in VALID_CLASSES:
            raise RuntimeError(
                f"Invalid ground truth for {task_id}: "
                f"{expected}"
            )

        # ----------------------------------------------------
        # Gemini response
        # ----------------------------------------------------

        message = agent_step.get("message")

        parsed = decode_message(message)

        classification = parsed.get("classification")

        if classification not in VALID_CLASSES:
            raise RuntimeError(
                f"Could not parse valid classification "
                f"for {task_id}\n\n"
                f"Agent step: {agent_step.get('step_id')}\n\n"
                f"Message:\n{message}"
            )

        # ----------------------------------------------------
        # Calculate correctness from canonical ground truth
        # ----------------------------------------------------

        correct = (
            classification == expected
        )

        # ----------------------------------------------------
        # Task metadata
        # ----------------------------------------------------

        evidence_state = task.get(
            "evidence_state"
        )

        task_family = task.get(
            "task_family"
        )

        category = task.get(
            "category"
        )

        experiment = task.get(
            "experiment",
            "migrated_baseline"
        )

        # ----------------------------------------------------
        # Result object
        # ----------------------------------------------------

        result = {
            "benchmark_version": "0.2.0",
            "task_id": task_id,
            "model": "gemini-3.5-flash",

            "classification": classification,
            "expected_classification": expected,
            "correct": correct,

            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0,

            "evidence_state": evidence_state,
            "task_family": task_family,
            "experiment": experiment,
            "category": category,

            "response": {
                "classification": classification
            },
        }

        output_file = (
            OUT_DIR
            / f"{task_id}.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                result,
                f,
                indent=2,
                ensure_ascii=False
            )

        written_ids.append(task_id)

        print(
            f"{index:03d} | "
            f"{classification:<22} | "
            f"expected: {expected:<22} | "
            f"{'CORRECT' if correct else 'WRONG'}"
        )

    # ========================================================
    # Strong validation
    # ========================================================

    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    result_files = list(
        OUT_DIR.glob("*.json")
    )

    result_ids = []

    correct_count = 0

    classification_counts = {
        "Vulnerable": 0,
        "Not Vulnerable": 0,
        "Insufficient Evidence": 0,
    }

    for file in result_files:

        with file.open(
            "r",
            encoding="utf-8"
        ) as f:
            result = json.load(f)

        task_id = result.get("task_id")

        result_ids.append(task_id)

        # Validate required fields
        required_fields = [
            "benchmark_version",
            "task_id",
            "model",
            "classification",
            "expected_classification",
            "correct",
            "evidence_state",
            "task_family",
            "experiment",
            "category",
        ]

        for field in required_fields:
            if field not in result:
                raise RuntimeError(
                    f"Missing field '{field}' "
                    f"in {file.name}"
                )

        # Validate classification
        if result["classification"] not in VALID_CLASSES:
            raise RuntimeError(
                f"Invalid classification in {file.name}"
            )

        if result["expected_classification"] not in VALID_CLASSES:
            raise RuntimeError(
                f"Invalid expected classification "
                f"in {file.name}"
            )

        # Validate correctness
        calculated_correct = (
            result["classification"]
            == result["expected_classification"]
        )

        if result["correct"] != calculated_correct:
            raise RuntimeError(
                f"Incorrect 'correct' flag in "
                f"{file.name}"
            )

        if result["correct"]:
            correct_count += 1

        classification_counts[
            result["classification"]
        ] += 1

    unique_result_ids = set(result_ids)
    expected_id_set = set(canonical_ids)

    missing = (
        expected_id_set
        - unique_result_ids
    )

    unexpected = (
        unique_result_ids
        - expected_id_set
    )

    duplicates = (
        len(result_ids)
        - len(unique_result_ids)
    )

    print(
        f"Files written      : "
        f"{len(result_files)}"
    )

    print(
        f"Unique task IDs    : "
        f"{len(unique_result_ids)}"
    )

    print(
        f"Duplicate IDs      : "
        f"{duplicates}"
    )

    print(
        f"Missing task IDs   : "
        f"{len(missing)}"
    )

    print(
        f"Unexpected IDs     : "
        f"{len(unexpected)}"
    )

    print()
    print("Classification counts:")

    for classification, count in (
        classification_counts.items()
    ):
        print(
            f"  {classification:<22}: "
            f"{count}"
        )

    print()
    print(
        f"Correct predictions: "
        f"{correct_count}/110"
    )

    accuracy = (
        correct_count / 110
    )

    print(
        f"Accuracy: "
        f"{accuracy:.4%}"
    )

    # ========================================================
    # Final hard checks
    # ========================================================

    if len(result_files) != 110:
        raise RuntimeError(
            "VALIDATION FAILED: "
            f"Expected 110 files, found "
            f"{len(result_files)}"
        )

    if len(unique_result_ids) != 110:
        raise RuntimeError(
            "VALIDATION FAILED: "
            "Expected 110 unique task IDs."
        )

    if duplicates != 0:
        raise RuntimeError(
            "VALIDATION FAILED: "
            "Duplicate task IDs detected."
        )

    if missing:
        raise RuntimeError(
            "VALIDATION FAILED: "
            f"Missing IDs: {sorted(missing)}"
        )

    if unexpected:
        raise RuntimeError(
            "VALIDATION FAILED: "
            f"Unexpected IDs: {sorted(unexpected)}"
        )

    if correct_count == 0:
        raise RuntimeError(
            "VALIDATION FAILED: "
            "0 correct results. "
            "Ground-truth mapping should be inspected."
        )

    print()
    print("=" * 70)
    print("SUCCESS")
    print("=" * 70)
    print(
        "110 clean Gemini 3.5 results extracted "
        "and internally verified."
    )
    print()
    print(
        "Ground truth source:"
    )
    print(
        "task['ground_truth']['classification']"
    )
    print()
    print(
        "Old contaminated directory was NOT modified."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()