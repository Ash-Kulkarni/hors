import typer, random
from rich.console import Console
from hors.state import (
    load_state,
    save_state,
    ensure_horse_pool,
    select_field,
    record_race,
    apply_result,
)
from hors.sim import run_race
from hors.odds import estimate_decimal_odds

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def init():
    """Seed initial horses + config."""
    from hors.seed_state import main as seed

    seed()


@app.command()
def odds(sims: int = 800):
    """Train odds for the next field and display."""
    state = load_state()
    ensure_horse_pool(state, 30)
    horses = select_field(state)
    win_counts = {h.id: 0 for h in horses}
    for _ in range(sims):
        res = run_race(horses)
        win_counts[res["winner"]] += 1
    o = {hid: round(v, 2) for hid, v in estimate_decimal_odds(win_counts, sims).items()}
    from rich.table import Table
    from rich.panel import Panel

    t = Table(title="Estimated Odds")
    t.add_column("Horse")
    t.add_column("Decimal", justify="right")
    t.add_column("Implied %", justify="right")
    over = 0.0
    for h in horses:
        over += 1 / o[h.id]
        t.add_row(h.name, f"{o[h.id]:.2f}", f"{100 / o[h.id]:.1f}%")
    console.print(Panel(t, title=f"Book: {over * 100:.1f}%"))


@app.command()
def race(distance: int = 1200, watch: bool = typer.Option(False, help="Live progress")):
    """Run a single race now."""
    state = load_state()
    ensure_horse_pool(state, 30)
    horses = select_field(state)
    seed = random.randint(0, 2**32 - 1)
    res = (
        run_race(horses, distance=distance, seed=seed, tick_delay=0.04)
        if watch
        else run_race(horses, distance=distance, seed=seed)
    )
    record_race(state, horses, res)
    apply_result(state, horses, res)
    save_state(state)


@app.command()
def run(interval: int = 120, distance: int = 1200):
    """Loop: price, race, persist, sleep."""
    import time

    try:
        while True:
            race(distance=distance, watch=False)  # reuse command
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped.[/]")


@app.command()
def horses(top: int = 0):
    """List horses; --top N shows top by wins."""
    from hors.models import Horse
    from rich.table import Table
    from rich.panel import Panel

    st = load_state()
    rows = [Horse(**h) for h in st["horses"]]
    if top:
        rows.sort(key=lambda h: h.wins, reverse=True)
        rows = rows[:top]
    t = Table(title="Horses")
    t.add_column("Name")
    t.add_column("Wins", justify="right")
    t.add_column("Age", justify="right")
    t.add_column("Class")
    for h in rows:
        t.add_row(h.name, str(h.wins), str(h.age_races), getattr(h, "klass", ""))
    console.print(Panel(t))


@app.command()
def archive(which: str = typer.Argument("last"), replay: bool = False):
    """Show last race (and optionally replay)."""
    st = load_state()
    if not st["races"]:
        console.print("[red]No races yet.[/]")
        raise typer.Exit(1)
    r = (
        st["races"][-1]
        if which == "last"
        else next((x for x in st["races"] if x["id"] == which), None)
    )
    if not r:
        console.print("[red]Race not found.[/]")
        raise typer.Exit(1)
    # summary table
    from rich.table import Table
    from rich.panel import Panel

    t = Table(title=f"Race {r['id']} • Seed {r['seed']} • Track {r['track']}")
    t.add_column("#")
    t.add_column("Horse")
    id_to_name = {h["id"]: h["name"] for h in st["horses"]}
    for i, hid in enumerate(r["order"], 1):
        t.add_row(str(i), id_to_name.get(hid, hid))
    console.print(Panel(t))
    if replay:
        # reconstruct horse objs and replay from seed
        from models import Horse as HModel

        horses = [HModel(**h) for h in st["horses"] if h["id"] in r["horses"]]
        visualise_race_result(
            horses, distance=r.get("distance", 1200), seed=r["seed"], tick_delay=0.04
        )


if __name__ == "__main__":
    app()
