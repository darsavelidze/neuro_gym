"""Контейнер зависимостей приложения."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .achievements_manager import AchievementsManager
    from .camera_controller import CameraController
    from .input_handler import InputHandler
    from .localization_manager import LocalizationManager
    from .mouse_tracker import MouseTracker
    from .progress_manager import ProgressManager
    from .sound_manager import SoundManager
    from .result_service import ResultService


@dataclass
class AppContext:
    sound: "SoundManager"
    progress: "ProgressManager"
    localization: "LocalizationManager"
    input_handler: "InputHandler"
    camera: "CameraController"
    achievements: "AchievementsManager"
    mouse_tracker: "MouseTracker"
    results: "ResultService"
