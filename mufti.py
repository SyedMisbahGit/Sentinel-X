import typer
import yaml
import sys
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from core.target import Target

# Import All Modules
from modules.recon import run_recon
from modules.permutations import run_permutations
from modules.ports import run_ports
from modules.probing import run_probing
from modules.cloud import run_cloud
from modules.email import run_email
from modules.takeover import run_takeover # NEW
from modules.cortex import run_cortex
from modules.offensive import run_offensive
from modules.mining import run_mining
from modules.chaos import run_chaos
from modules.report import run_report

# Setup Logging
logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True, markup=True)])
log = logging.getLogger("rich")
console = Console()
app = typer.Typer(help="MUFTI: The Supreme Security Auditor")

def load_config():
    try:
        with open("config/settings.yaml", "r") as f: return yaml.safe_load(f)
    except: sys.exit(1)

CONFIG = load_config()

BANNER = """
[bold white]
███╗   ███╗██╗   ██╗███████╗████████╗██╗
████╗ ████║██║   ██║██╔════╝╚══██╔══╝██║
██╔████╔██║██║   ██║█████╗     ██║   ██║
██║╚██╔╝██║██║   ██║██╔══╝     ██║   ██║
██║ ╚═╝ ██║╚██████╔╝██║        ██║   ██║
╚═╝     ╚═╝ ╚═════╝ ╚═╝        ╚═╝   ╚═╝
[/bold white][bold red]THE VERDICT IS FINAL.[/bold red]
"""

@app.callback()
def main(): pass

@app.command()
def scan(target: str = typer.Argument(...), mode: str = typer.Option("stealth", "--mode", "-m"), resume: bool = typer.Option(False, "--resume", "-r")):
    console.print(Align.center(BANNER))
    console.print(Panel.fit(f"[bold cyan]MUFTI v{CONFIG['global']['version']}[/bold cyan]\n[yellow]Target:[/yellow] {target}\n[yellow]Mode:[/yellow] {mode.upper()}"))

    session = Target.load(target) if resume and Target.load(target) else Target(domain=target, mode=mode)
    session.save()

    try:
        if "recon" not in session.completed_phases:
            run_recon(session, CONFIG)
            session.completed_phases.append("recon")
            session.save()
            
        if "ports" not in session.completed_phases:
            run_ports(session, CONFIG)
            session.completed_phases.append("ports")
            session.save()

        if "permutations" not in session.completed_phases:
            run_permutations(session, CONFIG)
            session.completed_phases.append("permutations")
            session.save()

        if "probing" not in session.completed_phases:
            run_probing(session, CONFIG)
            session.completed_phases.append("probing")
            session.save()
            
        # v1.8: The Seizure (Takeover)
        if "takeover" not in session.completed_phases:
            run_takeover(session, CONFIG)
            session.completed_phases.append("takeover")
            session.save()

        if "cloud" not in session.completed_phases:
            run_cloud(session, CONFIG)
            session.completed_phases.append("cloud")
            session.save()

        if "email" not in session.completed_phases:
            run_email(session, CONFIG)
            session.completed_phases.append("email")
            session.save()

        if "cortex" not in session.completed_phases:
            run_cortex(session, CONFIG)
            session.completed_phases.append("cortex")
            session.save()

        if "offensive" not in session.completed_phases:
            run_offensive(session, CONFIG)
            session.completed_phases.append("offensive")
            session.save()
            
        if "mining" not in session.completed_phases:
            run_mining(session, CONFIG)
            session.completed_phases.append("mining")
            session.save()

        if "chaos" not in session.completed_phases:
            run_chaos(session, CONFIG)
            session.completed_phases.append("chaos")
            session.save()

        run_report(session, CONFIG)
        console.print(f"[bold green][+] The Verdict has been issued.[/bold green]")

    except KeyboardInterrupt:
        session.save()
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Critical Error: {e}[/red]")
        session.save()
        sys.exit(1)

if __name__ == "__main__":
    app()
