"""
Простой трекер мыши для приложения NeuroGym
Отслеживает позицию курсора мыши для управления интерфейсом.

Примечание: pygame.mouse.get_pos() — неблокирующий вызов, поэтому
отдельный поток для опроса мыши не нужен. Трекер реализует
тот же публичный API, что и HandTracker, для взаимозаменяемости.
"""

import pygame


class MouseTracker:
    """Класс для отслеживания позиции курсора мыши (без отдельного потока)."""

    def __init__(self):
        self.running = False

    def start(self):
        """Активация трекера (поток не создаётся — используется get_pos)."""
        self.running = True
        return True

    def stop(self):
        """Деактивация трекера."""
        self.running = False

    def get_cursor_position(self):
        """Получение текущей позиции курсора мыши."""
        if not self.running:
            return None
        return pygame.mouse.get_pos()

    # --- Методы-заглушки для совместимости с HandTracker API ---

    def is_tracking_lost(self):
        """Мышь никогда не «теряется»."""
        return False

    def get_current_frame(self):
        """Заглушка для совместимости с API камеры."""
        return None
