from pydantic import BaseModel, Field
from typing import List, Dict, Literal
import uuid, random
from pathlib import Path

NAMES_PATH = Path(__file__).parent / "data" / "names.txt"

ClassName = Literal["maiden", "novice", "open"]


class Stats(BaseModel):
    energy: float
    agility: float
    discipline: float
    temperament: float


class Horse(BaseModel):
    id: str
    name: str
    age_races: int = 0
    retire_after: int = 10
    wins: int = 0
    losses: int = 0
    klass: ClassName = "maiden"
    form: List[float] = Field(default_factory=list)
    stats: Stats


def get_name():
    names = [n.strip() for n in NAMES_PATH.read_text().splitlines() if n.strip()]
    return random.choice(names)


def new_horse(name: str | None = None) -> Horse:
    if not name:
        name = get_name()
    s = Stats(
        energy=random.uniform(6, 9),
        agility=random.uniform(6, 9),
        discipline=random.uniform(5, 9),
        temperament=random.uniform(3, 7),
    )
    return Horse(id=f"h_{uuid.uuid4().hex[:6]}", name=name, stats=s)
