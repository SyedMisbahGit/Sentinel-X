import typer
import yaml
import sys
import logging
import shutil
import os
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Confirm
from core.target import Target

# Import Modules
from modules.recon import run_recon
from modules.permutations import run_permutations
from modules.ports import run_ports
from modules.probing import run_probing
from modules.cloud import run_cloud
from modules.email import run_email
from modules.takeover import run_takeover
from modules.cortex import run_cortex
from modules.offensive import run_offensive
from modules.mining import run_mining
from modules.chaos import run_chaos
from modules.report import run_report

# Setup Logging
logging.basicConfig(
    level="INFO", 
    format="%(message)s", 
    datefmt="[%X]", 
    handlers=[RichHandler(rich_tracebacks=True, markup=True, show_time=False)]
)
log = logging.getLogger("rich")
console = Console()

# Define App
app = typer.Typer(help="ARBITER: System Integrity Evaluator")

def load_config():
    try:
        with open("config/settings.yaml", "r") as f: return yaml.safe_load(f)
    except: sys.exit(1)

CONFIG = load_config()

BANNER = """
[bold cyan]
   ▄▄▄       ██▀███   ▄▄▄▄    ██▓▄▄▄█████▓▓█████  ██▀███  
  ▒████▄    ▓██ ▒ ██▒▓█████▄ ▓██▒▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
  ▒██  ▀█▄  ▓██ ░▄█ ▒▒██▒ ▄██▒██▒▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
  ░██▄▄▄▄██ ▒██▀▀█▄  ▒██░█▀  ░██░░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  
   ▓█   ▓██▒░██▓ ▒██▒░▓█  ▀█▓░██░  ▒██▒ ░ ░▒████▒░██▓ ▒██▒
   ▒▒   ▓▒█░░ ▒▓ ░▒▓░░▒▓███▀▒░▓    ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
    ▒   ▒▒ ░  ░▒ ░ ▒░▒░▒   ░  ▒ ░    ░     ░ ░  ░  ░▒ ░ ▒░
    ░   ▒     ░░   ░  ░    ░  ▒ ░  ░         ░     ░░   ░ 
        ░  ░   ░      ░       ░              ░  ░   ░     
                       ░                                  
[/bold cyan][bold white]SYSTEM INTEGRITY EVALUATOR // v2.0[/bold white]
"""

@app.callback()
def main(): pass

@app.command()
def scan(target: str = typer.Argument(...), mode: str = typer.Option("stealth", "--mode", "-m"), resume: bool = typer.Option(False, "--resume", "-r")):
    console.print(Align.center(BANNER))
    console.print(Panel.fit(f"[bold cyan]TARGET ACQUIRED:[/bold cyan] {target}\n[bold cyan]PROTOCOL:[/bold cyan] {mode.upper()}", border_style="cyan"))

    session = Target.load(target) if resume and Target.load(target) else Target(domain=target, mode=mode)
    session.save()

    try:
        phases = [
            ("recon", run_recon), ("ports", run_ports), ("permutations", run_permutations),
            ("probing", run_probing), ("takeover", run_takeover), ("cloud", run_cloud),
            ("email", run_email), ("cortex", run_cortex), ("offensive", run_offensive),
            ("mining", run_mining), ("chaos", run_chaos)
        ]

        for name, func in phases:
            if name not in session.completed_phases:
                func(session, CONFIG)
                session.completed_phases.append(name)
                session.save()

        run_report(session, CONFIG)
        console.print(f"[bold green]>> EVALUATION COMPLETE.[/bold green]")

        # --- NEW: INTERACTIVE SAVE PROMPT ---
        if Confirm.ask("[bold yellow]Do you want to SAVE the mission data locally?[/bold yellow]"):
            console.print(f"[green]✔ Data preserved in output/{target}[/green]")
        else:
            console.print(f"[red]! PURGING MISSION DATA...[/red]")
            output_dir = f"output/{target}"
            session_file = f"data/sessions/{target}.json"
            
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            if os.path.exists(session_file):
                os.remove(session_file)
                
            console.print(f"[red]✔ TRACE DELETED.[/red]")

    except KeyboardInterrupt:
        session.save()
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]SYSTEM FAILURE: {e}[/red]")
        session.save()
        sys.exit(1)

if __name__ == "__main__":
    app()
