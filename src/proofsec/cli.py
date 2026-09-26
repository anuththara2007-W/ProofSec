import argparse
import sys
import json
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from proofsec.client import ProofSec
from proofsec.schemas import CUSTOM_EVALUATION_VERSION
from proofsec.providers import get_provider, ProviderStatus

console = Console()

def evaluate_cmd(args):
    client = ProofSec(provider=args.provider)
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            scenario = data.get("scenario", "")
            evidence = data.get("evidence", [])
            context = data.get("context")
        except Exception as e:
            console.print(f"[red]Error loading file: {e}[/red]")
            sys.exit(1)
    else:
        console.print("[bold cyan]ProofSec Custom Evaluation[/bold cyan]\n")
        scenario = input("Scenario:\n> ")
        evidence_input = input("\nEvidence (comma separated, or leave blank):\n> ")
        evidence = [e.strip() for e in evidence_input.split(",")] if evidence_input else []
        context = input("\nAdditional context (optional):\n> ")

        if not args.json:
            confirm = input("\nEvaluate? [Y/n] ")
            if confirm.lower() not in ['', 'y', 'yes']:
                console.print("Aborted.")
                sys.exit(0)

    try:
        if not args.json:
            console.print("\n[yellow]Evaluating...[/yellow]\n")
        
        result = client.evaluate(
            scenario=scenario,
            evidence=evidence,
            context=context,
            save=args.save
        )
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]ERROR: {e}[/red]")
        sys.exit(1)

    if args.json:
        print(result.model_dump_json(indent=2))
        return

    # Rich terminal output
    console.print(Panel(
        f"[bold]Classification:[/bold] {result.classification}\n"
        f"[bold]Evidence State:[/bold] {result.evidence_state}\n"
        f"[bold]Summary:[/bold] {result.summary}\n\n"
        f"[bold]ID:[/bold] {result.evaluation_id}\n"
        f"[bold]Provider:[/bold] {result.provider} ({result.model})",
        title="ProofSec Result", expand=False
    ))
    
    if result.supporting_evidence:
        console.print("\n[bold green]Supporting Evidence:[/bold green]")
        for ev in result.supporting_evidence:
            console.print(f"  - {ev}")
            
    if result.missing_evidence:
        console.print("\n[bold yellow]Missing Evidence:[/bold yellow]")
        for ev in result.missing_evidence:
            console.print(f"  - {ev}")
            
    if result.contradicting_evidence:
        console.print("\n[bold red]Contradicting Evidence:[/bold red]")
        for ev in result.contradicting_evidence:
            console.print(f"  - {ev}")

    console.print(f"\n[bold]Reasoning:[/bold]\n{result.reasoning}")

def providers_cmd(args):
    # For now we list the known providers
    table = Table(title="ProofSec Providers")
    table.add_column("Provider ID", style="cyan")
    table.add_column("Description")
    
    table.add_row("kaggle", "Kaggle Models API (Requires authentication)")
    table.add_row("openai_compatible", "OpenAI /v1/chat/completions compatible endpoint")
    table.add_row("mock", "Local test fixture for deterministic testing")
    
    console.print(table)

def health_cmd(args):
    client = ProofSec(provider=args.provider)
    health = client.provider.health_check()
    
    if args.json:
        print(health.model_dump_json(indent=2))
        return
        
    color = "green" if health.status == ProviderStatus.AVAILABLE else "red"
    console.print(f"Provider: [bold]{health.provider}[/bold]")
    console.print(f"Model: {health.model}")
    console.print(f"Status: [{color}]{health.status.name}[/{color}]")

def version_cmd(args):
    console.print(f"ProofSec Custom Evaluation Version: {CUSTOM_EVALUATION_VERSION}")

def serve_cmd(args):
    from http.server import HTTPServer
    from proofsec.api import ProofSecAPIHandler
    
    port = args.port
    console.print(f"[bold green]Starting ProofSec API on port {port}...[/bold green]")
    server = HTTPServer((args.host, port), ProofSecAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\nShutting down server...")
        server.server_close()

def main():
    parser = argparse.ArgumentParser(description="ProofSec Evaluation Platform CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a security scenario")
    eval_parser.add_argument("--file", type=str, help="Path to JSON request file")
    eval_parser.add_argument("--provider", type=str, help="Model provider", default=None)
    eval_parser.add_argument("--json", action="store_true", help="Output JSON instead of rich text")
    eval_parser.add_argument("--save", action="store_true", default=True, help="Save evaluation locally (default true)")
    
    # providers command
    prov_parser = subparsers.add_parser("providers", help="List available model providers")
    
    # health command
    health_parser = subparsers.add_parser("health", help="Check provider health")
    health_parser.add_argument("--provider", type=str, help="Model provider", default=None)
    health_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    # serve command
    serve_parser = subparsers.add_parser("serve", help="Run the ProofSec API server")
    serve_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    # version command
    subparsers.add_parser("version", help="Show version info")
    
    # We will add history, revise, schema, benchmark later...

    args = parser.parse_args()

    if args.command == "evaluate":
        evaluate_cmd(args)
    elif args.command == "providers":
        providers_cmd(args)
    elif args.command == "health":
        health_cmd(args)
    elif args.command == "version":
        version_cmd(args)
    elif args.command == "serve":
        serve_cmd(args)

if __name__ == "__main__":
    main()
