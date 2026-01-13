"""
Упражнение "Следопыт" для приложения NeuroGym
Ребенок должен следить за движущимся объектом указательным пальцем
"""

import pygame
import math
import random

from .base_exercise import BaseExercise
from ..config import COLORS, EXERCISE_DURATION
from ..core.exercise_config import get_exercise_setting

class Pathfinder(BaseExercise):
    exercise_id = 'pathfinder'
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        super().__init__(screen_manager, screen, difficulty)
        self._load_settings()
        self._reset_state()

    def _load_settings(self):
        self.object_size = 40
        self.object_speed = get_exercise_setting(self.exercise_id, self.difficulty, 'speed', 120.0)
        self.base_xp_rate = get_exercise_setting(self.exercise_id, self.difficulty, 'xp_rate', 18.0)
        self.allowed_deviation = get_exercise_setting(self.exercise_id, self.difficulty, 'deviation', self.object_size * 2)
        self.trajectory_type = get_exercise_setting(self.exercise_id, self.difficulty, 'trajectory', 'linear')
        self.trajectory_change_interval = get_exercise_setting(
            self.exercise_id, self.difficulty, 'trajectory_interval', 2.0
        )
        self.max_history_length = get_exercise_setting(self.exercise_id, self.difficulty, 'history_length', 180)
        self.default_duration = get_exercise_setting(self.exercise_id, self.difficulty, 'duration', EXERCISE_DURATION)
        self.duration = self.default_duration

    def _reset_state(self):
        self.object_pos = [self.width // 2, self.height // 2]
        self.object_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self._normalize_direction()

        self.tracking_accuracy = 100.0
        self.tracking_history = []
        self.star_score = 0
        self.xp_gain = 0.0
        self.combo = 1.0
        self.max_combo = 5.0
        self.combo_timer = 0.0
        self.combo_step = 2.0
        self.combo_decay = 1.0
        self._last_in_area = False
        self.trajectory_timer = 0

    def on_enter(self, params=None):
        super().on_enter(params)
        self._load_settings()
        self._reset_state()
        
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
        if self.object_pos[0] - self.object_size // 2 < 0 or self.object_pos[0] + self.object_size // 2 > self.width:
            self.object_direction[0] *= -1  # отражение по горизонтали
            
        if self.object_pos[1] - self.object_size // 2 < 0 or self.object_pos[1] + self.object_size // 2 > self.height:
            self.object_direction[1] *= -1  # отражение по вертикали
            
        # Убеждаемся, что объект остается в пределах экрана
        self.object_pos[0] = max(self.object_size // 2, min(self.object_pos[0], self.width - self.object_size // 2))
        self.object_pos[1] = max(self.object_size // 2, min(self.object_pos[1], self.height - self.object_size // 2))
        
    def _update_tracking_accuracy(self, cursor_pos, distance=None):
        """
        Обновление точности слежения за объектом
        
        Args:
            cursor_pos: координаты курсора (x, y)
        """
        if not cursor_pos:
            return
            
        if distance is None:
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
            self.star_score = int(self.tracking_accuracy)

    def _update_experience(self, dt, is_in_area):
        """Начисляет опыт за нахождение в зоне слежения."""
        if is_in_area:
            self.combo_timer += dt
            if self.combo_timer >= self.combo_step and self.combo < self.max_combo:
                self.combo += 1
                self.combo_timer = 0
            gain = self.base_xp_rate * (1 + 0.25 * (self.combo - 1)) * dt
            self.xp_gain += gain
        else:
            self.combo_timer = 0
            self.combo = max(1.0, self.combo - self.combo_decay * dt)

        self.score = int(self.xp_gain)
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновление позиции объекта
        self._update_object_position(dt)
        
        # Получение позиции курсора из общего состояния
        cursor_pos = self.cursor_pos

        distance = None
        is_in_area = False
        if cursor_pos:
            distance = math.sqrt((cursor_pos[0] - self.object_pos[0])**2 + 
                                 (cursor_pos[1] - self.object_pos[1])**2)
            is_in_area = distance <= self.allowed_deviation
            self._last_in_area = is_in_area
        else:
            self._last_in_area = False
        
        # Обновление точности слежения
        self._update_tracking_accuracy(cursor_pos, distance)

        # Начисление опыта за удержание цели
        self._update_experience(dt, is_in_area)
        
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        """
        # Получение позиции курсора
        cursor_pos = self.cursor_pos
        
        # Определение цвета объекта (зеленый, если курсор внутри допустимой области, иначе желтый)
        is_in_area = self._last_in_area
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

    def _draw_extra_hud(self, y_start):
        """Отрисовка дополнительных метрик: XP/комбо и точность."""
        xp_text = self.fonts['MEDIUM'].render(f"XP: {int(self.xp_gain)} (x{self.combo:.1f})", True, COLORS['TEXT_DARK'])
        xp_rect = xp_text.get_rect(topleft=(20, y_start))
        self.screen.blit(xp_text, xp_rect)

        acc_text = self.fonts['MEDIUM'].render(f"Точность: {int(self.tracking_accuracy)}%", True, COLORS['TEXT_DARK'])
        acc_rect = acc_text.get_rect(topleft=(20, xp_rect.bottom + 8))
        self.screen.blit(acc_text, acc_rect)
            
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

        # Обновляем позицию курсора для жестового режима
        if cursor_pos:
            self.cursor_pos = cursor_pos
            distance = math.sqrt((cursor_pos[0] - self.object_pos[0])**2 + 
                                (cursor_pos[1] - self.object_pos[1])**2)
            self._update_tracking_accuracy(cursor_pos, distance)
            self._update_experience(0, distance <= self.allowed_deviation)
