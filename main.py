from pydantic import BaseModel

import random
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
import time


class Horse(BaseModel):
    name: str
    age: int
    breed: str
    energy: float
    appetite: float
    discipline: float
    agility: float
    temperament: float

    def move(
        self, time: float, track_condition: float = 1.0, mood: float = 1.0
    ) -> float:
        """
        Calculates distance based on stats, with randomness, track condition, and mood.
        """
        base = self.energy * time
        agility_bonus = self.agility * (1 + 0.05 * time)
        discipline_factor = 1 + (self.discipline / 10)
        temperament_effect = 1 - abs(self.temperament - 5) * 0.05
        appetite_boost = self.appetite * 0.1

        # Add a small random factor (±5%)
        random_factor = random.uniform(0.95, 1.05)

        # Mood and track_condition are multipliers (default 1.0)
        return (
            (base + agility_bonus + appetite_boost)
            * discipline_factor
            * temperament_effect
            * track_condition
            * mood
            * random_factor
        )


horse_data = [
    {
        "name": "Willow",
        "age": 6,
        "breed": "Thoroughbred",
        "energy": 8.0,
        "appetite": 6.5,
        "discipline": 7.0,
        "agility": 8.5,
        "temperament": 5.0,
    },
    {
        "name": "Maple",
        "age": 4,
        "breed": "Morgan",
        "energy": 7.5,
        "appetite": 8.0,
        "discipline": 6.0,
        "agility": 7.0,
        "temperament": 6.5,
    },
    {
        "name": "Echo",
        "age": 9,
        "breed": "Arabian",
        "energy": 6.0,
        "appetite": 5.5,
        "discipline": 9.0,
        "agility": 9.0,
        "temperament": 4.0,
    },
]


def run_race(horses, distance=1200):
    """
    Simulate a race to a fixed distance. Returns the winner and a dict of final distances.
    """
    track_condition = random.choice([0.9, 1.0, 1.1])
    moods = {horse.name: random.choice([0.95, 1.0, 1.05]) for horse in horses}
    times = {horse.name: 0 for horse in horses}
    finished = set()
    positions = {horse.name: 0.0 for horse in horses}
    winner = None

    while len(finished) < len(horses):
        for horse in horses:
            if horse.name in finished:
                continue
            # Each "tick" is 1 second
            times[horse.name] += 1
            positions[horse.name] += horse.move(1, track_condition, moods[horse.name])
            if positions[horse.name] >= distance and horse.name not in finished:
                finished.add(horse.name)
                if winner is None:
                    winner = horse
    return winner, positions, times, track_condition, moods


def visualise_race(horses, distance=1200):
    console = Console()
    progress = Progress(
        TextColumn("[bold blue]{task.fields[name]}", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.completed:.1f}m"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )

    track_condition = random.choice([0.9, 1.0, 1.1])
    moods = {horse.name: random.choice([0.95, 1.0, 1.05]) for horse in horses}
    tasks = {}
    positions = {horse.name: 0.0 for horse in horses}
    finished = set()
    winner = None

    with progress:
        for horse in horses:
            tasks[horse.name] = progress.add_task("", name=horse.name, total=distance)

        while len(finished) < len(horses):
            for horse in horses:
                if horse.name in finished:
                    continue
                move = horse.move(1, track_condition, moods[horse.name])
                positions[horse.name] += move
                progress.update(tasks[horse.name], advance=move)
                if positions[horse.name] >= distance and horse.name not in finished:
                    finished.add(horse.name)
                    if winner is None:
                        winner = horse
            time.sleep(0.2)

    console.print(
        f"\n[bold yellow]Track Condition:[/] {track_condition} | [bold yellow]Moods:[/] {moods}"
    )
    console.print(f"\n🏆 [bold green]{winner.name}[/] wins the race! 🏇")


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


# Example: benchmark 100 races and graph the wins
if __name__ == "__main__":
    horses = [Horse(**data) for data in horse_data]
    total_wins = {horse.name: 0 for horse in horses}
    for _ in range(100):
        winner, *_ = run_race(horses, 1500)
        total_wins[winner.name] += 1
    graph_wins(total_wins)
    # Optionally, visualise a single race:
    visualise_race(horses)
