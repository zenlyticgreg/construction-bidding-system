"""
Main CLI application for PACE.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.logging import get_module_logger
from ..core.config import settings
from ..services.project_service import ProjectService
from ..models.project import ProjectType, ProjectStatus

app = typer.Typer(
    name="pace",
    help="PACE - Project Analysis & Construction Estimating",
    add_completion=False,
)
console = Console()
logger = get_module_logger("cli.main")


@app.command()
def version():
    """Show PACE version."""
    console.print(f"[bold blue]PACE[/bold blue] version [bold]{settings.version}[/bold]")


@app.command()
def init():
    """Initialize PACE application."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing PACE...", total=None)
        
        # Create necessary directories
        for directory in [settings.data_dir, settings.logs_dir, settings.file.upload_dir, settings.file.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        progress.update(task, description="PACE initialized successfully!")
    
    console.print("[bold green]✓[/bold green] PACE application initialized successfully!")


@app.command()
def projects(
    list_all: bool = typer.Option(False, "--all", "-a", help="List all projects"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by project type"),
    agency: Optional[str] = typer.Option(None, "--agency", help="Filter by agency"),
):
    """Manage projects."""
    project_service = ProjectService()
    
    if list_all:
        projects = project_service.get_all_projects()
    elif status:
        try:
            status_enum = ProjectStatus(status.lower())
            projects = project_service.get_projects_by_status(status_enum)
        except ValueError:
            console.print(f"[red]Invalid status: {status}[/red]")
            raise typer.Exit(1)
    elif type:
        try:
            type_enum = ProjectType(type.lower())
            projects = project_service.get_projects_by_type(type_enum)
        except ValueError:
            console.print(f"[red]Invalid project type: {type}[/red]")
            raise typer.Exit(1)
    elif agency:
        projects = project_service.get_projects_by_agency(agency)
    else:
        projects = project_service.get_all_projects()
    
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return
    
    table = Table(title="Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Type", style="green")
    table.add_column("Agency", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Created", style="dim")
    
    for project in projects:
        table.add_row(
            project.id[:8] + "...",
            project.name,
            project.project_type.value,
            project.agency,
            project.status.value,
            project.created_at.strftime("%Y-%m-%d"),
        )
    
    console.print(table)


@app.command()
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    project_type: str = typer.Option(..., "--type", "-t", help="Project type"),
    agency: str = typer.Option(..., "--agency", "-a", help="Agency name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Project location"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b", help="Project budget"),
):
    """Create a new project."""
    try:
        type_enum = ProjectType(project_type.lower())
    except ValueError:
        console.print(f"[red]Invalid project type: {project_type}[/red]")
        console.print(f"Valid types: {', '.join(t.value for t in ProjectType)}")
        raise typer.Exit(1)
    
    project_service = ProjectService()
    project = project_service.create_project(
        name=name,
        project_type=type_enum,
        agency=agency,
        description=description,
        location=location,
        budget=budget,
    )
    
    console.print(f"[bold green]✓[/bold green] Created project: {project.name} (ID: {project.id})")


@app.command()
def analyze(
    project_id: str = typer.Argument(..., help="Project ID"),
    file_path: Path = typer.Argument(..., help="PDF file to analyze"),
):
    """Analyze a project specification PDF."""
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold blue]Analyzing[/bold blue] {file_path} for project {project_id}...")
    
    # TODO: Implement PDF analysis
    console.print("[yellow]PDF analysis not yet implemented[/yellow]")


@app.command()
def generate_bid(
    project_id: str = typer.Argument(..., help="Project ID"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate a bid for a project."""
    project_service = ProjectService()
    project = project_service.get_project(project_id)
    
    if not project:
        console.print(f"[red]Project not found: {project_id}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold blue]Generating bid[/bold blue] for project: {project.name}")
    
    # TODO: Implement bid generation
    console.print("[yellow]Bid generation not yet implemented[/yellow]")


@app.command()
def stats():
    """Show PACE statistics."""
    project_service = ProjectService()
    stats = project_service.get_project_statistics()
    
    table = Table(title="PACE Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="green")
    
    table.add_row("Total Projects", str(stats["total_projects"]))
    table.add_row("Active Projects", str(stats["active_projects"]))
    table.add_row("Completed Projects", str(stats["completed_projects"]))
    
    console.print(table)
    
    # Project types breakdown
    if stats["projects_by_type"]:
        type_table = Table(title="Projects by Type")
        type_table.add_column("Type", style="bold")
        type_table.add_column("Count", style="green")
        
        for project_type, count in stats["projects_by_type"].items():
            if count > 0:
                type_table.add_row(project_type.title(), str(count))
        
        console.print(type_table)


@app.command()
def config():
    """Show current configuration."""
    table = Table(title="PACE Configuration")
    table.add_column("Setting", style="bold")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", settings.environment)
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Data Directory", str(settings.data_dir))
    table.add_row("Logs Directory", str(settings.logs_dir))
    table.add_row("Default Agency", settings.agency.default_agency)
    
    console.print(table)


if __name__ == "__main__":
    app() 