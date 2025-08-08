import random, time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from typing import Dict, List
from hors.models import Horse

console = Console()


def horse_move(h: Horse, track: float, mood: float, rnd: random.Random) -> float:
    base = h.stats.energy
    agility_bonus = h.stats.agility * 1.05
    discipline_factor = 1 + (h.stats.discipline / 10)
    temperament_effect = max(0.2, 1 - abs(h.stats.temperament - 5) * 0.05)
    random_factor = rnd.uniform(0.95, 1.05)
    return (
        (base + agility_bonus)
        * discipline_factor
        * temperament_effect
        * track
        * mood
        * random_factor
    )


def run_race(horses: List[Horse], distance=1200, seed=None, tick_delay=None):
    rnd = random.Random(seed)
    track = rnd.choice([0.9, 1.0, 1.1])
    moods = {h.id: rnd.choice([0.95, 1.0, 1.05]) for h in horses}
    pos = {h.id: 0.0 for h in horses}
    time_ticks = {h.id: 0 for h in horses}
    finished, order, winner = set(), [], None

    # optional visualization
    progress = None
    tasks = {}
    if tick_delay is not None:
        progress = Progress(
            TextColumn("[bold blue]{task.fields[name]}"),
            BarColumn(bar_width=None),
            TextColumn("{task.completed:.1f}m"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        )
        progress.start()
        for h in horses:
            tasks[h.id] = progress.add_task("", name=h.name, total=distance)

    while len(finished) < len(horses):
        for h in horses:
            if h.id in finished:
                continue
            time_ticks[h.id] += 1
            pos[h.id] += horse_move(h, track, moods[h.id], rnd)
            if pos[h.id] >= distance:
                finished.add(h.id)
                order.append(h.id)
                if winner is None:
                    winner = h.id
        if progress:
            for h in horses:
                task = progress.tasks[tasks[h.id]]
                current = task.completed
                advance = max(0, min(pos[h.id], distance) - current)
                progress.update(tasks[h.id], advance=advance)
            time.sleep(tick_delay)

    if progress:
        progress.stop()

    return {
        "winner": winner,
        "order": order,
        "positions": pos,
        "times": time_ticks,
        "track_condition": track,
        "moods": moods,
        "distance": distance,
        "seed": seed,
    }
