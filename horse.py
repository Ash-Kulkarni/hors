from pydantic import BaseModel
import random


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
