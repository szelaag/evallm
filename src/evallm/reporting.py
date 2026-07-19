from rich.console import Console
from rich.table import Table, box

from evallm.models import SuiteResult


console = Console()


def get_color(percent: float) -> str:
    """
    Returns rich supported color name based on percent

    Args:
        percent: 0.0 <= float <= 1.0 on which the colour is returned

    Returns:
        "green3" for 1.0\n
        "yellow2" for greater then 0.75\n
        "orange_red1" for greater then 0.3\n
        "bright_red" for 0.0\n

    """
    if percent == 1.0:
        return "bright_green"
    elif percent > 0.75:
        return "chartreuse2"
    elif percent > 0.3:
        return "orange_red1"
    else:
        return "bright_red"


def get_progress_bar(percent: float, color: str | None = None, width: int = 12) -> str:
    """Returns colored progress bar string"""
    full = round(percent * width)
    if not color:
        color = get_color(percent)
    progress_bar = f"[{color}]▰[/]" * full + "[dim]▱[/]" * (width - full)
    return f"{progress_bar}"


def show_suite_results(suite_results: list[SuiteResult]) -> None:
    """Shows rich table of suite results"""
    console.print()
    for suite_result in suite_results:
        color = get_color(suite_result.pass_rate)
        progress_bar = get_progress_bar(suite_result.pass_rate, color, width=12)
        console.rule(
            f"Suite:[bold] {suite_result.name}[/] [bold {color}]{suite_result.passed_count}[dim] / [/]{suite_result.total}[/] {progress_bar}",
            characters="━",
            style="grey37",
            align="left",
        )
        table = Table(header_style="bold", box=box.SIMPLE_HEAVY)
        table.add_column("ID", style="dim", justify="center")
        table.add_column("Result", style="bold", justify="center")
        table.add_column("Expected", style="", justify="center")
        table.add_column("Actual", style="", justify="center")
        for case_result in suite_result.cases:
            result = (
                f"[{get_color(1.0)}]PASS[/]"
                if case_result.eval_result.passed
                else f"[{get_color(0.0)}]FAIL[/]"
            )
            table.add_row(
                case_result.id, result, case_result.expected, case_result.actual
            )
        console.print(table)


def show_message(message: str) -> None:
    """Takes the message and prints it
    Args:
        Str with rich formating
    """
    console.print()
    console.print(message)
