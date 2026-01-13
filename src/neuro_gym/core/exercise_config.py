"""Конфигурации упражнений с валидацией и типизацией."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence

SUPPORTED_DIFFICULTIES: Sequence[str] = (
    'Легкий',
    'Средний',
    'Сложный',
)


@dataclass(frozen=True)
class ExerciseConfig:
    values: Mapping[str, Mapping[str, Any]]

    def get(self, difficulty: str, key: str, default: Any = None) -> Any:
        return self.values.get(key, {}).get(difficulty, default)

    def missing_difficulties(self, difficulties: Sequence[str] = SUPPORTED_DIFFICULTIES) -> Dict[str, Sequence[str]]:
        """Возвращает недостающие уровни сложности для каждой настройки."""
        missing: Dict[str, Sequence[str]] = {}
        for setting, by_difficulty in self.values.items():
            gaps = tuple(level for level in difficulties if level not in by_difficulty)
            if gaps:
                missing[setting] = gaps
        return missing


class ExerciseConfigRegistry:
    def __init__(self, configs: Mapping[str, ExerciseConfig]):
        self._configs = dict(configs)

    def get(self, exercise_id: str, difficulty: str, key: str, default: Any = None) -> Any:
        config = self._configs.get(exercise_id)
        if not config:
            return default
        return config.get(difficulty, key, default)

    def validate(self) -> Dict[str, Dict[str, Sequence[str]]]:
        """Проверяет, что для каждой настройки присутствуют все уровни сложности."""
        issues: Dict[str, Dict[str, Sequence[str]]] = {}
        for exercise_id, config in self._configs.items():
            missing = config.missing_difficulties()
            if missing:
                issues[exercise_id] = missing
        return issues


EXERCISE_CONFIGS: Dict[str, ExerciseConfig] = {
    'pathfinder': ExerciseConfig({
        'duration': {'Легкий': 40, 'Средний': 35, 'Сложный': 45},
        'speed': {'Легкий': 120.0, 'Средний': 180.0, 'Сложный': 240.0},
        'deviation': {'Легкий': 80, 'Средний': 60, 'Сложный': 40},
        'trajectory': {'Легкий': 'linear', 'Средний': 'circular', 'Сложный': 'random'},
        'trajectory_interval': {'Легкий': 2.0, 'Средний': 1.5, 'Сложный': 1.2}
    }),
    'trajectory': ExerciseConfig({
        'checkpoints': {'Легкий': 6, 'Средний': 8, 'Сложный': 10}
    }),
    'sorting': ExerciseConfig({
        'categories': {'Легкий': 3, 'Средний': 4, 'Сложный': 5},
        'objects': {'Легкий': 6, 'Средний': 8, 'Сложный': 10},
        'errors': {'Легкий': 5, 'Средний': 4, 'Сложный': 3}
    }),
    'sequence': ExerciseConfig({
        'grid_size': {'Легкий': 3, 'Средний': 4, 'Сложный': 5},
        'sequence_length': {'Легкий': 3, 'Средний': 4, 'Сложный': 5},
        'display_time': {'Легкий': 1.0, 'Средний': 0.8, 'Сложный': 0.6},
        'difficulty_bonus': {'Легкий': 0, 'Средний': 10, 'Сложный': 20}
    }),
    'fast_fingers': ExerciseConfig({
        'appear_time': {'Легкий': 2.0, 'Средний': 1.5, 'Сложный': 1.0},
        'max_objects': {'Легкий': 3, 'Средний': 4, 'Сложный': 5},
        'object_types': {
            'Легкий': ['circle', 'square', 'triangle'],
            'Средний': ['circle', 'square', 'triangle', 'star'],
            'Сложный': ['circle', 'square', 'triangle', 'star', 'pentagon']
        },
        'spawn_interval': {'Легкий': 1.0, 'Средний': 0.8, 'Сложный': 0.6},
        'target_score': {'Легкий': 30, 'Средний': 40, 'Сложный': 50}
    }),
}

REGISTRY = ExerciseConfigRegistry(EXERCISE_CONFIGS)


def get_exercise_setting(exercise_id: str, difficulty: str, key: str, default: Any = None) -> Any:
    """Возвращает параметр упражнения по уровню сложности."""
    return REGISTRY.get(exercise_id, difficulty, key, default)
