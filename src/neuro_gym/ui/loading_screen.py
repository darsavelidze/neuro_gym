"""
Экран загрузки для приложения NeuroGym
Отображается при запуске приложения и во время загрузки ресурсов
"""

import pygame
import time
from .base_screen import BaseScreen
from ..config import COLORS, VERSION

class LoadingScreen(BaseScreen):
    def __init__(self, screen_manager, screen):
        """
        Инициализация экрана загрузки
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
        """
        super().__init__(screen_manager, screen)
        
        # Время создания экрана (для расчета анимации)
        self.start_time = time.time()
        
        # Минимальное время отображения экрана загрузки (в секундах)
        self.min_display_time = 2.0
        
        # Текущий прогресс загрузки (от 0 до 1)
        self.progress = 0
        
        # Ресурсы для загрузки (имитация)
        self.resources_to_load = ['textures', 'sounds', 'fonts', 'exercises']
        self.current_resource_index = 0
        
    def update(self, dt):
        """
        Обновление экрана загрузки
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Рассчитываем прогресс загрузки
        elapsed_time = time.time() - self.start_time
        
        # Имитация загрузки ресурсов
        if elapsed_time > self.current_resource_index * 0.5:
            # Переходим к следующему ресурсу
            if self.current_resource_index < len(self.resources_to_load):
                self.current_resource_index += 1
        
        # Обновляем прогресс на основе загруженных ресурсов
        self.progress = min(1.0, self.current_resource_index / len(self.resources_to_load))
        
        # Если все ресурсы загружены и прошло минимальное время, переходим в главное меню
        if self.progress >= 1.0 and elapsed_time >= self.min_display_time:
            self.transition_to('main_menu')
        
    def draw(self):
        """
        Отрисовка экрана загрузки
        """
        # Заливка экрана основным цветом
        self.screen.fill(COLORS['PRIMARY_BLUE'])
        
        # Отрисовка заголовка
        title_text = self.fonts['EXTRA_LARGE'].render("NeuroGym", True, COLORS['TEXT_LIGHT'])
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка строки загрузки
        progress_bar_width = int(self.width * 0.6)
        progress_bar_height = 30
        progress_bar_x = (self.width - progress_bar_width) // 2
        progress_bar_y = self.height // 2 + 40
        
        # Фон полосы загрузки
        pygame.draw.rect(self.screen, COLORS['BLACK'], 
                        (progress_bar_x - 2, progress_bar_y - 2, 
                         progress_bar_width + 4, progress_bar_height + 4))
        
        # Полоса загрузки (заполненная часть)
        filled_width = int(progress_bar_width * self.progress)
        pygame.draw.rect(self.screen, COLORS['ACCENT_YELLOW'], 
                        (progress_bar_x, progress_bar_y, 
                         filled_width, progress_bar_height))
        
        # Отображение текущего элемента загрузки
        if self.current_resource_index < len(self.resources_to_load):
            loading_text = f"Загрузка: {self.resources_to_load[self.current_resource_index]}..."
        else:
            loading_text = "Загрузка завершена"
            
        loading_surface = self.fonts['SMALL'].render(loading_text, True, COLORS['TEXT_LIGHT'])
        loading_rect = loading_surface.get_rect(center=(self.width // 2, progress_bar_y + 50))
        self.screen.blit(loading_surface, loading_rect)
        
        # Отображение версии приложения
        version_surface = self.fonts['SMALL'].render(f"v{VERSION}", True, COLORS['TEXT_LIGHT'])
        version_rect = version_surface.get_rect(bottomright=(self.width - 20, self.height - 20))
        self.screen.blit(version_surface, version_rect)
