"""
Менеджер экранов для приложения NeuroGym
Отвечает за переключение между различными экранами приложения.
Хранит экземпляры экранов и вызывает хуки жизненного цикла on_enter/on_exit.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pygame

from .registry import EXERCISE_SCREENS


class ScreenManager:
    def __init__(self, screen, context=None, game=None):
        """Инициализация менеджера экранов.

        Args:
            screen: поверхность pygame для отрисовки
            context: общий контейнер зависимостей (звук, прогресс и т.п.)
            game: ссылка на Game для обратных вызовов
        """
        self.screen = screen
        self.context = context
        self.game = game

        self.screens: Dict[str, Any] = {}
        self.screen_instances: Dict[str, Any] = {}
        self.current_screen: Optional[str] = None
        self.screen_history: list[str] = []
        self.screen_params: Dict[str, Dict[str, Any]] = {}

    def register_screen(self, screen_id, screen_class):
        """Регистрация нового экрана."""
        self.screens[screen_id] = screen_class

    def stop(self):
        """Запрос на остановку игры через Game."""
        if self.game:
            self.game.stop()

    def _apply_default_params(self, screen_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Дополняет параметры экрана значением сложности, если нужно."""
        if screen_id in dict(EXERCISE_SCREENS) and 'difficulty' not in params and self.game:
            params = dict(params)
            params['difficulty'] = self.game.get_difficulty()
        return params

    def _get_or_create_screen(self, screen_id: str, params: Dict[str, Any]):
        if screen_id not in self.screen_instances:
            screen_ref = self.screens[screen_id]
            if isinstance(screen_ref, str):
                from .registry import resolve_screen  # локальный импорт для избежания циклов
                screen_class = resolve_screen(screen_ref)
                self.screens[screen_id] = screen_class
            else:
                screen_class = screen_ref

            instance = screen_class(self, self.screen, **params)
            if hasattr(instance, 'set_context'):
                instance.set_context(self.context)
            self.screen_instances[screen_id] = instance

        screen = self.screen_instances[screen_id]
        # Сбрасываем переходы при повторном входе
        screen.next_screen = None
        screen.running = True
        if hasattr(screen, 'transition_params'):
            delattr(screen, 'transition_params')
        return screen

    def go_to(self, screen_id, **params):
        """Переход к указанному экрану с сохранением истории."""
        if screen_id not in self.screens:
            print(f"Ошибка: экран {screen_id} не найден")
            return None

        resolved_params = self._apply_default_params(screen_id, params)
        if self.current_screen:
            self.screen_history.append(self.current_screen)
            current_instance = self.screen_instances.get(self.current_screen)
            if current_instance and hasattr(current_instance, 'on_exit'):
                current_instance.on_exit()

        self.screen_params[screen_id] = resolved_params
        self.current_screen = screen_id

        screen_instance = self._get_or_create_screen(screen_id, resolved_params)
        if hasattr(screen_instance, 'on_enter'):
            screen_instance.on_enter(resolved_params)
        return screen_instance

    def go_back(self):
        """Возврат к предыдущему экрану с вызовом on_exit/on_enter."""
        if not self.screen_history:
            return None

        if self.current_screen:
            active = self.screen_instances.get(self.current_screen)
            if active and hasattr(active, 'on_exit'):
                active.on_exit()

        previous_screen = self.screen_history.pop()
        self.current_screen = previous_screen

        params = self.screen_params.get(previous_screen, {})
        screen_instance = self._get_or_create_screen(previous_screen, params)
        if hasattr(screen_instance, 'on_enter'):
            screen_instance.on_enter(params)
        return screen_instance

    def get_current_screen(self):
        """Получение текущего активного экрана."""
        if not self.current_screen or self.current_screen not in self.screens:
            return None
        params = self.screen_params.get(self.current_screen, {})
        params = self._apply_default_params(self.current_screen, params)
        return self._get_or_create_screen(self.current_screen, params)
