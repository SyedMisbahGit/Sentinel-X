import os
import sys
from rich.console import Console

console = Console()

REQUIRED_DIRS = ["config", "core", "modules", "data", "output", "data/wordlists", "data/sessions"]
REQUIRED_FILES = [
    "arbiter.py", 
    "config/settings.yaml", 
    "core/target.py",
    "modules/email.py", 
    "modules/recon.py", 
    "modules/ports.py",
    "modules/cortex.py"
]

def verify():
    console.print("[bold blue]Checking ARBITER Configuration...[/bold blue]")
    missing = False

    for d in REQUIRED_DIRS:
        if not os.path.exists(d):
            console.print(f"[red]❌ Missing Directory: {d}[/red]")
            missing = True
        else:
            console.print(f"[green]✔ Found Directory: {d}[/green]")

    for f in REQUIRED_FILES:
        if not os.path.exists(f):
            console.print(f"[red]❌ Missing File: {f}[/red]")
            missing = True
        else:
            console.print(f"[green]✔ Found File: {f}[/green]")

    if missing:
        console.print("\n[bold red]System Config Improper. Please fix missing files.[/bold red]")
        sys.exit(1)
    else:
        console.print("\n[bold green]ALL SYSTEMS NOMINAL. ARBITER IS READY.[/bold green]")

if __name__ == "__main__":
    verify()
