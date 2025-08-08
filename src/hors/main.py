import random, time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from hors.models import Horse
from hors.sim import run_race
from hors.odds import estimate_decimal_odds
from hors.state import (
    load_state,
    save_state,
    ensure_horse_pool,
    select_field,
    apply_result,
    record_race,
)

console = Console()


def train_odds(state, sims=1000):
    # Monte Carlo per active pool
    horses = select_field(state)
    win_counts = {h.id: 0 for h in horses}
    for _ in range(sims):
        res = run_race(horses)
        win_counts[res["winner"]] += 1
    odds = estimate_decimal_odds(win_counts, sims)
    return horses, odds


def print_odds(horses, odds):
    t = Table(title="Estimated Odds")
    t.add_column("Horse", style="cyan")
    t.add_column("Decimal", justify="right")
    t.add_column("Implied %", justify="right")
    overround = 0.0
    for h in horses:
        o = round(odds[h.id], 2)
        overround += 1 / o
        t.add_row(h.name, f"{o:.2f}", f"{100 / o:.1f}%")
    console.print(Panel(t, title=f"Book: {(overround * 100):.1f}%"))


def main_loop():
    state = load_state()
    ensure_horse_pool(state, min_count=30)

    while True:
        horses, odds = train_odds(state, sims=800)
        print_odds(horses, odds)

        seed = random.randint(0, 2**32 - 1)
        res = run_race(horses, seed=seed, tick_delay=0.03, distance=1200)
        # Show quick results
        console.print(
            Panel(
                f"Winner: [bold]{next(h.name for h in horses if h.id == res['winner'])}[/]  •  Seed: {seed}"
            )
        )

        record_race(state, horses, res)
        apply_result(state, horses, res)
        save_state(state)

        time.sleep(state["config"]["race_every_sec"])


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down...[/]")
