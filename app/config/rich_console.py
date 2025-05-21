from rich.markdown import Markdown
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from contextlib import contextmanager

console = Console()
class RichPrinter:
    def __init__(self, console: Console = None):
        self.console = console or Console()
    def info_string(self,message: str) -> None:
        console.print(f"ℹ️ [bold blue]{message}[/bold blue]")

    def warning_string(self,message: str) -> None:
        console.print(f"⚠️ [bold yellow]{message}[/bold yellow]")

    def error_string(self,message: str) -> None:
        console.print(f"🚨 [bold red]{message}[/bold red]")

    def success_string(self,message: str) -> None:
        console.print(f"✅ [bold green]{message}[/bold green]")

    def title_string(self,title: str) -> None:
        console.print(Rule(f"[bold cyan]{title}[/bold cyan]"))

    def panel_string(self,title: str, body: str, style: str = "magenta") -> None:
        console.print(Panel(body, title=title, title_align="left", style=style))

    def divider(self,char: str = "─") -> None:
        console.print(char * console.width)

    def highlight_string(self,message: str, color: str = "bright_magenta") -> None:
        console.print(f"[{color}]{message}[/{color}]")

    def model_selection_result(self,model: str) -> None:
        console.print(f"\n🤖 [bold magenta]Selected model:[/bold magenta] [italic]{model}[/italic]")

    def step_info(self,message: str) -> None:
        console.print(f"\n[bold cyan]⏩ {message}[/bold cyan]")

    def print_package_installation_start(self):
        console.print("📦 [bold]Installing requirements.txt packages...[/bold]", style="yellow")

    def print_package_installation_success(self):
        console.print("✅ [green]requirements.txt packages installed[/green]")

    def print_failed_tests_header(self,attempt: int):
        console.print(f"⚠️ [yellow]Tests had issues in attempt {attempt}:[/yellow]")

    def print_failed_test(self,name: str, error_message: str):
        console.print(f"  [red]{name} FAILED[/red]")
        console.print(Markdown(f"  ```\n  {error_message.strip()}\n  ```"))

    def print_test_appended_path(self,path: str):
        console.print(f"✅ [bold green]Test code appended to[/bold green] [italic]{path}[/italic]")

    def section_divider(self,title: str = "") -> None:
        if title:
            console.print(Rule(f"[bold green]{title}[/bold green]"))
        else:
            console.print(Rule(style="green"))

    @contextmanager
    def loading(self,message: str = "Loading..."):
        with console.status(f"[bold cyan]{message}[/bold cyan]", spinner="aesthetic"):
            yield

rich_console = RichPrinter()