import random
from horse import Horse


def race_stream(horses: list[Horse], distance=1200, seed=None):
    """
    Generator: yields (tick_index, positions_dict), then returns race summary.
    Reproducible via 'seed'. No in-memory history.
    """
    rnd = random.Random(seed)
    track_condition = rnd.choice([0.9, 1.0, 1.1])
    moods = {h.name: rnd.choice([0.95, 1.0, 1.05]) for h in horses}

    positions = {h.name: 0.0 for h in horses}
    times = {h.name: 0 for h in horses}
    finished = set()
    order = []
    winner = None
    tick = 0

    while len(finished) < len(horses):
        tick += 1
        for h in horses:
            if h.name in finished:
                continue
            times[h.name] += 1
            # Use local RNG by passing a per-tick random factor
            # Option A: expose 'rnd' to move(); Option B: keep Horse.move() randomness
            move = h.move(1, track_condition, moods[h.name])
            positions[h.name] += move
            if positions[h.name] >= distance and h.name not in finished:
                finished.add(h.name)
                order.append(h.name)
                if winner is None:
                    winner = h
        yield tick, positions.copy()

    return {
        "winner": winner.name,
        "positions": positions,
        "times": times,
        "track_condition": track_condition,
        "moods": moods,
        "order": order,
        "distance": distance,
        "seed": seed,
    }


def run_race(horses: list[Horse], distance=1200, seed=None):
    gen = race_stream(horses, distance=distance, seed=seed)
    while True:
        try:
            next(gen)
        except StopIteration as e:
            return e.value  # <-- summary dict
