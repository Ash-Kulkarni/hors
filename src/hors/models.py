from pydantic import BaseModel, Field
from typing import List, Dict, Literal
import uuid, random

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


def new_horse(name: str | None = None) -> Horse:
    if not name:
        name = f"Horse-{uuid.uuid4().hex[:4]}"
    # light random but sane ranges
    s = Stats(
        energy=random.uniform(6, 9),
        agility=random.uniform(6, 9),
        discipline=random.uniform(5, 9),
        temperament=random.uniform(3, 7),
    )
    return Horse(id=f"h_{uuid.uuid4().hex[:6]}", name=name, stats=s)
