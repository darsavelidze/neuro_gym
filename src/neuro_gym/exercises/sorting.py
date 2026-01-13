"""
Упражнение "Сортировка" для приложения NeuroGym
Ребенок должен перетаскивать предметы в соответствующие контейнеры
"""

import pygame
import math
import random

from .base_exercise import BaseExercise
from ..config import COLORS
from ..core.exercise_config import get_exercise_setting
from ..core.input_handler import GESTURE_PINCH_START, GESTURE_PINCH_END

class Sorting(BaseExercise):
    exercise_id = 'sorting'
    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        super().__init__(screen_manager, screen, difficulty)
        self._load_settings()
        self._reset_state()

    def _load_settings(self):
        self.num_categories = get_exercise_setting(self.exercise_id, self.difficulty, 'categories', 3)
        self.num_objects = get_exercise_setting(self.exercise_id, self.difficulty, 'objects', 6)
        self.allowed_errors = get_exercise_setting(self.exercise_id, self.difficulty, 'errors', 5)

    def _reset_state(self):
        self.categories = self._create_categories()
        self.objects = self._create_objects()
        self.current_object = None
        self.start_drag_pos = None
        self.errors_count = 0
        self.correct_placements = 0
        self.animation_time = 0
        self.objects_to_animate = []

    def on_enter(self, params=None):
        super().on_enter(params)
        self._load_settings()
        self._reset_state()
        
    def _create_categories(self):
        """
        Создание категорий для сортировки
        
        Returns:
            list: список категорий
        """
        categories = []
        
        # Определяем возможные типы категорий (формы, цвета)
        category_types = [
            {
                'name': 'Квадраты',
                'shape': 'square',
                'color': COLORS['ACCENT_YELLOW']
            },
            {
                'name': 'Круги',
                'shape': 'circle',
                'color': COLORS['POSITIVE_GREEN']
            },
            {
                'name': 'Треугольники',
                'shape': 'triangle',
                'color': COLORS['NEGATIVE_RED']
            },
            {
                'name': 'Звезды',
                'shape': 'star',
                'color': COLORS['PRIMARY_BLUE']
            },
            {
                'name': 'Ромбы',
                'shape': 'diamond',
                'color': (180, 100, 240)  # фиолетовый
            }
        ]
        
        # Выбираем нужное количество категорий
        selected_categories = category_types[:self.num_categories]
        
        # Размер контейнера
        container_size = 120
        
        # Расположение контейнеров внизу экрана
        container_y = self.height - container_size - 80
        container_spacing = 40
        total_width = self.num_categories * container_size + (self.num_categories - 1) * container_spacing
        start_x = (self.width - total_width) // 2
        
        # Создаем контейнеры для каждой категории
        for i, category in enumerate(selected_categories):
            container_x = start_x + i * (container_size + container_spacing)
            container_rect = pygame.Rect(container_x, container_y, container_size, container_size)
            
            categories.append({
                'name': category['name'],
                'shape': category['shape'],
                'color': category['color'],
                'rect': container_rect
            })
            
        return categories
        
    def _create_objects(self):
        """
        Создание объектов для сортировки
        
        Returns:
            list: список объектов
        """
        objects = []
        object_size = 60
        
        # Определяем область размещения объектов
        area_width = self.width - 200
        area_height = self.height // 2 - 100
        area_x = 100
        area_y = 100
        
        # Создаем объекты всех категорий
        objects_per_category = self.num_objects // self.num_categories
        remaining_objects = self.num_objects % self.num_categories
        
        object_count = 0
        
        for category in self.categories:
            # Определяем количество объектов данной категории
            count = objects_per_category
            if remaining_objects > 0:
                count += 1
                remaining_objects -= 1
                
            for _ in range(count):
                # Генерация случайной позиции для объекта
                valid_position = False
                max_attempts = 50
                attempts = 0
                
                while not valid_position and attempts < max_attempts:
                    # Генерируем случайную позицию в пределах области
                    x = random.randint(area_x, area_x + area_width - object_size)
                    y = random.randint(area_y, area_y + area_height - object_size)
                    rect = pygame.Rect(x, y, object_size, object_size)
                    
                    # Проверяем, не пересекается ли с другими объектами
                    overlaps = False
                    for obj in objects:
                        if rect.colliderect(obj['rect']):
                            overlaps = True
                            break
                            
                    if not overlaps:
                        valid_position = True
                        
                    attempts += 1
                    
                # Если не удалось найти место без пересечений, размещаем где получится
                if not valid_position:
                    x = random.randint(area_x, area_x + area_width - object_size)
                    y = random.randint(area_y, area_y + area_height - object_size)
                    rect = pygame.Rect(x, y, object_size, object_size)
                
                # Добавляем объект в список
                objects.append({
                    'category': category['shape'],
                    'color': category['color'],
                    'rect': rect,
                    'original_pos': (x, y),  # запоминаем изначальную позицию
                    'placed': False,          # флаг, что объект размещен в контейнере
                    'animation': {           # параметры для анимации
                        'active': False,
                        'start_pos': None,
                        'end_pos': None,
                        'progress': 0
                    }
                })
                
                object_count += 1
                
        # Перемешиваем объекты для большей случайности
        random.shuffle(objects)
        
        return objects
        
    def _draw_category_container(self, category):
        """
        Отрисовка контейнера категории
        
        Args:
            category: словарь с данными категории
        """
        # Отрисовка основы контейнера
        pygame.draw.rect(self.screen, category['color'] + (100,), category['rect'], border_radius=12)
        pygame.draw.rect(self.screen, category['color'], category['rect'], width=3, border_radius=12)
        
        # Отрисовка символа категории в центре
        center_x = category['rect'].centerx
        center_y = category['rect'].centery
        size = 40  # размер символа
        
        if category['shape'] == 'square':
            symbol_rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
            pygame.draw.rect(self.screen, category['color'], symbol_rect)
        elif category['shape'] == 'circle':
            pygame.draw.circle(self.screen, category['color'], (center_x, center_y), size // 2)
        elif category['shape'] == 'triangle':
            points = [
                (center_x, center_y - size // 2),
                (center_x - size // 2, center_y + size // 2),
                (center_x + size // 2, center_y + size // 2)
            ]
            pygame.draw.polygon(self.screen, category['color'], points)
        elif category['shape'] == 'star':
            # Рисуем звезду
            num_points = 5
            outer_radius = size // 2
            inner_radius = size // 4
            
            points = []
            for i in range(num_points * 2):
                radius = outer_radius if i % 2 == 0 else inner_radius
                angle = math.pi * i / num_points - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
                
            pygame.draw.polygon(self.screen, category['color'], points)
        elif category['shape'] == 'diamond':
            # Рисуем ромб
            points = [
                (center_x, center_y - size // 2),
                (center_x + size // 2, center_y),
                (center_x, center_y + size // 2),
                (center_x - size // 2, center_y)
            ]
            pygame.draw.polygon(self.screen, category['color'], points)
            
        # Добавляем текст с названием категории
        label = self.fonts['SMALL'].render(category['name'], True, COLORS['TEXT_DARK'])
        label_rect = label.get_rect(center=(center_x, category['rect'].bottom + 25))
        self.screen.blit(label, label_rect)
        
    def _draw_object(self, obj):
        """
        Отрисовка объекта для сортировки
        
        Args:
            obj: словарь с данными объекта
        """
        rect = obj['rect']
        center_x = rect.centerx
        center_y = rect.centery
        size = rect.width
        
        # Отрисовка объекта в зависимости от его типа
        if obj['category'] == 'square':
            pygame.draw.rect(self.screen, obj['color'], rect, border_radius=5)
            # Добавляем блик для объемности
            highlight_rect = pygame.Rect(rect.x, rect.y, size // 2, size // 3)
            pygame.draw.rect(self.screen, (255, 255, 255, 70), highlight_rect, border_radius=5)
        elif obj['category'] == 'circle':
            pygame.draw.circle(self.screen, obj['color'], (center_x, center_y), size // 2)
            # Добавляем блик для объемности
            pygame.draw.circle(self.screen, (255, 255, 255, 70), 
                             (center_x - size // 6, center_y - size // 6), size // 4)
        elif obj['category'] == 'triangle':
            points = [
                (center_x, rect.y),
                (rect.x, rect.y + size),
                (rect.x + size, rect.y + size)
            ]
            pygame.draw.polygon(self.screen, obj['color'], points)
            # Добавляем блик для объемности
            highlight_points = [
                points[0],
                (points[0][0] - size // 4, points[0][1] + size // 4),
                (points[0][0] + size // 4, points[0][1] + size // 4)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 255, 70), highlight_points)
        elif obj['category'] == 'star':
            # Рисуем звезду
            num_points = 5
            outer_radius = size // 2
            inner_radius = size // 4
            
            points = []
            for i in range(num_points * 2):
                radius = outer_radius if i % 2 == 0 else inner_radius
                angle = math.pi * i / num_points - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
                
            pygame.draw.polygon(self.screen, obj['color'], points)
            
            # Добавляем блик для объемности
            highlight_points = []
            for i in range(3):
                radius = inner_radius if i % 2 == 0 else inner_radius // 2
                angle = math.pi * i / 2 - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                highlight_points.append((x, y))
                
            pygame.draw.polygon(self.screen, (255, 255, 255, 70), highlight_points)
        elif obj['category'] == 'diamond':
            # Рисуем ромб
            points = [
                (center_x, rect.y),
                (rect.x + size, center_y),
                (center_x, rect.y + size),
                (rect.x, center_y)
            ]
            pygame.draw.polygon(self.screen, obj['color'], points)
            
            # Добавляем блик для объемности
            highlight_points = [
                (center_x, rect.y + 5),
                (center_x - size // 3, center_y - size // 6),
                (center_x, center_y - size // 3)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 255, 70), highlight_points)
            
        # Если объект перетаскивается, добавляем свечение вокруг него
        if obj == self.current_object:
            glow_size = 6
            glow_rect = pygame.Rect(
                rect.x - glow_size, rect.y - glow_size, 
                rect.width + glow_size * 2, rect.height + glow_size * 2
            )
            glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 255, 100), glow_surface.get_rect(), border_radius=10)
            self.screen.blit(glow_surface, glow_rect.topleft)
            
    def _check_placement(self, obj):
        """
        Проверка правильности размещения объекта в контейнере
        
        Args:
            obj: словарь с данными объекта
            
        Returns:
            tuple: (правильно ли размещен, категория контейнера)
        """
        # Проверяем, находится ли объект над каким-либо контейнером
        for category in self.categories:
            if obj['rect'].colliderect(category['rect']):
                # Объект размещен в контейнере
                # Проверяем, соответствует ли категория
                is_correct = (obj['category'] == category['shape'])
                return (is_correct, category['shape'])
                
        # Объект не размещен ни в одном контейнере
        return (False, None)

    def _release_object(self, mouse_pos):
        """Отпускание перетаскиваемого объекта и проверка размещения."""
        if not self.current_object:
            return

        is_correct, category = self._check_placement(self.current_object)

        if category:  # Объект размещен в контейнере
            if is_correct:
                self.correct_placements += 1
                self.current_object['placed'] = True
                for cat in self.categories:
                    if cat['shape'] == category:
                        target_x = cat['rect'].centerx - self.current_object['rect'].width // 2
                        target_y = cat['rect'].centery - self.current_object['rect'].height // 2
                        self.current_object['animation'] = {
                            'active': True,
                            'start_pos': self.current_object['rect'].topleft,
                            'end_pos': (target_x, target_y),
                            'progress': 0
                        }
                        break
            else:
                self.errors_count += 1
                original_x, original_y = self.current_object['original_pos']
                self.current_object['animation'] = {
                    'active': True,
                    'start_pos': self.current_object['rect'].topleft,
                    'end_pos': (original_x, original_y),
                    'progress': 0
                }
        else:
            original_x, original_y = self.current_object['original_pos']
            self.current_object['animation'] = {
                'active': True,
                'start_pos': self.current_object['rect'].topleft,
                'end_pos': (original_x, original_y),
                'progress': 0
            }

        self.current_object = None
        if self.errors_count >= self.allowed_errors and not self.is_completed:
            self._complete_exercise()
        
    def _update_object_positions(self):
        """
        Обновление позиций объектов (для анимаций)
        """
        for obj in self.objects:
            if obj['animation']['active']:
                # Обновляем прогресс анимации
                obj['animation']['progress'] += 0.05
                if obj['animation']['progress'] >= 1:
                    # Анимация завершена
                    obj['animation']['active'] = False
                    obj['rect'].topleft = obj['animation']['end_pos']
                else:
                    # Вычисляем промежуточную позицию
                    progress = obj['animation']['progress']
                    # Используем функцию замедления для более естественного движения
                    t = 0.5 - 0.5 * math.cos(progress * math.pi)
                    start_x, start_y = obj['animation']['start_pos']
                    end_x, end_y = obj['animation']['end_pos']
                    
                    # С небольшой дугой для эффекта "броска"
                    arc_height = 50 * math.sin(progress * math.pi)
                    
                    current_x = start_x + (end_x - start_x) * t
                    current_y = start_y + (end_y - start_y) * t - arc_height
                    
                    obj['rect'].topleft = (current_x, current_y)
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновляем время анимации
        self.animation_time += dt
        
        # Обновляем позиции анимированных объектов
        self._update_object_positions()
        
        # Проверка завершения упражнения
        if self.correct_placements >= self.num_objects and not self.is_completed:
            self._complete_exercise()

        if self.errors_count >= self.allowed_errors and not self.is_completed:
            self._complete_exercise()
            
    def _calculate_final_score(self):
        """
        Расчет итогового счета
        """
        # Базовая оценка за правильные размещения
        base_score = int((self.correct_placements / self.num_objects) * 100)
        
        # Штраф за ошибки
        error_penalty = min(50, self.errors_count * 10)
        
        # Итоговый счет
        final_score = max(0, base_score - error_penalty)
        
        # Бонус за сортировку всех объектов
        if self.correct_placements >= self.num_objects:
            # Бонус зависит от скорости выполнения и сложности
            difficulty_factor = {'Легкий': 1, 'Средний': 1.5, 'Сложный': 2}[self.difficulty]
            elapsed = getattr(self, 'elapsed_time', 0)
            speed_bonus = min(20, int(100 / (elapsed + 1) * difficulty_factor))
            final_score += speed_bonus
            
        self.score = min(100, final_score)  # Максимальная оценка - 100
        
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        """
        # Рисуем контейнеры категорий
        for category in self.categories:
            self._draw_category_container(category)
            
        # Рисуем объекты
        # Сначала неразмещенные, затем размещенные (для правильного порядка отображения)
        for obj in [o for o in self.objects if not o['placed']]:
            self._draw_object(obj)
            
        for obj in [o for o in self.objects if o['placed']]:
            self._draw_object(obj)

    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий упражнения
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        super().handle_events(events, cursor_pos)
        
        # Если упражнение на паузе или завершено, обрабатываем только базовые события
        if self.is_paused or self.is_completed or self.errors_count >= self.allowed_errors:
            return
            
        # Используем позицию мыши или жестов
        mouse_pos = cursor_pos if cursor_pos else self._get_cursor_position()

        # Проверяем режим управления
        gesture_mode = (self.context and self.context.input_handler
                        and self.context.input_handler.is_gesture_mode())
        
        for event in events:
            # ── Жесты: щипок = захват / отпускание ──
            if gesture_mode and event.type == GESTURE_PINCH_START and not self.current_object:
                for obj in [o for o in self.objects if not o['placed']]:
                    if obj['rect'].collidepoint(mouse_pos):
                        self.current_object = obj
                        self.start_drag_pos = mouse_pos
                        break
            elif gesture_mode and event.type == GESTURE_PINCH_END and self.current_object:
                self._release_object(mouse_pos)

            # ── Мышь: обычное перетаскивание ──
            elif not gesture_mode:
                # Начало перетаскивания объекта
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.current_object:
                    # Проверяем, клик выполнен по неразмещенному объекту
                    for obj in [o for o in self.objects if not o['placed']]:
                        if obj['rect'].collidepoint(mouse_pos):
                            self.current_object = obj
                            self.start_drag_pos = mouse_pos
                            break
                            
                # Конец перетаскивания объекта
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.current_object:
                    self._release_object(mouse_pos)
                
        # Обновление позиции перетаскиваемого объекта
        if self.current_object and mouse_pos:
            # Вычисляем смещение от начальной позиции перетаскивания
            if self.start_drag_pos:
                dx = mouse_pos[0] - self.start_drag_pos[0]
                dy = mouse_pos[1] - self.start_drag_pos[1]
                
                # Перемещаем объект
                self.current_object['rect'].x += dx
                self.current_object['rect'].y += dy
                
                # Обновляем начальную позицию перетаскивания
                self.start_drag_pos = mouse_pos
