"""
Упражнение "Запоминание последовательности" для приложения NeuroGym
Ребенок должен запомнить и повторить последовательность подсвеченных объектов
"""

import pygame
import math
import random

from .base_exercise import BaseExercise
from ..config import COLORS, SCREEN_PADDING
from ..core.exercise_config import get_exercise_setting
from ..ui.utils.draw import draw_hint
class Sequence(BaseExercise):
    exercise_id = 'sequence'
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        """
        Инициализация упражнения "Запоминание последовательности"
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen, difficulty)
        self._load_settings()
        self._init_resources()
        self._reset_state()

    def _load_settings(self):
        self.grid_size = get_exercise_setting(self.exercise_id, self.difficulty, 'grid_size', 3)
        self.sequence_length = get_exercise_setting(self.exercise_id, self.difficulty, 'sequence_length', 3)
        self.display_time = get_exercise_setting(self.exercise_id, self.difficulty, 'display_time', 1.0)

    def _init_resources(self):
        """Инициализация ресурсов (шрифты наследуются от BaseScreen)."""
        pass

    def _reset_state(self):
        self.sequence = []
        self.user_input = []
        self.message = "Нажмите цифры в правильной последовательности"
        self.message_timer = 0
        self.highlighted_buttons = []
        self.highlight_timer = 0
        self.animation_time = 0
        self.flash_cell = None
        self.flash_type = None
        self.flash_timer = 0
        self.game_state = 'display'
        self.display_index = 0
        self.input_index = 0
        self.display_timer = 0
        self.pause_timer = 0
        self.level = 1
        self.max_level = 5
        self.errors = 0
        self.grid = self._create_grid()
        self.sequence = self._generate_sequence()

    def on_enter(self, params=None):
        super().on_enter(params)
        self._load_settings()
        self._reset_state()
        
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
        start_x = (self.width - grid_pixel_size) // 2
        start_y = (self.height - grid_pixel_size) // 2
        
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
        difficulty_bonus = get_exercise_setting(self.exercise_id, self.difficulty, 'difficulty_bonus', 0)
        
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
                # Показываем элемент или делаем паузу
                if self.display_timer > 0:
                    # Элемент активно показывается
                    self.display_timer -= dt
                    if self.display_timer <= 0:
                        # Убираем подсветку и начинаем паузу
                        self.flash_cell = None
                        self.pause_timer = 0.3  # пауза между элементами
                elif self.pause_timer > 0:
                    # Пауза между элементами
                    self.pause_timer -= dt
                    if self.pause_timer <= 0:
                        # Переходим к следующему элементу
                        self.display_index += 1
                else:
                    # Начинаем показывать текущий элемент
                    row, col = self.sequence[self.display_index]
                    self._flash_cell(row, col, 'active')
                    self.display_timer = self.display_time
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
                
        # Если все уровни пройдены, отображаем итоговый результат
        if self.game_state == 'success':
            result_bg = pygame.Rect(
                self.width // 4,
                self.height // 4,
                self.width // 2,
                self.height // 3
            )
            pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (200,), result_bg, border_radius=15)
            
            success_text = self.fonts['LARGE'].render("Поздравляем!", True, COLORS['TEXT_LIGHT'])
            success_rect = success_text.get_rect(center=(self.width // 2, result_bg.y + 40))
            self.screen.blit(success_text, success_rect)
            
            score_text = self.fonts['LARGE'].render(f"Счёт: {self.score}", True, COLORS['TEXT_LIGHT'])
            score_rect = score_text.get_rect(center=(self.width // 2, result_bg.y + 100))
            self.screen.blit(score_text, score_rect)

    def _draw_extra_hud(self, y_start):
        """Единый стиль HUD: уровень, ошибки и подсказка состояния."""
        loc = getattr(self, 'localization', None)
        level_label = loc.get_text('level') if loc else 'Уровень'
        errors_label = loc.get_text('errors') if loc else 'Ошибки'
        remember_label = loc.get_text('remember_sequence') if loc else "Запоминайте последовательность..."
        repeat_label = loc.get_text('repeat_sequence') if loc else "Повторите последовательность"
        all_done_label = loc.get_text('all_levels_done') if loc else "Все уровни пройдены!"

        level_text = self.fonts['MEDIUM'].render(
            f"{level_label}: {self.level}/{self.max_level}", True, COLORS['TEXT_DARK']
        )
        level_rect = level_text.get_rect(topleft=(20, y_start))
        self.screen.blit(level_text, level_rect)

        errors_text = self.fonts['MEDIUM'].render(f"{errors_label}: {self.errors}", True, COLORS['TEXT_DARK'])
        errors_rect = errors_text.get_rect(topleft=(20, level_rect.bottom + 8))
        self.screen.blit(errors_text, errors_rect)

        hint_text = ""
        if self.game_state == 'display':
            hint_text = remember_label
        elif self.game_state == 'input':
            hint_text = f"{repeat_label} ({self.input_index + 1}/{len(self.sequence)})"
        elif self.game_state == 'success':
            hint_text = all_done_label

        if hint_text:
            draw_hint(self.screen, self.fonts['LARGE'], hint_text, y_start + 80)
            
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
        mouse_pos = cursor_pos if cursor_pos else self._get_cursor_position()
        
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
