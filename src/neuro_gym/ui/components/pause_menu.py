"""Компонент единого меню паузы для упражнений NeuroGym"""

from dataclasses import dataclass
from typing import Callable, Sequence

import pygame

from ...config import COLORS


@dataclass
class PauseOption:
    """Действие, доступное во время паузы."""

    label: str
    callback: Callable[[], None]
    color: tuple[int, int, int] | None = None
    text_color: tuple[int, int, int] | None = None
    font_size: str = 'MEDIUM'


class PauseMenu:
    """Управляет отображением меню паузы на экране упражнения."""

    def __init__(self, base_screen, width_ratio: float = 0.6, button_height: int = 60, spacing: int = 18):
        self.base_screen = base_screen
        # Небольшой кламп, чтобы кнопки не схлопывались и не выходили за экран
        self.width_ratio = max(0.1, min(width_ratio, 0.95))
        self.button_height = button_height
        self.spacing = spacing
        self.visible = False
        self.options: list[PauseOption] = []
        self.message = "Пауза"
        self._last_layout_size: tuple[int, int] | None = None

    def show(self, options: Sequence[PauseOption], message: str = "Пауза") -> None:
        """Показывает меню паузы с набором действий."""
        self.options = list(options)
        self.message = message
        self.visible = True
        self._layout_buttons()

    def hide(self) -> None:
        """Скрывает меню паузы."""
        self.visible = False
        self.options = []
        # Отключаем обработчики кнопок паузы
        self.base_screen.buttons = []

    def _layout_buttons(self) -> None:
        """Располагает кнопки паузы по центру экрана."""
        surface = self.base_screen.screen
        if not self.options:
            self.base_screen.buttons = []
            self._last_layout_size = surface.get_size()
            return

        total_height = len(self.options) * (self.button_height + self.spacing) - self.spacing
        width = int(surface.get_width() * self.width_ratio)
        start_x = (surface.get_width() - width) // 2
        start_y = (surface.get_height() - total_height) // 2 + 40

        self.base_screen.buttons = []
        for index, option in enumerate(self.options):
            y = start_y + index * (self.button_height + self.spacing)
            action_color = option.color or COLORS['PRIMARY_BLUE']
            action_text_color = option.text_color or COLORS['TEXT_LIGHT']
            self.base_screen.create_button(
                option.label,
                start_x,
                y,
                width,
                self.button_height,
                action=option.callback,
                color=action_color,
                text_color=action_text_color,
                font_size=option.font_size
            )

            self._last_layout_size = surface.get_size()

    def draw(self) -> None:
        """Рисует затемнение и заголовок меню паузы."""
        if not self.visible:
            return

        # При ресайзе окна перерисовываем кнопки, чтобы сохранить выравнивание
        current_size = self.base_screen.screen.get_size()
        if self._last_layout_size != current_size:
            self._layout_buttons()

        surface = self.base_screen.screen
        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font = self.base_screen.fonts.get('EXTRA_LARGE') or pygame.font.SysFont('Arial', 48)
        title = font.render(self.message, True, COLORS['TEXT_LIGHT'])
        rect = title.get_rect(center=(width // 2, height // 4))
        surface.blit(title, rect)
