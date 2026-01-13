"""Сервис обработки результатов упражнений."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple


@dataclass(frozen=True)
class ExerciseResult:
    exercise_id: str
    score: int
    accuracy: float
    duration: float
    star_score: int
    xp_gain: int


class ResultService:
    def __init__(self, progress_manager, achievements_manager):
        self.progress = progress_manager
        self.achievements = achievements_manager

    def process(self, result: ExerciseResult) -> Tuple[int, Iterable]:
        """Сохраняет результат и возвращает (звезды, новые достижения)."""
        stars = 0
        new_achievements: Iterable = []
        if self.progress:
            stars = self.progress.update_exercise_result(
                result.exercise_id,
                result.star_score,
                result.xp_gain,
            )
        if self.achievements:
            new_achievements = self.achievements.check_achievements()
        return stars, new_achievements
