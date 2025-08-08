import json
import os
import random
from pathlib import Path
from hors.models import new_horse

STATE_PATH = Path("state.json")
NAMES_PATH = Path("data/names.txt")


def load_names():
    if NAMES_PATH.exists():
        with open(NAMES_PATH) as f:
            return [line.strip() for line in f if line.strip()]
    return []


def main():
    names = load_names()
    horses = []
    for _ in range(30):  # starting pool
        name = random.choice(names) if names else None
        h = new_horse(name)
        horses.append(h.model_dump())

    state = {
        "horses": horses,
        "races": [],
        "config": {
            "race_every_sec": 20,  # every 2 min for now
            "field_size": 6,
            "max_horses": 60,
        },
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Seeded {len(horses)} horses into {STATE_PATH}")


if __name__ == "__main__":
    main()
