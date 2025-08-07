from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
import time
from horse import Horse
from simulation import race_stream


def visualise_race_result(horses, distance, seed=None, tick_delay=0.05):
    console = Console()
    progress = Progress(
        TextColumn("[bold blue]{task.fields[name]}", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.completed:.1f}m"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )

    with progress:
        task_ids = {
            h.name: progress.add_task("", name=h.name, total=distance) for h in horses
        }
        gen = race_stream(horses, distance=distance, seed=seed)
        while True:
            try:
                _tick, positions = next(gen)
                for h in horses:
                    task = progress.tasks[task_ids[h.name]]
                    current = task.completed
                    advance = max(0, min(positions[h.name], distance) - current)
                    progress.update(task_ids[h.name], advance=advance)
                time.sleep(tick_delay)
            except StopIteration as e:
                summary = e.value
                break

    console.print(
        f"\n[bold yellow]Track:[/] {summary['track_condition']}  "
        f"[bold yellow]Moods:[/] {summary['moods']}"
    )
    print_finish_table(summary)
    return summary


def print_finish_table(race):
    console = Console()
    order = race["order"]
    times = race["times"]
    # Compute margins (distance deltas at finish)
    positions = race["positions"]
    first_dist = positions[order[0]]
    margins = {n: max(0.0, first_dist - positions[n]) for n in order}

    t = Table(title="Finish Order")
    t.add_column("#", justify="right")
    t.add_column("Horse")
    t.add_column("Time (ticks)", justify="right")
    t.add_column("Margin (m)", justify="right")

    for i, name in enumerate(order, 1):
        t.add_row(str(i), name, str(times[name]), f"{margins[name]:.1f}")
    console.print(Panel(t, title="🏁 Results"))


def to_fractional(decimal_odds, max_den=16):
    """Approximate decimal odds to a nice fractional string (profit-only part)."""
    profit = max(decimal_odds - 1, 0.01)
    # best rational approx
    best = (1, 1, abs(1 / 1 - profit))
    for d in range(1, max_den + 1):
        n = round(profit * d)
        if n < 1:
            n = 1
        err = abs(n / d - profit)
        if err < best[2]:
            best = (n, d, err)
    return f"{best[0]}/{best[1]}"


def display_odds(odds):
    console = Console()
    t = Table(title="Estimated Odds")
    t.add_column("Horse", style="cyan")
    t.add_column("Decimal", justify="right")
    t.add_column("Fractional", justify="right")
    t.add_column("Implied %", justify="right")
    for name, dec in odds.items():
        imp = 100.0 / dec
        frac = to_fractional(dec)
        t.add_row(name, f"{dec:.2f}", frac, f"{imp:.1f}%")
    console.print(Panel(t, title="🏇 Market"))
