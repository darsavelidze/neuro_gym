"""
Экран результатов упражнения для приложения NeuroGym
Отображается после завершения упражнения и показывает статистику
"""

import pygame
import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from ui.base_screen import BaseScreen
from config import COLORS, SCREEN_PADDING

class ResultsScreen(BaseScreen):
    def __init__(self, screen_manager, screen, exercise_id=None, score=0, accuracy=0, duration=0):
        """
        Инициализация экрана результатов
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            exercise_id: идентификатор завершенного упражнения
            score: набранные очки
            accuracy: точность выполнения (процент)
            duration: затраченное время (секунды)
        """
        super().__init__(screen_manager, screen)
        
        # Результаты упражнения
        self.exercise_id = exercise_id
        self.score = score
        self.accuracy = accuracy
        self.duration = duration
        
        # Рассчитываем количество звезд на основе точности
        self.stars = self._calculate_stars()
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _calculate_stars(self):
        """
        Расчет количества заработанных звезд на основе точности выполнения
        
        Returns:
            int: количество звезд (от 0 до 3)
        """
        if self.accuracy >= 90:
            return 3
        elif self.accuracy >= 70:
            return 2
        elif self.accuracy >= 50:
            return 1
        else:
            return 0
            
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса экрана результатов
        """
        # Очистка кнопок
        self.buttons = []
        
        # Кнопки
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = self.height - button_height * 2 - button_spacing - SCREEN_PADDING
        
        # Центрирование кнопок по горизонтали
        button_x = (self.width - button_width) // 2
        
        # Кнопка "Повторить"
        self.create_button(
            "Повторить", 
            button_x, start_y, 
            button_width, button_height, 
            action=self._restart_exercise,
            font_size='MEDIUM'
        )
        
        # Кнопка "Вернуться в меню"
        self.create_button(
            "В главное меню", 
            button_x, start_y + button_height + button_spacing, 
            button_width, button_height, 
            action=lambda: self.transition_to('main_menu'),
            font_size='MEDIUM'
        )
        
    def _restart_exercise(self):
        """
        Перезапуск упражнения
        """
        if self.exercise_id:
            # Переход к упражнению без показа инструкций
            self.transition_to(self.exercise_id)
        else:
            # Если идентификатор упражнения не задан, возвращаемся в меню выбора упражнений
            self.transition_to('exercise_selection')
            
    def update(self, dt):
        """
        Обновление экрана результатов
        
        Args:
            dt: время в секундах с последнего обновления
        """
        pass
        
    def draw(self):
        """
        Отрисовка экрана результатов
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Отрисовка заголовка
        title_text = self.fonts['LARGE'].render("Результаты", True, COLORS['PRIMARY_BLUE'])
        title_rect = title_text.get_rect(center=(self.width // 2, SCREEN_PADDING + 50))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка звезд
        self._draw_stars()
        
        # Отрисовка статистики
        self._draw_statistics()
        
        # Отрисовка поздравления
        self._draw_congratulation()
        
        # Отрисовка кнопок
        self.draw_buttons()
        
    def _draw_stars(self):
        """
        Отрисовка полученных звезд
        """
        # Параметры звезд
        star_size = 60
        star_spacing = 20
        total_width = 3 * star_size + 2 * star_spacing
        start_x = (self.width - total_width) // 2
        star_y = self.height // 4
        
        for i in range(3):
            # Позиция текущей звезды
            star_x = start_x + i * (star_size + star_spacing)
            
            # Цвет звезды (желтый для заработанных, серый для незаработанных)
            star_color = COLORS['ACCENT_YELLOW'] if i < self.stars else COLORS['PRIMARY_BLUE'] + (80,)
            
            # Рисуем звезду (упрощенный вариант, в виде круга)
            pygame.draw.circle(
                self.screen,
                star_color,
                (star_x + star_size // 2, star_y),
                star_size // 2
            )
            
    def _draw_statistics(self):
        """
        Отрисовка статистики выполнения упражнения
        """
        # Параметры текста статистики
        text_y = self.height // 4 + 100
        text_spacing = 40
        
        # Отрисовка счета
        score_text = self.fonts['MEDIUM'].render(f"Набрано очков: {self.score}", True, COLORS['TEXT_DARK'])
        score_rect = score_text.get_rect(center=(self.width // 2, text_y))
        self.screen.blit(score_text, score_rect)
        
        # Отрисовка точности
        accuracy_text = self.fonts['MEDIUM'].render(f"Точность выполнения: {self.accuracy:.1f}%", True, COLORS['TEXT_DARK'])
        accuracy_rect = accuracy_text.get_rect(center=(self.width // 2, text_y + text_spacing))
        self.screen.blit(accuracy_text, accuracy_rect)
        
        # Отрисовка времени
        minutes = int(self.duration) // 60
        seconds = int(self.duration) % 60
        time_text = self.fonts['MEDIUM'].render(f"Затраченное время: {minutes:02d}:{seconds:02d}", True, COLORS['TEXT_DARK'])
        time_rect = time_text.get_rect(center=(self.width // 2, text_y + 2 * text_spacing))
        self.screen.blit(time_text, time_rect)
        
    def _draw_congratulation(self):
        """
        Отрисовка поздравления в зависимости от результата
        """
        # Выбор текста поздравления в зависимости от количества звезд
        if self.stars == 3:
            message = "Отличная работа! Ты справился на все звезды!"
            color = COLORS['POSITIVE_GREEN']
        elif self.stars == 2:
            message = "Хороший результат! Попробуй еще раз!"
            color = COLORS['PRIMARY_BLUE']
        elif self.stars == 1:
            message = "Неплохо! С практикой будет лучше!"
            color = COLORS['ACCENT_YELLOW']
        else:
            message = "Попробуй еще раз, у тебя получится!"
            color = COLORS['NEGATIVE_RED']
            
        # Отрисовка поздравительного сообщения
        message_text = self.fonts['LARGE'].render(message, True, color)
        message_rect = message_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(message_text, message_rect)
