"""
Упражнение "Ловкие пальчики" для приложения NeuroGym
Ребенок должен быстро касаться появляющихся на экране объектов
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

class FastFingers(BaseExercise):
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        """
        Инициализация упражнения "Ловкие пальчики"
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen, difficulty)
        
        # Параметры упражнения в зависимости от сложности
        self.object_appear_time = self._get_appear_time_for_difficulty()
        self.max_objects = self._get_max_objects_for_difficulty()
        self.object_types = self._get_object_types_for_difficulty()
        
        # Состояние игры
        self.objects = []        # список активных объектов
        self.object_timer = 0    # таймер для появления новых объектов
        self.game_duration = 60  # продолжительность игры в секундах
        self.game_timer = self.game_duration  # таймер обратного отсчета
        self.hits = 0            # счетчик успешных касаний
        self.misses = 0          # счетчик пропущенных объектов
        self.combo = 0           # текущая комбо-серия успешных касаний
        self.max_combo = 0       # максимальная достигнутая комбо-серия
        
        # Эффекты
        self.effects = []        # список визуальных эффектов
        
        # Целевой счет для уровня сложности
        self.target_score = {'Легкий': 30, 'Средний': 40, 'Сложный': 50}[self.difficulty]
        
    def _get_appear_time_for_difficulty(self):
        """
        Получение времени отображения объекта в зависимости от уровня сложности
        
        Returns:
            float: время в секундах
        """
        if self.difficulty == 'Легкий':
            return 2.0  # 2 секунды
        elif self.difficulty == 'Средний':
            return 1.5  # 1.5 секунды
        else:  # Сложный
            return 1.0  # 1 секунда
            
    def _get_max_objects_for_difficulty(self):
        """
        Получение максимального количества одновременных объектов
        
        Returns:
            int: максимальное количество объектов
        """
        if self.difficulty == 'Легкий':
            return 3
        elif self.difficulty == 'Средний':
            return 4
        else:  # Сложный
            return 5
            
    def _get_object_types_for_difficulty(self):
        """
        Получение типов объектов в зависимости от уровня сложности
        
        Returns:
            list: список доступных типов объектов
        """
        if self.difficulty == 'Легкий':
            return ['circle', 'square', 'triangle']
        elif self.difficulty == 'Средний':
            return ['circle', 'square', 'triangle', 'star']
        else:  # Сложный
            return ['circle', 'square', 'triangle', 'star', 'pentagon']
            
    def _generate_object(self):
        """
        Генерация нового объекта
        
        Returns:
            dict: словарь с параметрами объекта
        """
        # Базовый размер объекта
        base_size = random.randint(40, 60)
        
        # Выбор случайной позиции, избегая краев экрана и перекрытия с другими объектами
        margin = base_size * 2
        valid_position = False
        max_attempts = 20
        attempts = 0
        
        x, y = 0, 0
        
        while not valid_position and attempts < max_attempts:
            x = random.randint(margin, WINDOW_WIDTH - margin)
            y = random.randint(margin, WINDOW_HEIGHT - margin)
            
            # Проверка на перекрытие с другими объектами
            overlapping = False
            for obj in self.objects:
                dx = x - obj['x']
                dy = y - obj['y']
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < (base_size + obj['size']):
                    overlapping = True
                    break
                    
            if not overlapping:
                valid_position = True
                
            attempts += 1
            
        # Если не удалось найти свободное место за max_attempts попыток, используем случайные координаты
        if not valid_position:
            x = random.randint(margin, WINDOW_WIDTH - margin)
            y = random.randint(margin, WINDOW_HEIGHT - margin)
            
        # Выбор случайного типа объекта
        object_type = random.choice(self.object_types)
        
        # Выбор случайного цвета
        colors = [COLORS['ACCENT_YELLOW'], COLORS['POSITIVE_GREEN'], 
                 COLORS['PRIMARY_BLUE'], COLORS['NEGATIVE_RED']]
        color = random.choice(colors)
        
        # Создаем новый объект
        new_object = {
            'type': object_type,
            'x': x,
            'y': y,
            'size': base_size,
            'color': color,
            'timer': self.object_appear_time,  # таймер до исчезновения
            'animation': 1.0,  # параметр для анимации появления/исчезновения (0-1)
            'state': 'appearing',  # 'appearing', 'visible', 'disappearing', 'hit'
            'hit': False  # флаг, что объект был успешно нажат
        }
        
        return new_object
        
    def _update_objects(self, dt):
        """
        Обновление состояния всех объектов
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Создание новых объектов с определенной периодичностью
        self.object_timer -= dt
        if self.object_timer <= 0 and len(self.objects) < self.max_objects:
            self.objects.append(self._generate_object())
            # Время до появления следующего объекта зависит от сложности
            self.object_timer = 1.0 if self.difficulty == 'Легкий' else 0.8 if self.difficulty == 'Средний' else 0.6
            
        # Обновление состояния каждого объекта
        for obj in self.objects[:]:  # создаем копию списка, так как будем удалять элементы
            # Анимация появления
            if obj['state'] == 'appearing':
                obj['animation'] = min(1.0, obj['animation'] + dt * 3)
                if obj['animation'] >= 1.0:
                    obj['state'] = 'visible'
                    
            # Отсчет времени видимости объекта
            elif obj['state'] == 'visible':
                obj['timer'] -= dt
                if obj['timer'] <= 0:
                    obj['state'] = 'disappearing'
                    obj['animation'] = 1.0
                    
                    # Если объект пропущен, увеличиваем счетчик промахов
                    if not obj['hit']:
                        self.misses += 1
                        self.combo = 0  # сбрасываем комбо
                    
            # Анимация исчезновения
            elif obj['state'] == 'disappearing' or obj['state'] == 'hit':
                obj['animation'] = max(0.0, obj['animation'] - dt * 3)
                if obj['animation'] <= 0.0:
                    self.objects.remove(obj)
                    
        # Обновление визуальных эффектов
        for effect in self.effects[:]:  # создаем копию списка
            effect['duration'] -= dt
            if effect['duration'] <= 0:
                self.effects.remove(effect)
                
    def _check_object_click(self, pos):
        """
        Проверка клика по объектам
        
        Args:
            pos: координаты клика (x, y)
            
        Returns:
            int: индекс объекта или -1, если клик не по объекту
        """
        for i, obj in enumerate(self.objects):
            # Проверяем только видимые объекты, которые еще не были нажаты
            if obj['state'] == 'visible' and not obj['hit']:
                # Вычисляем расстояние от клика до центра объекта
                dx = pos[0] - obj['x']
                dy = pos[1] - obj['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Проверяем, попал ли клик в объект
                if distance <= obj['size']:
                    return i
                    
        return -1
        
    def _add_hit_effect(self, x, y, color):
        """
        Добавление эффекта при успешном попадании
        
        Args:
            x, y: координаты эффекта
            color: цвет эффекта
        """
        effect = {
            'type': 'circle',
            'x': x,
            'y': y,
            'size': 0,
            'max_size': 50,
            'color': color,
            'duration': 0.3  # длительность эффекта в секундах
        }
        
        self.effects.append(effect)
        
    def _calculate_final_score(self):
        """
        Расчет итогового счета
        """
        # Базовый счет зависит от количества успешных попаданий
        base_score = int(self.hits * 2)
        
        # Штраф за пропущенные объекты
        miss_penalty = min(50, self.misses * 3)
        
        # Бонус за комбо
        combo_bonus = self.max_combo * 2
        
        # Итоговый счет
        final_score = max(0, base_score - miss_penalty + combo_bonus)
        
        # Масштабируем до 100
        final_score = min(100, final_score)
        
        self.score = final_score
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновление игрового таймера
        if self.game_timer > 0:
            self.game_timer -= dt
            if self.game_timer <= 0:
                # Время истекло, завершаем упражнение
                self._calculate_final_score()
        
        # Обновление объектов
        self._update_objects(dt)
        
    def _draw_object(self, obj):
        """
        Отрисовка объекта
        
        Args:
            obj: словарь с параметрами объекта
        """
        # Вычисляем текущий размер объекта на основе анимации
        # При появлении/исчезновении размер изменяется от 0 до obj['size']
        current_size = obj['size'] * obj['animation']
        
        # Вычисляем прозрачность объекта
        alpha = min(255, int(255 * obj['animation']))
        
        # Цвет объекта с учетом прозрачности
        color = obj['color'][:3] + (alpha,)
        
        # Отрисовка объекта в зависимости от типа
        if obj['type'] == 'circle':
            # Тень
            if alpha > 100:
                shadow_alpha = int(alpha * 0.5)
                shadow_color = (0, 0, 0, shadow_alpha)
                pygame.draw.circle(self.screen, shadow_color, 
                                 (obj['x'] + 3, obj['y'] + 3), current_size)
                
            # Основной объект
            pygame.draw.circle(self.screen, color, (obj['x'], obj['y']), current_size)
            
            # Блик для объемности
            if alpha > 100:
                highlight_size = current_size * 0.4
                highlight_x = obj['x'] - current_size * 0.3
                highlight_y = obj['y'] - current_size * 0.3
                pygame.draw.circle(self.screen, (255, 255, 255, alpha // 2), 
                                 (highlight_x, highlight_y), highlight_size)
                
        elif obj['type'] == 'square':
            # Вычисляем координаты углов квадрата
            half_size = current_size
            rect = pygame.Rect(obj['x'] - half_size, obj['y'] - half_size, half_size * 2, half_size * 2)
            
            # Тень
            if alpha > 100:
                shadow_rect = rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                shadow_alpha = int(alpha * 0.5)
                shadow_color = (0, 0, 0, shadow_alpha)
                pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=int(current_size * 0.2))
                
            # Основной объект
            pygame.draw.rect(self.screen, color, rect, border_radius=int(current_size * 0.2))
            
            # Блик для объемности
            if alpha > 100:
                highlight_rect = pygame.Rect(rect.x, rect.y, rect.width * 0.6, rect.height * 0.3)
                pygame.draw.rect(self.screen, (255, 255, 255, alpha // 2), 
                              highlight_rect, border_radius=int(current_size * 0.1))
                
        elif obj['type'] == 'triangle':
            # Вычисляем координаты вершин треугольника
            points = [
                (obj['x'], obj['y'] - current_size),
                (obj['x'] - current_size, obj['y'] + current_size),
                (obj['x'] + current_size, obj['y'] + current_size)
            ]
            
            # Тень
            if alpha > 100:
                shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
                shadow_alpha = int(alpha * 0.5)
                shadow_color = (0, 0, 0, shadow_alpha)
                pygame.draw.polygon(self.screen, shadow_color, shadow_points)
                
            # Основной объект
            pygame.draw.polygon(self.screen, color, points)
            
            # Блик для объемности
            if alpha > 100:
                highlight_points = [
                    points[0],
                    (points[0][0] - current_size * 0.5, points[0][1] + current_size * 0.5),
                    (points[0][0] + current_size * 0.5, points[0][1] + current_size * 0.5)
                ]
                pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), highlight_points)
                
        elif obj['type'] == 'star':
            # Рисуем пятиконечную звезду
            num_points = 5
            outer_radius = current_size
            inner_radius = current_size * 0.5
            
            points = []
            for i in range(num_points * 2):
                radius = outer_radius if i % 2 == 0 else inner_radius
                angle = math.pi * i / num_points - math.pi / 2
                x = obj['x'] + radius * math.cos(angle)
                y = obj['y'] + radius * math.sin(angle)
                points.append((x, y))
                
            # Тень
            if alpha > 100:
                shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
                shadow_alpha = int(alpha * 0.5)
                shadow_color = (0, 0, 0, shadow_alpha)
                pygame.draw.polygon(self.screen, shadow_color, shadow_points)
                
            # Основной объект
            pygame.draw.polygon(self.screen, color, points)
            
            # Блик для объемности
            if alpha > 100:
                # Небольшой блик в верхней части звезды
                highlight_points = [points[0], points[9], points[1]]
                pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), highlight_points)
                
        elif obj['type'] == 'pentagon':
            # Рисуем пятиугольник
            num_points = 5
            radius = current_size
            
            points = []
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points - math.pi / 2
                x = obj['x'] + radius * math.cos(angle)
                y = obj['y'] + radius * math.sin(angle)
                points.append((x, y))
                
            # Тень
            if alpha > 100:
                shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
                shadow_alpha = int(alpha * 0.5)
                shadow_color = (0, 0, 0, shadow_alpha)
                pygame.draw.polygon(self.screen, shadow_color, shadow_points)
                
            # Основной объект
            pygame.draw.polygon(self.screen, color, points)
            
            # Блик для объемности
            if alpha > 100:
                # Небольшой блик в верхней части пятиугольника
                highlight_points = [
                    points[0],
                    ((points[0][0] + points[4][0]) // 2, (points[0][1] + points[4][1]) // 2),
                    ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
                ]
                pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), highlight_points)
                
    def _draw_effect(self, effect):
        """
        Отрисовка визуального эффекта
        
        Args:
            effect: словарь с параметрами эффекта
        """
        if effect['type'] == 'circle':
            # Вычисляем текущий размер эффекта
            progress = 1 - (effect['duration'] / 0.3)  # нормализованный прогресс от 0 до 1
            current_size = effect['max_size'] * progress
            
            # Вычисляем прозрачность (убывает с увеличением размера)
            alpha = int(255 * (1 - progress))
            
            # Цвет эффекта с учетом прозрачности
            color = effect['color'][:3] + (alpha,)
            
            # Рисуем круговой эффект (расходящееся кольцо)
            pygame.draw.circle(self.screen, color, (effect['x'], effect['y']), current_size, width=2)
            
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        """
        # Отрисовка визуальных эффектов
        for effect in self.effects:
            self._draw_effect(effect)
            
        # Отрисовка всех объектов
        for obj in self.objects:
            self._draw_object(obj)
            
        # Отображение игровой статистики
        # Таймер
        time_text = self.fonts['MEDIUM'].render(f"Время: {max(0, int(self.game_timer))}", True, COLORS['TEXT_DARK'])
        time_rect = time_text.get_rect(topleft=(20, 20))
        self.screen.blit(time_text, time_rect)
        
        # Счетчик попаданий
        hits_text = self.fonts['MEDIUM'].render(f"Попадания: {self.hits}/{self.target_score}", True, COLORS['TEXT_DARK'])
        hits_rect = hits_text.get_rect(topleft=(20, 50))
        self.screen.blit(hits_text, hits_rect)
        
        # Комбо
        combo_text = self.fonts['MEDIUM'].render(f"Комбо: {self.combo}", True, COLORS['TEXT_DARK'])
        combo_rect = combo_text.get_rect(topleft=(20, 80))
        self.screen.blit(combo_text, combo_rect)
        
        # Отображение результата, если время истекло
        if self.game_timer <= 0:
            result_bg = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
            pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (200,), result_bg, border_radius=15)
            
            # Заголовок в зависимости от результата
            if self.hits >= self.target_score:
                result_text = self.fonts['LARGE'].render("Отличная работа!", True, COLORS['TEXT_LIGHT'])
            else:
                result_text = self.fonts['LARGE'].render("Время вышло!", True, COLORS['TEXT_LIGHT'])
                
            result_rect = result_text.get_rect(center=(WINDOW_WIDTH // 2, result_bg.y + 40))
            self.screen.blit(result_text, result_rect)
            
            # Статистика
            stats_text = self.fonts['MEDIUM'].render(
                f"Попадания: {self.hits}   Пропущено: {self.misses}   Макс. комбо: {self.max_combo}", 
                True, COLORS['TEXT_LIGHT']
            )
            stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, result_bg.y + 90))
            self.screen.blit(stats_text, stats_rect)
            
            # Итоговый счет
            score_text = self.fonts['LARGE'].render(f"Счёт: {self.score}", True, COLORS['TEXT_LIGHT'])
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, result_bg.y + 140))
            self.screen.blit(score_text, score_rect)
            
    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий упражнения
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        super().handle_events(events, cursor_pos)
        
        # Если упражнение на паузе или время вышло, обрабатываем только базовые события
        if self.is_paused or self.game_timer <= 0:
            return
            
        # Используем позицию мыши или жестов
        mouse_pos = cursor_pos if cursor_pos else pygame.mouse.get_pos()
        
        for event in events:
            # Обработка кликов мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                object_index = self._check_object_click(mouse_pos)
                
                if object_index >= 0:
                    # Успешное попадание по объекту
                    hit_object = self.objects[object_index]
                    hit_object['hit'] = True
                    hit_object['state'] = 'hit'
                    
                    # Увеличиваем счетчик попаданий
                    self.hits += 1
                    
                    # Увеличиваем комбо
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    
                    # Добавляем эффект попадания
                    self._add_hit_effect(hit_object['x'], hit_object['y'], hit_object['color'])
                    
        # Обработка событий касания (для жестового управления)
        if cursor_pos:
            # Проверяем, есть ли объект под курсором
            object_index = self._check_object_click(cursor_pos)
            
            if object_index >= 0:
                # Аналогично обработке клика мышью
                hit_object = self.objects[object_index]
                
                # Проверяем, что объект еще не был нажат
                if not hit_object['hit']:
                    hit_object['hit'] = True
                    hit_object['state'] = 'hit'
                    
                    # Увеличиваем счетчик попаданий
                    self.hits += 1
                    
                    # Увеличиваем комбо
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    
                    # Добавляем эффект попадания
                    self._add_hit_effect(hit_object['x'], hit_object['y'], hit_object['color'])
