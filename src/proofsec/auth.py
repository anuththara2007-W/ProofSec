import os
import subprocess
from rich.console import Console

console = Console()

def handle_auth_kaggle():
    console.print("[bold]Kaggle Authentication[/bold]")
    
    # Check if kaggle CLI is installed
    try:
        res = subprocess.run(["kaggle", "--version"], capture_output=True, text=True)
        if res.returncode == 0:
            console.print("✓ Kaggle CLI detected")
        else:
            console.print("✗ Kaggle CLI not found. Install with `pip install kaggle`.")
            return
    except FileNotFoundError:
        console.print("✗ Kaggle CLI not found. Install with `pip install kaggle`.")
        return

    # Check authentication
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if os.path.exists(kaggle_json) or (os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY")):
        console.print("✓ Kaggle authentication detected")
        # Could read username here if we wanted to parse JSON, but we shouldn't log secrets
        import json
        try:
            with open(kaggle_json, 'r') as f:
                creds = json.load(f)
                username = creds.get('username', 'unknown')
                console.print(f"✓ Kaggle account: {username}")
        except Exception:
            pass
        
        # Test benchmark access implicitly if possible, or just print ready
        console.print("✓ Provider ready")
        console.print("\nRun:\n    proofsec benchmark status")
    else:
        console.print("✗ Kaggle authentication required\n")
        console.print("To authenticate:")
        console.print("1. Go to https://www.kaggle.com/settings in your browser.")
        console.print("2. Click 'Create New Token' to download kaggle.json.")
        console.print("3. Place kaggle.json in ~/.kaggle/ (or C:\\Users\\<User>\\.kaggle\\ on Windows).")
        console.print("4. Ensure the file has restricted permissions (chmod 600 ~/.kaggle/kaggle.json).")`n        console.print("Alternatively, set the KAGGLE_USERNAME and KAGGLE_KEY environment variables.")
        console.print("\nThen retry.")

def handle_auth_status():
    from proofsec.providers import provider_manager
    console.print("[bold]Authentication Status[/bold]")
    for name, provider_cls in provider_manager.list_providers().items():
        provider = provider_cls()
        caps = provider.get_capabilities()
        auth_status = caps.get("authentication", "unknown")
        color = "green" if auth_status in ["authenticated", "API key", "none"] else "red"
        console.print(f"Provider: [bold]{name}[/bold]")
        console.print(f"Status: [{color}]{auth_status}[/{color}]\n")

