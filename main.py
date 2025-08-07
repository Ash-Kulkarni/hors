from pydantic import BaseModel

import random
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
import time

from horse import Horse
from data import horse_data


def run_race(horses, distance=1200):
    """
    Simulate a race to a fixed distance. Returns a dict with all race data, including per-tick positions.
    """
    track_condition = random.choice([0.9, 1.0, 1.1])
    moods = {horse.name: random.choice([0.95, 1.0, 1.05]) for horse in horses}
    times = {horse.name: 0 for horse in horses}
    finished = set()
    positions = {horse.name: 0.0 for horse in horses}
    winner = None
    order = []
    history = []

    while len(finished) < len(horses):
        tick_snapshot = {}
        for horse in horses:
            if horse.name in finished:
                tick_snapshot[horse.name] = positions[horse.name]
                continue
            times[horse.name] += 1
            move = horse.move(1, track_condition, moods[horse.name])
            positions[horse.name] += move
            tick_snapshot[horse.name] = positions[horse.name]
            if positions[horse.name] >= distance and horse.name not in finished:
                finished.add(horse.name)
                order.append(horse.name)
                if winner is None:
                    winner = horse
        history.append(tick_snapshot.copy())
    return {
        "winner": winner.name,
        "positions": positions,
        "times": times,
        "track_condition": track_condition,
        "moods": moods,
        "order": order,
        "history": history,
        "distance": distance,
    }


def visualise_race_result(race_data, horses):
    console = Console()
    progress = Progress(
        TextColumn("[bold blue]{task.fields[name]}", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.completed:.1f}m"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )

    tasks = {}
    with progress:
        for horse in horses:
            tasks[horse.name] = progress.add_task(
                "", name=horse.name, total=race_data["distance"]
            )

        for tick in race_data["history"]:
            for horse in horses:
                current = progress.tasks[tasks[horse.name]].completed
                advance = max(0, tick[horse.name] - current)
                progress.update(tasks[horse.name], advance=advance)
            time.sleep(0.2)

    console.print(
        f"\n[bold yellow]Track Condition:[/] {race_data['track_condition']} | [bold yellow]Moods:[/] {race_data['moods']}"
    )
    console.print(f"\n🏆 [bold green]{race_data['winner']}[/] wins the race! 🏇")


def graph_wins(total_wins):
    console = Console()
    table = Table(title="Horse Race Win Counts")
    table.add_column("Horse", justify="left", style="cyan")
    table.add_column("Wins", justify="right", style="magenta")
    table.add_column("Bar", justify="left", style="green")
    max_wins = max(total_wins.values()) if total_wins else 1
    for horse, wins in total_wins.items():
        bar = "█" * int((wins / max_wins) * 20)
        table.add_row(horse, str(wins), bar)
    console.print(Panel(table, title="🏇 Race Results", expand=False))


if __name__ == "__main__":
    horses = [Horse(**data) for data in horse_data]
    total_wins = {horse.name: 0 for horse in horses}
    race_results = []
    for _ in range(100):
        race_data = run_race(horses)
        total_wins[race_data["winner"]] += 1
        race_results.append(race_data)
    graph_wins(total_wins)
    # Optionally, visualise a single race playback:
    visualise_race_result(race_results[2], horses)
    visualise_race_result(race_results[3], horses)
