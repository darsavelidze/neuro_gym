"""Компонент для отображения итогового баннера в упражнениях."""

from __future__ import annotations

from typing import Iterable

import pygame

from ..utils.draw import draw_result_panel


class ResultBanner:
    """Упрощённое управление всплывающим баннером результата."""

    def __init__(self, fonts: dict[str, pygame.font.Font]):
        self.fonts = fonts
        self.visible = False
        self.title = ''
        self.lines: list[str] = []
        self.bg_color = None
        self.title_color = None
        self.text_color = None
        self.text_align = 'center'
        self.rect: pygame.Rect | None = None

    def show(self, title: str, lines: Iterable[str], *, rect: pygame.Rect | None = None,
             bg_color=None, title_color=None, text_color=None, text_align='left') -> None:
        self.title = title
        self.lines = list(lines)
        self.rect = rect
        self.bg_color = bg_color
        self.title_color = title_color
        self.text_color = text_color
        self.text_align = text_align
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        draw_result_panel(
            surface,
            self.fonts,
            self.title,
            self.lines,
            rect=self.rect,
            bg_color=self.bg_color,
            title_color=self.title_color,
            text_color=self.text_color,
            text_align=self.text_align
        )
