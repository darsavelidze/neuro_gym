"""Вспомогательные функции отрисовки для UI."""

import pygame

from ...config import COLORS


def draw_progress_bar(surface: pygame.Surface, rect: pygame.Rect, ratio: float, *, bg_color=None, fill_color=None, border_radius: int = 8):
    """Рисует полоску прогресса в пределах прямоугольника."""
    bg = bg_color or COLORS['TEXT_DARK']
    fill = fill_color or COLORS['PRIMARY_BLUE']
    clamped = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surface, bg, rect, border_radius=border_radius)
    if clamped > 0:
        fill_width = int(rect.width * clamped)
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        pygame.draw.rect(surface, fill, fill_rect, border_radius=border_radius)
    return rect


def draw_hint(surface: pygame.Surface, font: pygame.font.Font, text: str, center_y: int, *, padding: int = 20,
              border_color=None, bg_color=None, text_color=None):
    """Рисует подпись-подсказку с рамкой и фоном."""
    border = border_color or COLORS['PRIMARY_BLUE']
    bg = bg_color or COLORS['BACKGROUND']
    color = text_color or COLORS['PRIMARY_BLUE']

    hint = font.render(text, True, color)
    hint_rect = hint.get_rect(center=(surface.get_width() // 2, center_y))
    hint_bg = hint_rect.inflate(padding * 2, padding)
    pygame.draw.rect(surface, bg, hint_bg, border_radius=10)
    pygame.draw.rect(surface, border, hint_bg, width=2, border_radius=10)
    surface.blit(hint, hint_rect)
    return hint_rect


def draw_result_panel(surface: pygame.Surface, fonts: dict, title: str, lines: list[str], *, rect: pygame.Rect | None = None,
                      bg_color=None, title_color=None, text_color=None, text_align: str = 'center'):
    """Рисует итоговый баннер с заголовком и строками статистики."""
    bg = bg_color or (COLORS['PRIMARY_BLUE'] + (200,)) if len(COLORS['PRIMARY_BLUE']) == 4 else COLORS['PRIMARY_BLUE']
    title_col = title_color or COLORS['TEXT_LIGHT']
    text_col = text_color or COLORS['TEXT_LIGHT']
    padding = 24
    line_spacing = 12

    if rect is None:
        w, h = surface.get_size()
        rect = pygame.Rect(w // 4, h // 4, w // 2, h // 3)

    pygame.draw.rect(surface, bg, rect, border_radius=15)

    title_text = fonts['LARGE'].render(title, True, title_col)
    title_rect = title_text.get_rect(center=(rect.centerx, rect.y + padding + title_text.get_height() // 2))
    surface.blit(title_text, title_rect)

    y = title_rect.bottom + padding // 2
    for line in lines:
        stat_text = fonts['MEDIUM'].render(line, True, text_col)
        if text_align == 'left':
            stat_rect = stat_text.get_rect(topleft=(rect.x + padding, y))
        elif text_align == 'right':
            stat_rect = stat_text.get_rect(topright=(rect.right - padding, y))
        else:
            stat_rect = stat_text.get_rect(midtop=(rect.centerx, y))
        surface.blit(stat_text, stat_rect)
        y = stat_rect.bottom + line_spacing

    return rect
