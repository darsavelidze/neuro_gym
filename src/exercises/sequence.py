"""
Упражнение "Запоминание последовательности" для приложения NeuroGym
Ребенок должен запомнить и повторить последовательность подсвеченных объектов
"""

import pygame
import sys
import math
import random
import os
import time

# Добавляем корневой каталог проекта в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(src_dir)

from exercises.base_exercise import BaseExercise
from config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT

class Sequence(BaseExercise):
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        """
        Инициализация упражнения "Запоминание последовательности"
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen, difficulty)
        
        # Параметры упражнения в зависимости от сложности
        self.grid_size = self._get_grid_size_for_difficulty()
        self.sequence_length = self._get_sequence_length_for_difficulty()
        self.display_time = self._get_display_time_for_difficulty()
        
        # Создание игровой сетки
        self.grid = self._create_grid()
        
        # Генерация последовательности
        self.sequence = self._generate_sequence()
        
        # Состояние игры
        self.game_state = 'display'  # 'display', 'input', 'success', 'failure'
        self.display_index = 0       # текущий индекс отображаемого элемента последовательности
        self.input_index = 0         # текущий индекс ожидаемого ввода
        self.display_timer = 0       # таймер для отображения элементов последовательности
        self.pause_timer = 0         # таймер для паузы между элементами
        self.level = 1               # текущий уровень
        self.max_level = 5           # максимальное количество уровней
        self.errors = 0              # счетчик ошибок
        
        # Анимация
        self.animation_time = 0      # время для анимационных эффектов
        self.flash_cell = None       # ячейка для эффекта вспышки
        self.flash_type = None       # тип вспышки ('correct' или 'error')
        self.flash_timer = 0         # таймер эффекта вспышки
        
    def _get_grid_size_for_difficulty(self):
        """
        Определение размера сетки в зависимости от уровня сложности
        
        Returns:
            int: размер сетки (NxN)
        """
        if self.difficulty == 'Легкий':
            return 3  # сетка 3x3
        elif self.difficulty == 'Средний':
            return 4  # сетка 4x4
        else:  # Сложный
            return 5  # сетка 5x5
            
    def _get_sequence_length_for_difficulty(self):
        """
        Определение начальной длины последовательности в зависимости от уровня сложности
        
        Returns:
            int: длина последовательности
        """
        if self.difficulty == 'Легкий':
            return 3
        elif self.difficulty == 'Средний':
            return 4
        else:  # Сложный
            return 5
            
    def _get_display_time_for_difficulty(self):
        """
        Определение времени отображения ячейки в последовательности
        
        Returns:
            float: время в секундах
        """
        if self.difficulty == 'Легкий':
            return 1.0  # 1 секунда
        elif self.difficulty == 'Средний':
            return 0.8  # 0.8 секунды
        else:  # Сложный
            return 0.6  # 0.6 секунды
            
    def _create_grid(self):
        """
        Создание игровой сетки
        
        Returns:
            list: двумерный список ячеек сетки
        """
        grid = []
        
        # Размер ячейки
        cell_size = 70
        cell_spacing = 15
        
        # Общий размер сетки
        grid_pixel_size = self.grid_size * cell_size + (self.grid_size - 1) * cell_spacing
        
        # Позиция верхнего левого угла сетки (центрирование)
        start_x = (WINDOW_WIDTH - grid_pixel_size) // 2
        start_y = (WINDOW_HEIGHT - grid_pixel_size) // 2
        
        # Создание ячеек
        for row in range(self.grid_size):
            grid_row = []
            for col in range(self.grid_size):
                cell_x = start_x + col * (cell_size + cell_spacing)
                cell_y = start_y + row * (cell_size + cell_spacing)
                
                cell = {
                    'rect': pygame.Rect(cell_x, cell_y, cell_size, cell_size),
                    'state': 'idle',  # 'idle', 'active', 'correct', 'error'
                    'animation': 0,   # для анимационных эффектов
                    'row': row,
                    'col': col
                }
                
                grid_row.append(cell)
            grid.append(grid_row)
            
        return grid
        
    def _generate_sequence(self):
        """
        Генерация случайной последовательности ячеек
        
        Returns:
            list: список кортежей (row, col) с координатами ячеек
        """
        current_length = self.sequence_length + (self.level - 1)
        sequence = []
        
        # Генерируем последовательность случайных ячеек
        for _ in range(current_length):
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)
            
            # Избегаем повторения одной и той же ячейки подряд
            if sequence and sequence[-1] == (row, col):
                while sequence[-1] == (row, col):
                    row = random.randint(0, self.grid_size - 1)
                    col = random.randint(0, self.grid_size - 1)
                    
            sequence.append((row, col))
            
        return sequence
        
    def _start_next_level(self):
        """
        Переход к следующему уровню
        """
        self.level += 1
        self.display_index = 0
        self.input_index = 0
        self.game_state = 'display'
        
        # Генерируем новую последовательность
        self.sequence = self._generate_sequence()
        
        # Сбрасываем таймеры
        self.display_timer = 0
        self.pause_timer = 0
        
    def _restart_level(self):
        """
        Перезапуск текущего уровня
        """
        # Увеличиваем счетчик ошибок
        self.errors += 1
        
        # Сбрасываем индексы
        self.display_index = 0
        self.input_index = 0
        self.game_state = 'display'
        
        # Генерируем новую последовательность
        self.sequence = self._generate_sequence()
        
        # Сбрасываем таймеры
        self.display_timer = 0
        self.pause_timer = 0
        
    def _calculate_final_score(self):
        """
        Расчет итогового счета
        """
        # Базовый счет на основе пройденных уровней
        base_score = (self.level - 1) * 20
        
        # Штраф за ошибки
        error_penalty = min(60, self.errors * 15)
        
        # Бонус за сложность
        difficulty_bonus = {'Легкий': 0, 'Средний': 10, 'Сложный': 20}[self.difficulty]
        
        # Итоговый счет
        final_score = max(0, base_score - error_penalty + difficulty_bonus)
        
        self.score = min(100, final_score)  # Максимальная оценка - 100
        
    def _check_cell_click(self, pos):
        """
        Проверка клика по ячейке сетки
        
        Args:
            pos: координаты клика (x, y)
            
        Returns:
            tuple: (row, col) или None, если клик не по ячейке
        """
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col]['rect'].collidepoint(pos):
                    return (row, col)
                    
        return None
        
    def _flash_cell(self, row, col, flash_type):
        """
        Установка эффекта вспышки для ячейки
        
        Args:
            row, col: координаты ячейки
            flash_type: тип вспышки ('active', 'correct', 'error')
        """
        self.flash_cell = (row, col)
        self.flash_type = flash_type
        self.flash_timer = 0.3  # длительность вспышки в секундах
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновление времени анимации
        self.animation_time += dt
        
        # Обновление таймера вспышки
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_cell = None
                self.flash_type = None
        
        # Обработка состояний игры
        if self.game_state == 'display':
            # Режим отображения последовательности
            if self.display_index < len(self.sequence):
                # Продолжаем показывать текущий элемент
                if self.pause_timer > 0:
                    self.pause_timer -= dt
                    if self.pause_timer <= 0:
                        # Показываем следующий элемент
                        row, col = self.sequence[self.display_index]
                        self._flash_cell(row, col, 'active')
                        self.display_timer = self.display_time
                        self.display_index += 1
                else:
                    if self.display_timer > 0:
                        self.display_timer -= dt
                        if self.display_timer <= 0:
                            # Пауза перед следующим элементом
                            self.pause_timer = 0.2  # пауза между элементами
            else:
                # Последовательность показана, переходим к вводу
                self.game_state = 'input'
                self.input_index = 0
                
        # Проверка завершения игры
        if self.level > self.max_level:
            self.game_state = 'success'
            self._calculate_final_score()
            
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        """
        # Отрисовка фона для сетки
        grid_bg = pygame.Rect(
            self.grid[0][0]['rect'].x - 20,
            self.grid[0][0]['rect'].y - 20,
            self.grid_size * self.grid[0][0]['rect'].width + (self.grid_size - 1) * 15 + 40,
            self.grid_size * self.grid[0][0]['rect'].height + (self.grid_size - 1) * 15 + 40
        )
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (50,), grid_bg, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'], grid_bg, width=2, border_radius=15)
        
        # Отрисовка сетки
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid[row][col]
                
                # Определение цвета ячейки
                cell_color = COLORS['PRIMARY_BLUE'] + (150,)  # стандартный цвет
                
                # Если ячейка находится в эффекте вспышки
                if self.flash_cell and self.flash_cell == (row, col):
                    if self.flash_type == 'active':
                        cell_color = COLORS['ACCENT_YELLOW']
                    elif self.flash_type == 'correct':
                        cell_color = COLORS['POSITIVE_GREEN']
                    elif self.flash_type == 'error':
                        cell_color = COLORS['NEGATIVE_RED']
                
                # Отрисовка тени для ячейки
                shadow_rect = cell['rect'].copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=8)
                
                # Отрисовка ячейки
                pygame.draw.rect(self.screen, cell_color, cell['rect'], border_radius=8)
                
                # Добавляем объемность ячейке
                highlight_rect = pygame.Rect(
                    cell['rect'].x,
                    cell['rect'].y,
                    cell['rect'].width,
                    cell['rect'].height // 3
                )
                pygame.draw.rect(self.screen, (255, 255, 255, 30), highlight_rect, border_radius=8)
                
        # Отображение информации о текущем уровне и ошибках
        level_text = self.fonts['MEDIUM'].render(f"Уровень: {self.level}/{self.max_level}", True, COLORS['TEXT_DARK'])
        level_rect = level_text.get_rect(topleft=(20, 20))
        self.screen.blit(level_text, level_rect)
        
        errors_text = self.fonts['MEDIUM'].render(f"Ошибки: {self.errors}", True, COLORS['TEXT_DARK'])
        errors_rect = errors_text.get_rect(topleft=(20, 50))
        self.screen.blit(errors_text, errors_rect)
        
        # Отображение подсказки в зависимости от режима игры
        hint_text = ""
        if self.game_state == 'display':
            hint_text = "Запоминайте последовательность..."
        elif self.game_state == 'input':
            hint_text = f"Повторите последовательность ({self.input_index}/{len(self.sequence)})"
        elif self.game_state == 'success':
            hint_text = "Отлично! Все уровни пройдены!"
        
        hint = self.fonts['MEDIUM'].render(hint_text, True, COLORS['TEXT_DARK'])
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(hint, hint_rect)
        
        # Если все уровни пройдены, отображаем итоговый результат
        if self.game_state == 'success':
            result_bg = pygame.Rect(
                WINDOW_WIDTH // 4,
                WINDOW_HEIGHT // 4,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 3
            )
            pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (200,), result_bg, border_radius=15)
            
            success_text = self.fonts['LARGE'].render("Поздравляем!", True, COLORS['TEXT_LIGHT'])
            success_rect = success_text.get_rect(center=(WINDOW_WIDTH // 2, result_bg.y + 40))
            self.screen.blit(success_text, success_rect)
            
            score_text = self.fonts['LARGE'].render(f"Счёт: {self.score}", True, COLORS['TEXT_LIGHT'])
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, result_bg.y + 100))
            self.screen.blit(score_text, score_rect)
            
    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий упражнения
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        super().handle_events(events, cursor_pos)
        
        # Если упражнение на паузе или завершено, обрабатываем только базовые события
        if self.is_paused or self.game_state == 'success':
            return
            
        # Используем позицию мыши или жестов
        mouse_pos = cursor_pos if cursor_pos else pygame.mouse.get_pos()
        
        for event in events:
            # Обработка клика по ячейкам в режиме ввода
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.game_state == 'input':
                cell_coords = self._check_cell_click(mouse_pos)
                if cell_coords:
                    row, col = cell_coords
                    
                    # Проверяем, совпадает ли выбранная ячейка с ожидаемой
                    expected_row, expected_col = self.sequence[self.input_index]
                    
                    if row == expected_row and col == expected_col:
                        # Правильный выбор
                        self._flash_cell(row, col, 'correct')
                        self.input_index += 1
                        
                        # Проверяем, вся ли последовательность введена
                        if self.input_index >= len(self.sequence):
                            # Последовательность введена верно
                            if self.level >= self.max_level:
                                # Все уровни пройдены
                                self.game_state = 'success'
                                self._calculate_final_score()
                            else:
                                # Переход к следующему уровню
                                self._start_next_level()
                    else:
                        # Неправильный выбор
                        self._flash_cell(row, col, 'error')
                        
                        # Перезапуск уровня
                        self._restart_level()
