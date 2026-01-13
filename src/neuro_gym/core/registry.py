"""
Реестр экранов и упражнений NeuroGym с ленивой загрузкой классов.
"""

from __future__ import annotations

from importlib import import_module
from typing import Callable, Iterable, Sequence, Tuple

from ..config import EXERCISES

ScreenEntry = Tuple[str, str]

MAIN_SCREENS: Sequence[ScreenEntry] = (
    ('loading', 'neuro_gym.ui.loading_screen.LoadingScreen'),
    ('main_menu', 'neuro_gym.ui.main_menu.MainMenu'),
    ('exercise_selection', 'neuro_gym.ui.exercise_selection.ExerciseSelection'),
    ('instructions', 'neuro_gym.ui.instructions_screen.InstructionsScreen'),
    ('settings', 'neuro_gym.ui.settings_screen.SettingsScreen'),
    ('results', 'neuro_gym.ui.results_screen.ResultsScreen'),
    ('achievements', 'neuro_gym.ui.achievements_screen.AchievementsScreen'),
)

EXERCISE_SCREENS: Sequence[ScreenEntry] = tuple(
    (exercise['id'], exercise['screen']) for exercise in EXERCISES if exercise.get('screen')
)

ALL_SCREENS: Sequence[ScreenEntry] = MAIN_SCREENS + EXERCISE_SCREENS


def resolve_screen(dotted_path: str):
    """Импортирует и возвращает класс экрана по dotted path."""
    module_path, class_name = dotted_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name)


def iter_screen_entries() -> Iterable[ScreenEntry]:
    """Итерирует все экраны с их путями."""
    return ALL_SCREENS
