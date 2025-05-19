"""
Упражнение "Траектория" для приложения NeuroGym
Ребенок должен провести пальцем по заданной траектории, не выходя за границы
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

class Trajectory(BaseExercise):
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        """
        Инициализация упражнения "Траектория"
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen, difficulty)
        
        # Параметры траектории
        self.path_width = self._get_path_width_for_difficulty()
        self.path_type = self._get_path_type_for_difficulty()
        
        # Генерируем траекторию
        self.path_points = self._generate_path()
        
        # Параметры для отслеживания прогресса
        self.current_segment = 0
        self.progress = 0.0  # от 0 до 1
        self.is_on_path = True
        self.errors_count = 0
        self.max_errors = 10  # максимальное количество ошибок
        
        # Состояние курсора
        self.cursor_pos = None
        self.is_drawing = False
        self.path_complete = False
        
        # Точки начала и конца
        self.start_point = self.path_points[0]
        self.end_point = self.path_points[-1]
        
        # Область запуска и финиша
        self.start_radius = 30
        self.end_radius = 30
        
    def _get_path_width_for_difficulty(self):
        """
        Получение ширины пути в зависимости от уровня сложности
        
        Returns:
            int: ширина пути в пикселях
        """
        if self.difficulty == 'Легкий':
            return 60
        elif self.difficulty == 'Средний':
            return 40
        else:  # Сложный
            return 30
            
    def _get_path_type_for_difficulty(self):
        """
        Получение типа траектории в зависимости от уровня сложности
        
        Returns:
            str: тип траектории
        """
        if self.difficulty == 'Легкий':
            return 'line'
        elif self.difficulty == 'Средний':
            return 'wave'
        else:  # Сложный
            return 'complex'
            
    def _generate_path(self):
        """
        Генерация траектории в зависимости от выбранного типа
        
        Returns:
            list: список точек, определяющих траекторию [(x1, y1), (x2, y2), ...]
        """
        points = []
        
        # Определяем область для размещения траектории
        margin = 80  # отступ от краев экрана
        area_width = WINDOW_WIDTH - 2 * margin
        area_height = WINDOW_HEIGHT - 2 * margin
        
        if self.path_type == 'line':
            # Простая линия с небольшим изгибом
            start_x = margin
            end_x = WINDOW_WIDTH - margin
            mid_y = WINDOW_HEIGHT // 2
            
            # Создаем точки траектории
            num_points = 50
            for i in range(num_points + 1):
                progress = i / num_points
                x = start_x + (end_x - start_x) * progress
                
                # Небольшой изгиб вверх посередине
                y_offset = math.sin(progress * math.pi) * 50
                y = mid_y - y_offset
                
                points.append((x, y))
                
        elif self.path_type == 'wave':
            # Волнистая линия
            start_x = margin
            end_x = WINDOW_WIDTH - margin
            mid_y = WINDOW_HEIGHT // 2
            
            # Создаем точки траектории
            num_points = 100
            for i in range(num_points + 1):
                progress = i / num_points
                x = start_x + (end_x - start_x) * progress
                
                # Синусоидальная волна
                y_offset = math.sin(progress * 4 * math.pi) * 80
                y = mid_y + y_offset
                
                points.append((x, y))
                
        else:  # 'complex'
            # Сложная траектория с зигзагами и петлями
            start_x = margin
            end_x = WINDOW_WIDTH - margin
            mid_y = WINDOW_HEIGHT // 2
            
            # Создаем точки траектории
            num_points = 150
            for i in range(num_points + 1):
                progress = i / num_points
                x = start_x + (end_x - start_x) * progress
                
                # Комбинация синусоиды и более сложной функции
                y_offset = math.sin(progress * 6 * math.pi) * 70
                y_offset += math.cos(progress * 3 * math.pi) * 40
                y = mid_y + y_offset
                
                points.append((x, y))
        
        return points
        
    def _check_on_path(self, pos):
        """
        Проверка, находится ли курсор на траектории
        
        Args:
            pos: координаты курсора (x, y)
            
        Returns:
            bool: True, если курсор на траектории, иначе False
        """
        if not pos:
            return False
            
        # Находим ближайший сегмент траектории
        min_distance = float('inf')
        closest_segment = 0
        
        for i in range(len(self.path_points) - 1):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            
            # Вычисляем расстояние от точки до отрезка
            distance = self._point_to_segment_distance(pos, p1, p2)
            
            if distance < min_distance:
                min_distance = distance
                closest_segment = i
        
        # Проверяем, находится ли точка в пределах ширины пути
        is_on_path = min_distance <= self.path_width / 2
        
        # Обновляем текущий сегмент и прогресс
        if is_on_path:
            self.current_segment = closest_segment
            # Расчет прогресса прохождения (от 0 до 1)
            self.progress = (closest_segment + 1) / (len(self.path_points) - 1)
            
        return is_on_path
        
    def _point_to_segment_distance(self, p, v, w):
        """
        Вычисление расстояния от точки до отрезка
        
        Args:
            p: точка (x, y)
            v, w: концы отрезка (x1, y1), (x2, y2)
            
        Returns:
            float: расстояние от точки до отрезка
        """
        # Вектор v -> w
        l2 = ((w[0] - v[0]) ** 2 + (w[1] - v[1]) ** 2)
        if l2 == 0:  # v == w случай
            return math.sqrt((p[0] - v[0]) ** 2 + (p[1] - v[1]) ** 2)
            
        # Проекция точки p на отрезок v-w
        t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
        projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
        
        # Расстояние от точки до проекции
        return math.sqrt((p[0] - projection[0]) ** 2 + (p[1] - projection[1]) ** 2)
        
    def _check_path_completion(self):
        """
        Проверка завершения прохождения траектории
        
        Returns:
            bool: True, если траектория пройдена успешно, иначе False
        """
        if not self.cursor_pos:
            return False
            
        # Проверяем, находится ли курсор в конечной точке
        end_distance = math.sqrt(
            (self.cursor_pos[0] - self.end_point[0]) ** 2 + 
            (self.cursor_pos[1] - self.end_point[1]) ** 2
        )
        
        return end_distance <= self.end_radius
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Если упражнение завершено, обновлять ничего не нужно
        if self.path_complete:
            return
            
        # Проверка начала рисования
        if self.cursor_pos and not self.is_drawing:
            # Если курсор находится в стартовой точке, начинаем рисование
            start_distance = math.sqrt(
                (self.cursor_pos[0] - self.start_point[0]) ** 2 + 
                (self.cursor_pos[1] - self.start_point[1]) ** 2
            )
            
            if start_distance <= self.start_radius:
                self.is_drawing = True
        
        # Если идёт рисование, проверяем положение курсора
        if self.is_drawing and self.cursor_pos:
            # Проверяем, находится ли курсор на пути
            current_on_path = self._check_on_path(self.cursor_pos)
            
            # Если курсор сошел с пути, увеличиваем счетчик ошибок
            if self.is_on_path and not current_on_path:
                self.errors_count += 1
                
                # Если превышено максимальное количество ошибок, завершаем упражнение
                if self.errors_count >= self.max_errors:
                    self.is_drawing = False
                    # Рассчитываем финальный счет
                    self._calculate_final_score()
            
            self.is_on_path = current_on_path
            
            # Проверка завершения траектории
            if self._check_path_completion():
                self.path_complete = True
                self.is_drawing = False
                # Рассчитываем финальный счет
                self._calculate_final_score()
    
    def _calculate_final_score(self):
        """
        Расчет итогового счета на основе прогресса и количества ошибок
        """
        # Базовый счет зависит от процента прохождения пути
        base_score = int(self.progress * 100)
        
        # Штраф за ошибки
        error_penalty = min(50, self.errors_count * 5)
        
        # Итоговый счет
        final_score = max(0, base_score - error_penalty)
        
        # Если путь пройден до конца, добавляем бонус
        if self.path_complete:
            final_score += 20
            
        self.score = final_score
    
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        """
        # Рисуем фон траектории
        for i in range(len(self.path_points) - 1):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            
            # Рисуем сегмент пути
            self._draw_path_segment(p1, p2, self.path_width)
        
        # Рисуем стартовую точку
        pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'], self.start_point, self.start_radius)
        pygame.draw.circle(self.screen, COLORS['WHITE'], self.start_point, self.start_radius - 5)
        start_text = self.fonts['MEDIUM'].render("СТАРТ", True, COLORS['TEXT_DARK'])
        start_text_rect = start_text.get_rect(center=self.start_point)
        self.screen.blit(start_text, start_text_rect)
        
        # Рисуем конечную точку
        pygame.draw.circle(self.screen, COLORS['NEGATIVE_RED'], self.end_point, self.end_radius)
        pygame.draw.circle(self.screen, COLORS['WHITE'], self.end_point, self.end_radius - 5)
        finish_text = self.fonts['MEDIUM'].render("ФИНИШ", True, COLORS['TEXT_DARK'])
        finish_text_rect = finish_text.get_rect(center=self.end_point)
        self.screen.blit(finish_text, finish_text_rect)
        
        # Рисуем положение курсора
        if self.cursor_pos:
            # Цвет зависит от того, находится ли курсор на пути
            cursor_color = COLORS['POSITIVE_GREEN'] if self.is_on_path else COLORS['NEGATIVE_RED']
            cursor_size = 15
            
            pygame.draw.circle(self.screen, cursor_color, self.cursor_pos, cursor_size)
            pygame.draw.circle(self.screen, COLORS['WHITE'], self.cursor_pos, cursor_size // 2)
            
        # Отображение прогресса и ошибок
        progress_text = self.fonts['MEDIUM'].render(f"Прогресс: {int(self.progress * 100)}%", True, COLORS['TEXT_DARK'])
        progress_rect = progress_text.get_rect(topleft=(20, 20))
        self.screen.blit(progress_text, progress_rect)
        
        errors_text = self.fonts['MEDIUM'].render(f"Ошибки: {self.errors_count}/{self.max_errors}", True, COLORS['TEXT_DARK'])
        errors_rect = errors_text.get_rect(topleft=(20, 50))
        self.screen.blit(errors_text, errors_rect)
        
        # Сообщение о завершении
        if self.path_complete:
            complete_text = self.fonts['LARGE'].render("Траектория пройдена!", True, COLORS['POSITIVE_GREEN'])
            complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
            self.screen.blit(complete_text, complete_rect)
            
            score_text = self.fonts['LARGE'].render(f"Счёт: {self.score}", True, COLORS['PRIMARY_BLUE'])
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4 + 50))
            self.screen.blit(score_text, score_rect)
            
    def _draw_path_segment(self, p1, p2, width):
        """
        Отрисовка сегмента пути
        
        Args:
            p1, p2: точки начала и конца сегмента
            width: ширина пути
        """
        # Вычисляем вектор направления
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        # Нормализуем
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length
            
        # Перпендикулярный вектор
        px = -dy
        py = dx
        
        # Вычисляем четыре угла прямоугольника, представляющего сегмент
        half_width = width / 2
        points = [
            (p1[0] + px * half_width, p1[1] + py * half_width),
            (p2[0] + px * half_width, p2[1] + py * half_width),
            (p2[0] - px * half_width, p2[1] - py * half_width),
            (p1[0] - px * half_width, p1[1] - py * half_width)
        ]
        
        # Рисуем сегмент пути
        path_color = COLORS['PRIMARY_BLUE'] + (150,)  # полупрозрачный цвет
        pygame.draw.polygon(self.screen, path_color, points)
        
        # Рисуем границы
        border_color = COLORS['ACCENT_YELLOW']
        pygame.draw.line(self.screen, border_color, 
                       (p1[0] + px * half_width, p1[1] + py * half_width),
                       (p2[0] + px * half_width, p2[1] + py * half_width), 2)
        pygame.draw.line(self.screen, border_color, 
                       (p2[0] - px * half_width, p2[1] - py * half_width),
                       (p1[0] - px * half_width, p1[1] - py * half_width), 2)
        
    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий упражнения
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        super().handle_events(events, cursor_pos)
        
        # Если упражнение на паузе, обрабатываем только базовые события
        if self.is_paused:
            return
            
        # Обновляем положение курсора
        if cursor_pos:
            self.cursor_pos = cursor_pos
        else:
            # Если жесты не используются, получаем позицию мыши
            self.cursor_pos = pygame.mouse.get_pos()
