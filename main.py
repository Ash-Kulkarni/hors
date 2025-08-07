import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from horse import Horse
from data import horse_data
from simulation import run_race
from display import display_odds, visualise_race_result
from pricing import estimate_all_odds


def main():
    console = Console()
    horses = [Horse(**d) for d in horse_data]

    # Train odds (more sims = more stable)
    sims = 2000
    total_wins = {h.name: 0 for h in horses}
    for _ in range(sims):
        res = run_race(horses)
        total_wins[res["winner"]] += 1

    odds = estimate_all_odds(
        horses, total_wins, sims=sims, house_margin=0.10, alpha=1.0
    )
    display_odds(odds)

    # Example bets
    bets = {"Willow": 100, "Maple": 50, "Echo": 75}

    # Run a reproducible race and visualize from seed (no history stored)
    seed = random.randint(0, 2**32 - 1)
    race = visualise_race_result(horses, distance=1200, seed=seed, tick_delay=0.05)

    # Settle
    winner = race["winner"]
    payouts = {}
    for name, stake in bets.items():
        if name == winner:
            profit = stake * (odds[name] - 1)  # profit-only
            payouts[name] = profit
        else:
            payouts[name] = -stake

    # Payout table
    t = Table(title="Payouts")
    t.add_column("Horse")
    t.add_column("Stake", justify="right")
    t.add_column("P/L", justify="right")
    for name, stake in bets.items():
        pl = payouts[name]
        t.add_row(
            name,
            f"£{stake:.2f}",
            f"[green]£{pl:.2f}[/]" if pl >= 0 else f"[red]£{pl:.2f}[/]",
        )
    console.print(Panel(t, title=f"🏆 Winner: {winner}  |  Seed: {race['seed']}"))


if __name__ == "__main__":
    main()
