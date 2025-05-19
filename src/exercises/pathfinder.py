"""
Упражнение "Следопыт" для приложения NeuroGym
Ребенок должен следить за движущимся объектом указательным пальцем
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

# Импортируем базовый класс напрямую
from exercises.base_exercise import BaseExercise
from config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT

class Pathfinder(BaseExercise):
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        """
        Инициализация упражнения "Следопыт"
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen, difficulty)
        
        # Параметры объекта слежения
        self.object_size = 40
        self.object_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2]
        self.object_speed = self._get_speed_for_difficulty()
        self.object_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self._normalize_direction()
        
        # Статистика слежения
        self.tracking_accuracy = 100.0
        self.tracking_history = []  # история расстояний между объектом и курсором
        self.max_history_length = 100  # максимальная длина истории для расчета точности
        
        # Допустимая область отклонения (радиус вокруг объекта)
        self.allowed_deviation = self._get_deviation_for_difficulty()
        
        # Траектория движения (для сложных уровней)
        self.trajectory_type = self._get_trajectory_for_difficulty()
        self.trajectory_timer = 0
        self.trajectory_change_interval = 3.0  # время между изменениями траектории (секунды)
        
    def _get_speed_for_difficulty(self):
        """
        Получение скорости объекта в зависимости от уровня сложности
        
        Returns:
            float: скорость объекта (пикселей в секунду)
        """
        if self.difficulty == 'Легкий':
            return 100.0
        elif self.difficulty == 'Средний':
            return 150.0
        else:  # Сложный
            return 200.0
            
    def _get_deviation_for_difficulty(self):
        """
        Получение допустимой области отклонения в зависимости от уровня сложности
        
        Returns:
            int: радиус допустимой области в пикселях
        """
        if self.difficulty == 'Легкий':
            return self.object_size * 2
        elif self.difficulty == 'Средний':
            return self.object_size * 1.5
        else:  # Сложный
            return self.object_size
            
    def _get_trajectory_for_difficulty(self):
        """
        Получение типа траектории в зависимости от уровня сложности
        
        Returns:
            str: тип траектории
        """
        if self.difficulty == 'Легкий':
            return 'linear'
        elif self.difficulty == 'Средний':
            return 'circular'
        else:  # Сложный
            return 'random'
            
    def _normalize_direction(self):
        """
        Нормализация вектора направления движения объекта
        """
        length = math.sqrt(self.object_direction[0]**2 + self.object_direction[1]**2)
        if length > 0:
            self.object_direction[0] /= length
            self.object_direction[1] /= length
            
    def _update_object_position(self, dt):
        """
        Обновление позиции объекта слежения
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновление таймера траектории
        self.trajectory_timer += dt
        
        # Если пришло время, меняем направление движения
        if self.trajectory_timer >= self.trajectory_change_interval:
            self.trajectory_timer = 0
            
            if self.trajectory_type == 'linear':
                # Плавное изменение направления
                self.object_direction[0] += random.uniform(-0.2, 0.2)
                self.object_direction[1] += random.uniform(-0.2, 0.2)
                self._normalize_direction()
                
            elif self.trajectory_type == 'circular':
                # Круговое движение
                angle = random.uniform(0, 2 * math.pi)
                self.object_direction[0] = math.cos(angle)
                self.object_direction[1] = math.sin(angle)
                
            elif self.trajectory_type == 'random':
                # Случайное направление
                self.object_direction[0] = random.uniform(-1, 1)
                self.object_direction[1] = random.uniform(-1, 1)
                self._normalize_direction()
        
        # Обновление позиции объекта
        self.object_pos[0] += self.object_direction[0] * self.object_speed * dt
        self.object_pos[1] += self.object_direction[1] * self.object_speed * dt
        
        # Проверка столкновения с границами
        if self.object_pos[0] - self.object_size // 2 < 0 or self.object_pos[0] + self.object_size // 2 > WINDOW_WIDTH:
            self.object_direction[0] *= -1  # отражение по горизонтали
            
        if self.object_pos[1] - self.object_size // 2 < 0 or self.object_pos[1] + self.object_size // 2 > WINDOW_HEIGHT:
            self.object_direction[1] *= -1  # отражение по вертикали
            
        # Убеждаемся, что объект остается в пределах экрана
        self.object_pos[0] = max(self.object_size // 2, min(self.object_pos[0], WINDOW_WIDTH - self.object_size // 2))
        self.object_pos[1] = max(self.object_size // 2, min(self.object_pos[1], WINDOW_HEIGHT - self.object_size // 2))
        
    def _update_tracking_accuracy(self, cursor_pos):
        """
        Обновление точности слежения за объектом
        
        Args:
            cursor_pos: координаты курсора (x, y)
        """
        if not cursor_pos:
            return
            
        # Расчет расстояния между объектом и курсором
        distance = math.sqrt((cursor_pos[0] - self.object_pos[0])**2 + 
                            (cursor_pos[1] - self.object_pos[1])**2)
        
        # Добавление текущего расстояния в историю
        self.tracking_history.append(distance)
        
        # Ограничение длины истории
        if len(self.tracking_history) > self.max_history_length:
            self.tracking_history.pop(0)
        
        # Расчет точности как процента времени в пределах допустимой области
        if self.tracking_history:
            in_area_count = sum(1 for d in self.tracking_history if d <= self.allowed_deviation)
            self.tracking_accuracy = (in_area_count / len(self.tracking_history)) * 100.0
        
            # Обновление счета на основе точности слежения
            self.score = int(self.tracking_accuracy)
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновление позиции объекта
        self._update_object_position(dt)
        
        # Получение позиции курсора
        cursor_pos = pygame.mouse.get_pos()
        
        # Обновление точности слежения
        self._update_tracking_accuracy(cursor_pos)
        
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        """
        # Получение позиции курсора
        cursor_pos = pygame.mouse.get_pos()
        
        # Определение цвета объекта (зеленый, если курсор внутри допустимой области, иначе желтый)
        is_in_area = False
        if cursor_pos:
            distance = math.sqrt((cursor_pos[0] - self.object_pos[0])**2 + 
                                (cursor_pos[1] - self.object_pos[1])**2)
            is_in_area = distance <= self.allowed_deviation
            
        object_color = COLORS['POSITIVE_GREEN'] if is_in_area else COLORS['ACCENT_YELLOW']
        
        # Отрисовка объекта слежения
        pygame.draw.circle(
            self.screen,
            object_color,
            (int(self.object_pos[0]), int(self.object_pos[1])),
            self.object_size // 2
        )
        
        # Отрисовка курсора (только при использовании мыши)
        if cursor_pos:
            pygame.draw.circle(
                self.screen,
                COLORS['PRIMARY_BLUE'],
                cursor_pos,
                5
            )
            
        # Отрисовка границы допустимой области (для отладки)
        if self.difficulty == 'Легкий':
            pygame.draw.circle(
                self.screen,
                object_color + (50,),  # полупрозрачный круг
                (int(self.object_pos[0]), int(self.object_pos[1])),
                self.allowed_deviation,
                1  # только контур
            )
            
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
            
        # При использовании жестового управления, обновляем точность слежения
        if cursor_pos:
            self._update_tracking_accuracy(cursor_pos)
