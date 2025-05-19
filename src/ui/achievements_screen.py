"""
Экран достижений для приложения NeuroGym
Отображает полученные и доступные достижения пользователя
"""

import pygame
import sys
import math
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from ui.base_screen import BaseScreen
from config import COLORS, SCREEN_PADDING

class AchievementsScreen(BaseScreen):
    def __init__(self, screen_manager, screen):
        """
        Инициализация экрана достижений
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
        """
        super().__init__(screen_manager, screen)
        
        # Получаем доступ к менеджеру достижений и локализации через screen_manager
        self.achievements_manager = self.screen_manager.game.achievements_manager
        self.localization = self.screen_manager.game.localization_manager
        
        # Получаем список достижений
        self.language = self.localization.get_language()
        self.achievements = self.achievements_manager.get_all_achievements(self.language)
        
        # Параметры отображения списка
        self.items_per_page = 4
        self.current_page = 0
        self.total_pages = max(1, (len(self.achievements) + self.items_per_page - 1) // self.items_per_page)
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса экрана достижений
        """
        # Очистка кнопок
        self.buttons = []
        
        # Кнопка "Назад" для возврата в главное меню
        back_button_width = 150
        back_button_height = 60
        back_button_x = SCREEN_PADDING
        back_button_y = SCREEN_PADDING
        
        self.create_button(
            self.localization.get_text('back'), 
            back_button_x, back_button_y, 
            back_button_width, back_button_height, 
            action=lambda: self.transition_to('main_menu'),
            color=COLORS['PRIMARY_BLUE']
        )
        
        # Если есть несколько страниц, добавляем кнопки навигации
        if self.total_pages > 1:
            nav_button_width = 80
            nav_button_height = 60
            
            # Кнопка "Предыдущая страница"
            prev_button_x = self.width // 4 - nav_button_width // 2
            prev_button_y = self.height - SCREEN_PADDING - nav_button_height
            
            self.create_button(
                "←", 
                prev_button_x, prev_button_y, 
                nav_button_width, nav_button_height, 
                action=self._prev_page,
                color=COLORS['PRIMARY_BLUE']
            )
            
            # Кнопка "Следующая страница"
            next_button_x = 3 * self.width // 4 - nav_button_width // 2
            next_button_y = self.height - SCREEN_PADDING - nav_button_height
            
            self.create_button(
                "→", 
                next_button_x, next_button_y, 
                nav_button_width, nav_button_height, 
                action=self._next_page,
                color=COLORS['PRIMARY_BLUE']
            )
    
    def _prev_page(self):
        """
        Переход на предыдущую страницу
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.screen_manager.game.sound_manager.play_sound('button_click')
    
    def _next_page(self):
        """
        Переход на следующую страницу
        """
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.screen_manager.game.sound_manager.play_sound('button_click')
    
    def update(self, dt):
        """
        Обновление экрана достижений
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновляем язык, если он изменился
        current_language = self.localization.get_language()
        if current_language != self.language:
            self.language = current_language
            self.achievements = self.achievements_manager.get_all_achievements(self.language)
    
    def draw(self):
        """
        Отрисовка экрана достижений
        """
        # Заливка фона
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Отрисовка заголовка
        title_text = self.fonts['LARGE'].render(
            self.localization.get_text('achievements'), 
            True, 
            COLORS['PRIMARY_BLUE']
        )
        title_rect = title_text.get_rect(center=(self.width // 2, SCREEN_PADDING + 30))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка счетчика страниц
        if self.total_pages > 1:
            page_text = self.fonts['MEDIUM'].render(
                f"{self.current_page + 1} / {self.total_pages}", 
                True, 
                COLORS['TEXT_DARK']
            )
            page_rect = page_text.get_rect(center=(self.width // 2, self.height - SCREEN_PADDING - 30))
            self.screen.blit(page_text, page_rect)
            
        # Отрисовка достижений текущей страницы
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.achievements))
        
        achievements_to_display = self.achievements[start_idx:end_idx]
        
        card_width = int(self.width * 0.8)
        card_height = 100
        card_margin = 20
        card_start_y = 100
        
        for i, achievement in enumerate(achievements_to_display):
            card_y = card_start_y + i * (card_height + card_margin)
            card_x = (self.width - card_width) // 2
            
            # Определяем цвет карточки в зависимости от статуса достижения
            card_color = COLORS['PRIMARY_BLUE'] if achievement['achieved'] else (80, 80, 100)
            
            # Рисуем карточку достижения
            self._draw_achievement_card(
                achievement, 
                card_x, card_y, 
                card_width, card_height,
                card_color
            )
            
        # Отрисовка кнопок
        self.draw_buttons()
            
    def _draw_achievement_card(self, achievement, x, y, width, height, color):
        """
        Отрисовка карточки достижения
        
        Args:
            achievement: данные достижения
            x, y: координаты верхнего левого угла карточки
            width, height: ширина и высота карточки
            color: цвет карточки
        """
        # Рисуем фон карточки
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color + (100,), card_rect, border_radius=10)
        pygame.draw.rect(self.screen, color, card_rect, width=2, border_radius=10)
        
        # Отрисовка названия достижения
        name_text = self.fonts['MEDIUM'].render(
            achievement['name'], 
            True, 
            COLORS['TEXT_LIGHT']
        )
        name_rect = name_text.get_rect(topleft=(x + 20, y + 15))
        self.screen.blit(name_text, name_rect)
        
        # Отрисовка описания достижения
        description_text = self.fonts['SMALL'].render(
            achievement['description'], 
            True, 
            COLORS['TEXT_LIGHT']
        )
        description_rect = description_text.get_rect(topleft=(x + 20, y + 50))
        self.screen.blit(description_text, description_rect)
        
        # Отрисовка статуса достижения
        status_text = self.fonts['SMALL'].render(
            self.localization.get_text('completed') if achievement['achieved'] else "...", 
            True, 
            COLORS['POSITIVE_GREEN'] if achievement['achieved'] else COLORS['TEXT_DARK']
        )
        status_rect = status_text.get_rect(bottomright=(x + width - 20, y + height - 15))
        self.screen.blit(status_text, status_rect)
        
        # Если достижение получено, рисуем значок (звездочку)
        if achievement['achieved']:
            # Позиция значка
            icon_size = 24
            icon_x = x + width - 50
            icon_y = y + 20
            
            # Рисуем звезду
            self._draw_star(icon_x, icon_y, icon_size, COLORS['ACCENT_YELLOW'])
            
    def _draw_star(self, x, y, size, color):
        """
        Отрисовка звезды
        
        Args:
            x, y: координаты центра звезды
            size: размер звезды
            color: цвет звезды
        """
        # Вершины пятиконечной звезды
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi * 2 / 10
            radius = size / 2 if i % 2 == 0 else size / 4
            points.append((
                x + radius * math.cos(angle),
                y - radius * math.sin(angle)
            ))
        
        # Рисуем звезду
        pygame.draw.polygon(self.screen, color, points)
