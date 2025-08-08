import json, os, random
from typing import List
from hors.models import Horse, new_horse

STATE_PATH = "state.json"


def load_state():
    if not os.path.exists(STATE_PATH):
        return {
            "horses": [],
            "races": [],
            "config": {"race_every_sec": 120, "field_size": 6, "max_horses": 60},
        }
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def ensure_horse_pool(state, min_count=30):
    if len(state["horses"]) >= min_count:
        return
    for _ in range(min_count - len(state["horses"])):
        h = new_horse()
        state["horses"].append(h.model_dump())


def classify(h):
    w = h["wins"]
    if w == 0:
        return "maiden"
    if w <= 3:
        return "novice"
    return "open"


def select_field(state):
    horses = [Horse(**h) for h in state["horses"] if h["age_races"] < h["retire_after"]]
    # group by class; pick the most populous class
    buckets = {"maiden": [], "novice": [], "open": []}
    for h in horses:
        h.klass = classify(h.model_dump())
        buckets[h.klass].append(h)
    group = max(buckets.values(), key=lambda L: len(L)) or horses
    random.shuffle(group)
    field_size = state["config"]["field_size"]
    return group[:field_size]


def apply_result(state, horses, race_summary):
    winner_id = race_summary["winner"]
    for h in state["horses"]:
        if h["id"] in race_summary["positions"]:
            h["age_races"] += 1
            if h["id"] == winner_id:
                h["wins"] += 1
            else:
                h["losses"] += 1
    # retire + respawn
    alive = []
    for h in state["horses"]:
        if h["age_races"] >= h["retire_after"]:
            continue
        alive.append(h)
    state["horses"] = alive
    ensure_horse_pool(state, min_count=30)


def record_race(state, horses, summary):
    state["races"].append(
        {
            "id": f"r_{len(state['races']) + 1:05d}",
            "ts": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "distance": summary["distance"],
            "seed": summary["seed"],
            "track": summary["track_condition"],
            "moods": summary["moods"],
            "horses": [h.id for h in horses],
            "order": summary["order"],
            "winner": summary["winner"],
        }
    )
