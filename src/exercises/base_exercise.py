"""
Базовый класс упражнения для приложения NeuroGym
Все упражнения должны наследоваться от этого класса
"""

import pygame
import sys
import time
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from ui.base_screen import BaseScreen
from config import COLORS, EXERCISE_DURATION, SCREEN_PADDING

class BaseExercise(BaseScreen):
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        """
        Инициализация базового класса упражнения
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen)
        
        # Уровень сложности упражнения
        self.difficulty = difficulty
        
        # Счет и прогресс
        self.score = 0
        self.max_score = 100
        self.accuracy = 100.0  # процент точности выполнения
        
        # Таймер упражнения
        self.start_time = time.time()
        self.elapsed_time = 0
        self.duration = EXERCISE_DURATION  # длительность упражнения в секундах
        
        # Состояние упражнения
        self.is_paused = False
        self.is_completed = False
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса упражнения
        """
        # Очистка кнопок
        self.buttons = []
        
        # Кнопка паузы
        pause_size = 40
        pause_x = self.width - pause_size - SCREEN_PADDING
        pause_y = SCREEN_PADDING
        
        self.create_button(
            "II", 
            pause_x, pause_y, 
            pause_size, pause_size, 
            action=self._toggle_pause,
            font_size='MEDIUM'
        )
        
    def _toggle_pause(self):
        """
        Переключение состояния паузы
        """
        self.is_paused = not self.is_paused
        
        # Если упражнение на паузе, показываем дополнительные кнопки
        if self.is_paused:
            self._create_pause_ui()
        else:
            # Если упражнение продолжается, возвращаемся к стандартным кнопкам
            self._create_ui_elements()
            
    def _create_pause_ui(self):
        """
        Создание UI для состояния паузы
        """
        # Очистка кнопок
        self.buttons = []
        
        # Размеры и расположение кнопок
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = self.height // 2 - button_height
        
        # Центрирование кнопок по горизонтали
        button_x = (self.width - button_width) // 2
        
        # Кнопка "Продолжить"
        self.create_button(
            "Продолжить", 
            button_x, start_y, 
            button_width, button_height, 
            action=self._toggle_pause,
            color=COLORS['POSITIVE_GREEN'],
            font_size='MEDIUM'
        )
        
        # Кнопка "Начать заново"
        self.create_button(
            "Начать заново", 
            button_x, start_y + button_height + button_spacing, 
            button_width, button_height,
            action=self._restart_exercise,
            font_size='MEDIUM'
        )
        
        # Кнопка "Выход в меню"
        self.create_button(
            "Выход в меню", 
            button_x, start_y + 2 * (button_height + button_spacing), 
            button_width, button_height,
            action=self._exit_to_menu,
            font_size='MEDIUM'
        )
        
    def _restart_exercise(self):
        """
        Перезапуск упражнения
        """
        # Сбрасываем все параметры упражнения
        self.score = 0
        self.accuracy = 100.0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.is_paused = False
        self.is_completed = False
        
        # Возвращаем стандартный UI
        self._create_ui_elements()
        
    def _exit_to_menu(self):
        """
        Выход в главное меню
        """
        # Показываем диалог подтверждения
        # В реальном приложении здесь должен быть диалог
        self.transition_to('main_menu')
        
    def _complete_exercise(self):
        """
        Завершение упражнения и переход к экрану результатов
        """
        self.is_completed = True
        
        # В реальном приложении здесь должен быть переход к экрану результатов
        # с передачей данных об упражнении
        self.transition_to('results')
        
    def update(self, dt):
        """
        Обновление состояния упражнения
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Если упражнение на паузе или уже завершено, ничего не делаем
        if self.is_paused or self.is_completed:
            return
            
        # Обновление времени
        self.elapsed_time = time.time() - self.start_time
        
        # Проверка на завершение времени упражнения
        if self.elapsed_time >= self.duration:
            self._complete_exercise()
            
        # Специфичная для упражнения логика будет в классе-наследнике
        self._exercise_specific_update(dt)
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        Должно быть переопределено в классе-наследнике
        
        Args:
            dt: время в секундах с последнего обновления
        """
        pass
        
    def draw(self):
        """
        Отрисовка упражнения
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Если упражнение на паузе, затемняем игровую область
        if self.is_paused:
            # Создаем полупрозрачную поверхность
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # черный цвет с альфа-каналом 128 (полупрозрачный)
            self.screen.blit(overlay, (0, 0))
            
            # Отрисовка заголовка паузы
            pause_text = self.fonts['LARGE'].render("Пауза", True, COLORS['TEXT_LIGHT'])
            pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 4))
            self.screen.blit(pause_text, pause_rect)
        else:
            # Отрисовка игровой области (будет переопределена в классе-наследнике)
            self._draw_exercise_area()
            
            # Отрисовка информационной панели (счет, таймер)
            self._draw_info_panel()
        
        # Отрисовка кнопок
        self.draw_buttons()
        
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        Должна быть переопределена в классе-наследнике
        """
        pass
        
    def _draw_info_panel(self):
        """
        Отрисовка информационной панели
        """
        # Отрисовка счета
        score_text = self.fonts['MEDIUM'].render(f"Счет: {self.score}", True, COLORS['TEXT_DARK'])
        score_rect = score_text.get_rect(topleft=(SCREEN_PADDING, SCREEN_PADDING))
        self.screen.blit(score_text, score_rect)
        
        # Отрисовка таймера
        remaining_time = max(0, self.duration - self.elapsed_time)
        minutes = int(remaining_time) // 60
        seconds = int(remaining_time) % 60
        time_text = self.fonts['MEDIUM'].render(f"Время: {minutes:02d}:{seconds:02d}", True, COLORS['TEXT_DARK'])
        time_rect = time_text.get_rect(topright=(self.width - SCREEN_PADDING - 50, SCREEN_PADDING))
        self.screen.blit(time_text, time_rect)