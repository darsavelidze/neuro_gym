"""
Упражнение "Траектория" для приложения NeuroGym
Ребенок должен пройти по кружочкам в правильном порядке
"""

import pygame
import math
import random

from .base_exercise import BaseExercise
from ..config import COLORS
from ..core.exercise_config import get_exercise_setting

class Trajectory(BaseExercise):
    exercise_id = 'trajectory'
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        super().__init__(screen_manager, screen, difficulty)
        self.start_radius = 30
        self.end_radius = 30
        self.checkpoint_radius = 25
        self._load_settings()
        self._reset_state()

    def _load_settings(self):
        self.num_checkpoints = get_exercise_setting(self.exercise_id, self.difficulty, 'checkpoints', 6)

    def _reset_state(self):
        self.checkpoints = self._generate_checkpoint_path()
        self.next_checkpoint = 0
        self.visited_checkpoints = 0
        self.progress = 0.0
        self.errors_count = 0
        self.max_errors = 3
        self.completed_paths = 0
        self.cursor_pos = None
        self.is_drawing = False
        self.path_complete = False
        self.start_point = self.checkpoints[0]['pos']
        self.end_point = self.checkpoints[-1]['pos']
        if hasattr(self, '_completion_timer'):
            delattr(self, '_completion_timer')

    def on_enter(self, params=None):
        super().on_enter(params)
        self._load_settings()
        self._reset_state()
        
    def _generate_checkpoint_path(self):
        """Генерация случайного пути из кружочков"""
        margin = 100
        min_x = margin
        max_x = self.width - margin
        min_y = margin + 80
        max_y = self.height - margin
        
        checkpoints = []
        min_distance = 100  # минимальное расстояние между кружочками
        max_attempts = 100
        
        for i in range(self.num_checkpoints):
            attempts = 0
            valid_position = False
            x, y = 0, 0
            
            while not valid_position and attempts < max_attempts:
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                
                valid_position = True
                for cp in checkpoints:
                    # Поддерживаем как словари (новый формат), так и кортежи (на случай будущих изменений)
                    base = cp['base'] if isinstance(cp, dict) else cp
                    dist = math.hypot(x - base[0], y - base[1])
                    if dist < min_distance:
                        valid_position = False
                        break
                
                attempts += 1
            
            checkpoints.append({
                'base': (x, y),
                'pos': [float(x), float(y)],
                'velocity': [0.0, 0.0],
                'target': (x, y),
                'drift_timer': 0.0
            })

        self._initialize_checkpoint_motion(checkpoints)
        return checkpoints

    def _initialize_checkpoint_motion(self, checkpoints):
        """Задает параметры плавного движения для чекпоинтов."""
        # Старт и финиш оставляем статичными для понятности игроку
        for idx, cp in enumerate(checkpoints):
            is_static = idx == 0 or idx == len(checkpoints) - 1
            cp['is_static'] = is_static
            if is_static:
                cp['target'] = cp['base']
                cp['drift_timer'] = 0.0
                continue

            cp['target'] = self._pick_new_target(cp['base'])
            cp['drift_timer'] = random.uniform(1.2, 2.4)
            cp['velocity'] = [random.uniform(-20, 20), random.uniform(-20, 20)]

    def _pick_new_target(self, base_pos):
        """Возвращает новую цель для дрейфа в пределах допустимой области."""
        drift_radius = 60
        margin = 100
        min_x = margin
        max_x = self.width - margin
        min_y = margin + 80
        max_y = self.height - margin

        offset_angle = random.uniform(0, math.pi * 2)
        offset_dist = random.uniform(drift_radius * 0.3, drift_radius)
        dx = math.cos(offset_angle) * offset_dist
        dy = math.sin(offset_angle) * offset_dist
        tx = min(max(base_pos[0] + dx, min_x), max_x)
        ty = min(max(base_pos[1] + dy, min_y), max_y)
        return (tx, ty)

    def _update_checkpoint_motion(self, dt):
        """Плавно двигает чекпоинты к целям с легким демпфированием (эффект plexus)."""
        if dt <= 0:
            return

        for idx, cp in enumerate(self.checkpoints):
            if cp.get('is_static'):
                continue

            cp['drift_timer'] -= dt
            if cp['drift_timer'] <= 0:
                cp['target'] = self._pick_new_target(cp['base'])
                cp['drift_timer'] = random.uniform(1.2, 2.4)

            # Пружинящее движение к целевой точке
            pos = cp['pos']
            vx, vy = cp['velocity']
            tx, ty = cp['target']

            to_target_x = tx - pos[0]
            to_target_y = ty - pos[1]
            spring = 2.5  # чем больше, тем быстрее подтягивается
            damping = 0.9  # сглаживание скорости

            vx += to_target_x * spring * dt
            vy += to_target_y * spring * dt
            vx *= damping
            vy *= damping

            pos[0] += vx * dt
            pos[1] += vy * dt

            # Ограничиваем область движения, чтобы кружки не «уплывали» за экран
            margin = 90
            min_x = margin
            max_x = self.width - margin
            min_y = margin + 60
            max_y = self.height - margin
            pos[0] = min(max(pos[0], min_x), max_x)
            pos[1] = min(max(pos[1], min_y), max_y)

            cp['velocity'] = [vx, vy]
    
    def _reset_path(self):
        """Генерация новой траектории после завершения"""
        self.checkpoints = self._generate_checkpoint_path()
        self.next_checkpoint = 0
        self.visited_checkpoints = 0
        self.progress = 0.0
        self.errors_count = 0
        self.is_drawing = False
        self.path_complete = False
        self.start_point = self.checkpoints[0]['pos']
        self.end_point = self.checkpoints[-1]['pos']
        self.completed_paths += 1
        
    def _advance_checkpoints(self):
        """Проверяем достижение следующего чекпоинта"""
        if self.next_checkpoint >= len(self.checkpoints) or not self.cursor_pos:
            return
            
        cp = self.checkpoints[self.next_checkpoint]['pos']
        cx, cy = cp
        dx = self.cursor_pos[0] - cx
        dy = self.cursor_pos[1] - cy
        dist = math.hypot(dx, dy)
        
        if dist <= self.checkpoint_radius:
            self.next_checkpoint += 1
            self.visited_checkpoints += 1
            self.progress = self.visited_checkpoints / len(self.checkpoints)
            
            if self.next_checkpoint >= len(self.checkpoints):
                self.path_complete = True
                self.is_drawing = False
        
    def _exercise_specific_update(self, dt):
        """Обновление упражнения"""
        # Обновляем плавное движение чекпоинтов до проверки логики
        self._update_checkpoint_motion(dt)

        if self.path_complete:
            # Автоматически генерируем новую траекторию через короткую задержку
            if not hasattr(self, '_completion_timer'):
                self._completion_timer = 0.5  # 0.5 секунды задержка
            
            self._completion_timer -= dt
            if self._completion_timer <= 0:
                self._reset_path()
                delattr(self, '_completion_timer')
            return
        
        # Проверка начала рисования
        if self.cursor_pos and not self.is_drawing:
            start_distance = math.hypot(
                self.cursor_pos[0] - self.start_point[0],
                self.cursor_pos[1] - self.start_point[1]
            )
            
            if start_distance <= self.start_radius:
                self.is_drawing = True
                self.next_checkpoint = 1
                self.visited_checkpoints = 1
                self.progress = self.visited_checkpoints / len(self.checkpoints)
        
        # Если рисуем, продвигаем чекпоинты
        if self.is_drawing and self.cursor_pos:
            self._advance_checkpoints()
    
    def _calculate_final_score(self):
        """Расчет итогового счета"""
        # Базовый счет = количество пройденных траекторий * 10
        base_score = self.completed_paths * 10
        
        # Бонус за текущий прогресс
        current_bonus = int(self.progress * 10)
        
        # Итоговый счет
        self.score = min(100, base_score + current_bonus)
        self.accuracy = self.progress * 100
    
    def _draw_exercise_area(self):
        """Отрисовка игровой области"""
        # Рисуем линии между чекпоинтами
        for i in range(len(self.checkpoints) - 1):
            p1 = self.checkpoints[i]['pos']
            p2 = self.checkpoints[i + 1]['pos']
            
            # Цвет линии зависит от того, пройден ли участок
            if i < self.next_checkpoint - 1:
                color = COLORS['POSITIVE_GREEN']
                width = 3
            else:
                color = COLORS['PRIMARY_BLUE'] + (100,)
                width = 2
            
            pygame.draw.line(self.screen, color, p1, p2, width)
        
        # Рисуем чекпоинты
        for idx, cp in enumerate(self.checkpoints):
            cp_pos_f = cp['pos']
            cp_pos = (int(round(cp_pos_f[0])), int(round(cp_pos_f[1])))
            if idx == 0:
                # Старт
                pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'], cp_pos, self.start_radius)
                pygame.draw.circle(self.screen, COLORS['WHITE'], cp_pos, self.start_radius - 5)
                start_text = self.fonts['SMALL'].render("СТАРТ", True, COLORS['TEXT_DARK'])
                self.screen.blit(start_text, start_text.get_rect(center=cp_pos))
            elif idx == len(self.checkpoints) - 1:
                # Финиш
                pygame.draw.circle(self.screen, COLORS['NEGATIVE_RED'], cp_pos, self.end_radius)
                pygame.draw.circle(self.screen, COLORS['WHITE'], cp_pos, self.end_radius - 5)
                finish_text = self.fonts['SMALL'].render("ФИНИШ", True, COLORS['TEXT_DARK'])
                self.screen.blit(finish_text, finish_text.get_rect(center=cp_pos))
            else:
                # Обычный чекпоинт
                if idx < self.next_checkpoint:
                    # Пройденный
                    color = COLORS['POSITIVE_GREEN']
                elif idx == self.next_checkpoint:
                    # Следующий целевой
                    color = COLORS['ACCENT_YELLOW']
                else:
                    # Еще не достигнутый
                    color = COLORS['PRIMARY_BLUE']
                
                pygame.draw.circle(self.screen, color, cp_pos, self.checkpoint_radius)
                pygame.draw.circle(self.screen, COLORS['WHITE'], cp_pos, self.checkpoint_radius - 5)
                
                # Номер чекпоинта
                num_text = self.fonts['MEDIUM'].render(str(idx), True, COLORS['TEXT_DARK'])
                self.screen.blit(num_text, num_text.get_rect(center=cp_pos))
        
        # Курсор
        if self.cursor_pos:
            cursor_color = COLORS['POSITIVE_GREEN'] if self.is_drawing else COLORS['PRIMARY_BLUE']
            pygame.draw.circle(self.screen, cursor_color, self.cursor_pos, 12)
            pygame.draw.circle(self.screen, COLORS['WHITE'], self.cursor_pos, 6)
        
        # Прогресс
        progress_text = self.fonts['MEDIUM'].render(
            f"Траекторий пройдено: {self.completed_paths} | Прогресс: {int(self.progress * 100)}%",
            True, COLORS['TEXT_DARK']
        )
        self.screen.blit(progress_text, progress_text.get_rect(topleft=(20, 20)))
        
        # Сообщение о завершении
        if self.path_complete:
            complete_text = self.fonts['LARGE'].render("Отлично! Следующая траектория...", True, COLORS['POSITIVE_GREEN'])
            self.screen.blit(complete_text, complete_text.get_rect(center=(self.width // 2, self.height // 4)))
    
    def handle_events(self, events, cursor_pos=None):
        """Обработка событий"""
        super().handle_events(events, cursor_pos)
        if self.is_paused:
            return
        self.cursor_pos = cursor_pos if cursor_pos else self._get_cursor_position()
