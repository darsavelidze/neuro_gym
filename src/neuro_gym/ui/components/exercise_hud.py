"""Вспомогательный HUD для упражнений: пауза и базовые метрики."""

import pygame

from ...config import COLORS, SCREEN_PADDING
from ...utils.formatting import format_time_seconds


class ExerciseHUD:
    """Отвечает за создание общей кнопки паузы и отрисовку базовых метрик."""

    def __init__(self, base_screen):
        self.base_screen = base_screen
        self.pause_button = None

    def ensure_pause_button(self, on_toggle):
        """Создает или переиспользует кнопку паузы в правом верхнем углу."""
        pause_size = 40
        pause_x = self.base_screen.width - pause_size - SCREEN_PADDING
        pause_y = SCREEN_PADDING
        # Пересоздаем, чтобы обновить ссылку на действие
        self.pause_button = self.base_screen.create_button(
            "II",
            pause_x,
            pause_y,
            pause_size,
            pause_size,
            action=on_toggle,
            font_size='MEDIUM'
        )
        return self.pause_button

    def draw_basic(self, score, elapsed_time, duration):
        """Рисует базовую панель: счет и таймер. Возвращает следующую y-координату для доп. строк."""
        screen = self.base_screen.screen
        fonts = self.base_screen.fonts
        localization = getattr(self.base_screen.screen_manager.game, 'localization_manager', None)
        score_label = localization.get_text('score') if localization else 'Счет'
        time_label = localization.get_text('time') if localization else 'Время'

        score_text = fonts['MEDIUM'].render(f"{score_label}: {int(score)}", True, COLORS['TEXT_DARK'])
        score_rect = score_text.get_rect(topleft=(SCREEN_PADDING, SCREEN_PADDING))
        screen.blit(score_text, score_rect)

        remaining_time = max(0, duration - elapsed_time)
        time_text = fonts['MEDIUM'].render(
            f"{time_label}: {format_time_seconds(remaining_time)}",
            True,
            COLORS['TEXT_DARK']
        )
        time_rect = time_text.get_rect(topright=(self.base_screen.width - SCREEN_PADDING - 50, SCREEN_PADDING))
        screen.blit(time_text, time_rect)

        return score_rect.bottom + 10
