import os
import subprocess
import json
from rich.console import Console

console = Console()

def get_kaggle_benchmark_slug() -> str:
    slug = os.environ.get("PROOFSEC_KAGGLE_BENCHMARK")
    if not slug:
        console.print("[red]Error: PROOFSEC_KAGGLE_BENCHMARK environment variable not set.[/red]")
        console.print("Please set it to the format <owner>/<benchmark> (e.g. proofsec/proofsec-v0.2).")
        raise ValueError("Missing PROOFSEC_KAGGLE_BENCHMARK")
    return slug

def check_benchmark_status():
    try:
        slug = get_kaggle_benchmark_slug()
    except ValueError:
        return
        
    console.print(f"[bold]Kaggle Benchmark[/bold]")
    console.print(f"Slug: {slug}")
    
    # We would use kaggle CLI to fetch details if it supported benchmarks directly
    # 'kaggle models instances versions' or similar. Since we don't know the exact kaggle CLI
    # command for custom benchmarks, we simulate the output structure as requested.
    
    res = subprocess.run(["kaggle", "--version"], capture_output=True, text=True)
    if res.returncode != 0:
        console.print("Authentication: [red]FAILED[/red] (Kaggle CLI not found)")
        return
        
    # Check auth
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_json):
        console.print("Authentication: [red]FAILED[/red] (Missing kaggle.json)")
        console.print("Leaderboard: [red]Unavailable[/red]")
        return
        
    console.print("Authentication: [green]READY[/green]")
    console.print("Benchmark access: [yellow]UNKNOWN[/yellow] (Requires Kaggle API endpoint)")
    console.print("Leaderboard: [yellow]Unavailable[/yellow]")

def download_benchmark_results():
    try:
        slug = get_kaggle_benchmark_slug()
    except ValueError:
        return
        
    console.print(f"Downloading results for {slug}...")
    
    # Actual implementation would be:
    # kaggle models download <slug> or similar to fetch results
    
    # For now we create the directory and simulate
    from proofsec.evaluator import get_project_root
    dest_dir = get_project_root() / "results" / "external" / "kaggle"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    provenance = {
      "source": "kaggle",
      "benchmark": slug,
      "downloaded_at": "unknown",
      "source_url": f"https://kaggle.com/models/{slug}",
      "sha256": "pending",
      "provider": "kaggle"
    }
    
    with open(dest_dir / "provenance.json", 'w') as f:
        json.dump(provenance, f, indent=2)
        
    console.print(f"[green]Results would be downloaded to {dest_dir}[/green]")
