"""
Экран инструкций перед началом упражнения
"""

import pygame
import math
from .base_screen import BaseScreen
from ..config import COLORS, EXERCISES, SCREEN_PADDING

class InstructionsScreen(BaseScreen):
    def __init__(self, screen_manager, screen, exercise_id=None):
        """
        Инициализация экрана инструкций
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            exercise_id: идентификатор выбранного упражнения
        """
        super().__init__(screen_manager, screen)
        
        # Идентификатор упражнения
        self.exercise_id = exercise_id
        
        # Получение информации о выбранном упражнении
        self.exercise_info = self._get_exercise_info(exercise_id)
        
        # Переменные для анимации демонстрации
        self.demo_animation_time = 0
        self.demo_object_pos = [0, 0]
        self.demo_cursor_pos = [0, 0]
        self.demo_direction = [1, 1]
        
        # Создание элементов интерфейса
        self._create_ui_elements()

    def on_enter(self, params=None):
        """Обновляет выбранное упражнение при повторном входе."""
        super().on_enter(params)
        new_exercise_id = None
        if params:
            new_exercise_id = params.get('exercise_id', self.exercise_id)
        if new_exercise_id and new_exercise_id != self.exercise_id:
            self.exercise_id = new_exercise_id
            self.exercise_info = self._get_exercise_info(new_exercise_id)
            self._reset_demo_state()
        elif new_exercise_id is None and not self.exercise_info:
            # Попробуем восстановить информацию, если её не было
            self.exercise_info = self._get_exercise_info(self.exercise_id)

    def _reset_demo_state(self):
        """Сбрасывает состояние демо-анимации."""
        self.demo_animation_time = 0
        self.demo_object_pos = [0, 0]
        self.demo_cursor_pos = [0, 0]
        self.demo_direction = [1, 1]
        
    def _get_exercise_info(self, exercise_id):
        """
        Получение информации об упражнении по его идентификатору
        
        Args:
            exercise_id: идентификатор упражнения
            
        Returns:
            dict: информация об упражнении или None, если упражнение не найдено
        """
        for exercise in EXERCISES:
            if exercise['id'] == exercise_id:
                return exercise
                
        return None
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса экрана инструкций
        """
        # Очистка кнопок
        self.buttons = []
        
        # Стандартная кнопка "Назад" в левом верхнем углу
        self.create_back_button('exercise_selection', 'Назад')
        
        # Кнопка "OK" для начала упражнения (с улучшенным дизайном)
        button_width = 220
        button_height = 80
        button_x = (self.width - button_width) // 2
        button_y = self.height - button_height - SCREEN_PADDING - 10
        
        # Создаем яркую привлекательную кнопку
        self.create_button(
            "НАЧАТЬ", 
            button_x, button_y, 
            button_width, button_height, 
            action=self._start_exercise,
            color=COLORS['POSITIVE_GREEN'],
            hover_color=(100, 230, 120),  # Немного ярче при наведении
            text_color=COLORS['WHITE'],   # Белый текст для лучшего контраста
            font_size='LARGE'
        )
        
    def _start_exercise(self):
        """
        Запуск выбранного упражнения
        """
        if self.exercise_id:
            # Переход к экрану упражнения
            # Имя экрана упражнения должно соответствовать его идентификатору
            self.transition_to(self.exercise_id)
        else:
            # Если упражнение не выбрано, возвращаемся к выбору упражнения
            self.transition_to('exercise_selection')
            
    def update(self, dt):
        """
        Обновление экрана инструкций
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновляем анимацию демонстрации
        self._update_demo_animation(dt)
        
    def draw(self):
        """
        Отрисовка экрана инструкций
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
        
        if not self.exercise_info:
            # Если информация об упражнении не найдена, показываем сообщение об ошибке
            
            # Создаем фон для сообщения об ошибке
            error_bg_rect = pygame.Rect((self.width - 400) // 2, (self.height - 120) // 2, 400, 120)
            pygame.draw.rect(self.screen, COLORS['NEGATIVE_RED'] + (50,), error_bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, COLORS['NEGATIVE_RED'], error_bg_rect, width=2, border_radius=15)
            
            # Текст ошибки
            error_text = self.fonts['LARGE'].render("Упражнение не найдено", True, COLORS['NEGATIVE_RED'])
            error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(error_text, error_rect)
        else:
            # Создаем декоративный фон для заголовка
            title_bg_width = int(self.width * 0.7)
            title_bg_height = 80
            title_bg_rect = pygame.Rect((self.width - title_bg_width) // 2, SCREEN_PADDING + 20, 
                                      title_bg_width, title_bg_height)
                                      
            # Рисуем фон с тенью и закруглёнными углами
            shadow_rect = title_bg_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect, border_radius=15)
            pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (50,), title_bg_rect, border_radius=15)
            
            # Отрисовка заголовка (название упражнения)
            title_text = self.fonts['LARGE'].render(self.exercise_info['name'], True, COLORS['TEXT_LIGHT'])
            title_rect = title_text.get_rect(center=(self.width // 2, SCREEN_PADDING + 60))
            self.screen.blit(title_text, title_rect)
            
            # Отрисовка инструкции
            self._draw_instruction_text()
            
            # Отрисовка простой демонстрации упражнения
            self._draw_exercise_demo()
        
        # Отрисовка кнопок
        self.draw_buttons()
        
    def _draw_instruction_text(self):
        """
        Отрисовка текста инструкции
        """
        # Основной текст инструкции
        instruction_text = ""
        
        # Задаем инструкции в зависимости от упражнения
        if self.exercise_id == 'pathfinder':
            instruction_text = "Следуй за движущимся объектом указательным пальцем. Старайся удерживать палец на объекте."
        elif self.exercise_id == 'trajectory':
            instruction_text = "Проведи пальцем по линии от начала до конца. Старайся не выходить за границы."
        elif self.exercise_id == 'sorting':
            instruction_text = "Перетащи предметы в соответствующие контейнеры, распределяя их по группам."
        elif self.exercise_id == 'sequence':
            instruction_text = "Запомни и повтори последовательность подсвеченных объектов, нажимая на них в том же порядке."
        elif self.exercise_id == 'fast_fingers':
            instruction_text = "Быстро касайся появляющихся на экране объектов, прежде чем они исчезнут."
        else:
            instruction_text = self.exercise_info['description']
        
        # Разбиваем длинный текст на строки для лучшей читаемости
        max_width = int(self.width * 0.8)
        lines = []
        words = instruction_text.split()
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            text_width = self.fonts['LARGE'].size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
                
        lines.append(current_line)
        
        # Создаем фоновый прямоугольник для текста инструкций
        instruction_bg_width = int(self.width * 0.85)
        instruction_bg_height = len(lines) * self.fonts['LARGE'].get_linesize() + 30
        instruction_bg_rect = pygame.Rect(
            (self.width - instruction_bg_width) // 2,
            self.height // 3 - 15,
            instruction_bg_width,
            instruction_bg_height
        )
        
        # Рисуем полупрозрачный фон с легким градиентом
        pygame.draw.rect(self.screen, (255, 255, 255, 30), instruction_bg_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (30,), instruction_bg_rect, 
                       width=2, border_radius=12)
        
        # Отрисовка каждой строки инструкции
        line_height = self.fonts['LARGE'].get_linesize()
        start_y = self.height // 3
        
        for i, line in enumerate(lines):
            # Создаем текст с легким эффектом тени для лучшей читаемости
            # Сначала рисуем тень
            shadow_surface = self.fonts['LARGE'].render(line, True, (0, 0, 0, 100))
            shadow_rect = shadow_surface.get_rect(center=(self.width // 2 + 2, start_y + i * line_height + 2))
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Затем основной текст
            text_surface = self.fonts['LARGE'].render(line, True, COLORS['TEXT_DARK'])
            text_rect = text_surface.get_rect(center=(self.width // 2, start_y + i * line_height))
            self.screen.blit(text_surface, text_rect)
            
    def _draw_exercise_demo(self):
        """
        Отрисовка простой демонстрации упражнения
        """
        # Область для демонстрации
        demo_width = int(self.width * 0.6)
        demo_height = int(self.height * 0.3)
        demo_x = (self.width - demo_width) // 2
        demo_y = self.height // 2 + 30
        
        # Фон области демонстрации с закругленными углами и тенью
        
        # Сначала рисуем тень
        shadow_rect = pygame.Rect(demo_x + 5, demo_y + 5, demo_width, demo_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=15)
        
        # Затем основной фон с закругленными углами
        demo_rect = pygame.Rect(demo_x, demo_y, demo_width, demo_height)
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (80,), demo_rect, border_radius=15)
        
        # Добавляем градиентную подсветку для объемного эффекта
        highlight_rect = demo_rect.copy()
        highlight_rect.height = max(5, demo_rect.height // 10)
        pygame.draw.rect(self.screen, (255, 255, 255, 40), highlight_rect, border_radius=15)
        
        # В зависимости от упражнения рисуем анимированную демонстрацию
        if self.exercise_id == 'pathfinder':
            # Демонстрация: движущийся объект и следующий за ним палец
            
            # Сначала рисуем траекторию движения (тонкая пунктирная линия)
            center_x = demo_x + demo_width // 2
            center_y = demo_y + demo_height // 2
            radius = min(demo_width, demo_height) * 0.3
            
            # Рисуем пунктирную круговую траекторию
            num_segments = 36
            for i in range(num_segments):
                angle = i * (2 * math.pi / num_segments)
                start_angle = angle
                end_angle = angle + math.pi / num_segments
                
                start_pos = (
                    center_x + radius * math.cos(start_angle),
                    center_y + radius * math.sin(start_angle)
                )
                end_pos = (
                    center_x + radius * math.cos(end_angle),
                    center_y + radius * math.sin(end_angle)
                )
                
                # Рисуем пунктирную линию (через один сегмент)
                if i % 2 == 0:
                    pygame.draw.line(self.screen, COLORS['PRIMARY_BLUE'] + (100,), 
                                  start_pos, end_pos, 2)
            
            # Рисуем объект слежения (желтый круг с тенью)
            # Сначала тень
            shadow_offset = 3
            pygame.draw.circle(self.screen, (0, 0, 0, 100), 
                             (self.demo_object_pos[0] + shadow_offset, 
                              self.demo_object_pos[1] + shadow_offset), 22)
            
            # Затем сам объект с градиентом (два круга)
            pygame.draw.circle(self.screen, COLORS['ACCENT_YELLOW'], 
                             (self.demo_object_pos[0], self.demo_object_pos[1]), 20)
            pygame.draw.circle(self.screen, (255, 255, 255, 70), 
                             (self.demo_object_pos[0] - 7, self.demo_object_pos[1] - 7), 8)
            
            # Рисуем курсор (палец) с эффектом свечения
            # Сначала внешнее свечение
            glow_size = 16 + 2 * math.sin(self.demo_animation_time * 5)
            pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'] + (100,), 
                            (self.demo_cursor_pos[0], self.demo_cursor_pos[1]), glow_size)
            
            # Затем основной курсор
            pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'], 
                             (self.demo_cursor_pos[0], self.demo_cursor_pos[1]), 12)
            
            # Добавляем блик на курсоре
            pygame.draw.circle(self.screen, (255, 255, 255, 150), 
                             (self.demo_cursor_pos[0] - 4, self.demo_cursor_pos[1] - 4), 4)
                             
        elif self.exercise_id == 'trajectory':
            # Демонстрация: путь с границами и анимированным курсором
            start_x = demo_x + 50
            start_y = demo_y + demo_height // 2
            end_x = demo_x + demo_width - 50
            
            # Рисуем путь (волнистая линия для большей наглядности)
            path_points = []
            num_points = 50
            for i in range(num_points + 1):
                progress = i / num_points
                x = start_x + (end_x - start_x) * progress
                # Добавляем небольшую волну для более интересной траектории
                wave_height = 15
                y = start_y + math.sin(progress * 6) * wave_height
                path_points.append((x, y))
                
            # Рисуем основной путь
            path_width = 24
            pygame.draw.lines(self.screen, COLORS['PRIMARY_BLUE'], False, path_points, path_width)
            
            # Рисуем границы пути (верхнюю и нижнюю)
            upper_border = [(x, y - path_width//2) for x, y in path_points]
            lower_border = [(x, y + path_width//2) for x, y in path_points]
            pygame.draw.lines(self.screen, COLORS['ACCENT_YELLOW'], False, upper_border, 2)
            pygame.draw.lines(self.screen, COLORS['ACCENT_YELLOW'], False, lower_border, 2)
            
            # Отмечаем начало и конец
            pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'], path_points[0], 12)
            pygame.draw.circle(self.screen, COLORS['NEGATIVE_RED'], path_points[-1], 12)
            
            # Отрисовка курсора движущегося по пути
            if hasattr(self, 'demo_cursor_pos'):
                # Определение позиции курсора на пути
                progress = (math.sin(self.demo_animation_time * 0.8) + 1) / 2
                point_index = int(progress * (len(path_points) - 1))
                
                if 0 <= point_index < len(path_points):
                    cursor_pos = path_points[point_index]
                    
                    # Рисуем курсор "палец" с эффектом свечения
                    pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'] + (100,), cursor_pos, 15)
                    pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'], cursor_pos, 10)
                    pygame.draw.circle(self.screen, (255, 255, 255, 150), 
                                    (cursor_pos[0] - 3, cursor_pos[1] - 3), 4)
            
        elif self.exercise_id == 'sorting':
            # Демонстрация: объекты и контейнеры с анимацией сортировки
            # Контейнеры
            container_width = 70
            container_height = 70
            container_spacing = 50
            container_y = demo_y + demo_height - container_height - 20
            
            # Массив цветов для контейнеров
            container_colors = [COLORS['ACCENT_YELLOW'], COLORS['POSITIVE_GREEN'], COLORS['NEGATIVE_RED']]
            containers = []
            
            # Рисуем контейнеры со стильными эффектами
            for i in range(3):
                container_x = demo_x + 80 + i * (container_width + container_spacing)
                container_rect = pygame.Rect(container_x, container_y, container_width, container_height)
                
                # Сначала рисуем тень
                shadow_rect = container_rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=10)
                
                # Затем контейнер с градиентным эффектом
                pygame.draw.rect(self.screen, container_colors[i] + (150,), container_rect, border_radius=10)
                pygame.draw.rect(self.screen, container_colors[i], container_rect, width=2, border_radius=10)
                
                # Метка формы внутри контейнера
                shape_size = 24
                shape_center = (container_x + container_width // 2, container_y + container_height // 2)
                
                if i == 0:  # Квадрат
                    shape_rect = pygame.Rect(
                        shape_center[0] - shape_size // 2,
                        shape_center[1] - shape_size // 2,
                        shape_size, shape_size
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255, 100), shape_rect)
                elif i == 1:  # Круг
                    pygame.draw.circle(self.screen, (255, 255, 255, 100), shape_center, shape_size // 2)
                else:  # Треугольник
                    pygame.draw.polygon(self.screen, (255, 255, 255, 100), [
                        (shape_center[0], shape_center[1] - shape_size // 2),
                        (shape_center[0] - shape_size // 2, shape_center[1] + shape_size // 2),
                        (shape_center[0] + shape_size // 2, shape_center[1] + shape_size // 2)
                    ])
                
                containers.append((container_rect, container_colors[i], i))
            
            # Объекты для сортировки
            object_size = 34
            object_y = demo_y + 50
            
            # Определяем, какой объект перемещается (на основе времени анимации)
            animation_phase = int(self.demo_animation_time) % 3
            
            for i in range(3):
                # Базовая позиция объекта
                base_x = demo_x + 90 + i * (object_size + 70)
                
                # Если этот объект выбран для анимации, вычисляем его текущую позицию
                if i == animation_phase:
                    # Время в анимации (от 0 до 1)
                    t = (self.demo_animation_time % 1)
                    
                    # Начальная и конечная позиции для анимированного объекта
                    start_pos = (base_x, object_y)
                    target_container = containers[i]
                    end_pos = (target_container[0].centerx - object_size // 2, 
                               target_container[0].centery - object_size // 2)
                    
                    # Интерполяция с замедлением в конце
                    t = 0.5 - 0.5 * math.cos(t * math.pi)  # плавная анимация
                    
                    # Вычисляем текущую позицию
                    object_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                    current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                    
                    # Добавляем небольшую дугу в траекторию
                    arc_height = 40
                    arc_offset = math.sin(t * math.pi) * arc_height
                    current_y -= arc_offset
                    
                    # Рисуем подсказку (пунктирную линию)
                    pygame.draw.line(self.screen, container_colors[i] + (100,), 
                                   start_pos, end_pos, 2)
                else:
                    # Объекты, не участвующие в текущей анимации
                    object_x = base_x
                    current_y = object_y
                
                # Рисуем сами объекты в зависимости от формы
                if i == 0:  # Квадрат
                    # Тень
                    pygame.draw.rect(self.screen, (0, 0, 0, 80), 
                                  (object_x + 3, current_y + 3, object_size, object_size))
                    # Объект
                    pygame.draw.rect(self.screen, COLORS['ACCENT_YELLOW'], 
                                  (object_x, current_y, object_size, object_size))
                    # Блик
                    highlight_rect = pygame.Rect(object_x, current_y, object_size // 2, object_size // 3)
                    pygame.draw.rect(self.screen, (255, 255, 255, 100), highlight_rect)
                    
                elif i == 1:  # Круг
                    # Центр круга
                    center_x = object_x + object_size // 2
                    center_y = current_y + object_size // 2
                    # Тень
                    pygame.draw.circle(self.screen, (0, 0, 0, 80), 
                                    (center_x + 3, center_y + 3), object_size // 2)
                    # Объект
                    pygame.draw.circle(self.screen, COLORS['POSITIVE_GREEN'], 
                                    (center_x, center_y), object_size // 2)
                    # Блик
                    pygame.draw.circle(self.screen, (255, 255, 255, 100), 
                                     (center_x - object_size // 6, center_y - object_size // 6), 
                                     object_size // 6)
                    
                else:  # Треугольник
                    # Центр треугольника
                    center_x = object_x + object_size // 2
                    center_y = current_y + object_size // 2
                    # Вершины треугольника
                    triangle_points = [
                        (center_x, current_y),
                        (object_x, current_y + object_size),
                        (object_x + object_size, current_y + object_size)
                    ]
                    # Тень
                    shadow_points = [(x+3, y+3) for x, y in triangle_points]
                    pygame.draw.polygon(self.screen, (0, 0, 0, 80), shadow_points)
                    # Объект
                    pygame.draw.polygon(self.screen, COLORS['NEGATIVE_RED'], triangle_points)
                    # Блик
                    highlight_points = [
                        triangle_points[0],
                        (triangle_points[0][0] - object_size // 4, triangle_points[0][1] + object_size // 4),
                        (triangle_points[0][0] + object_size // 4, triangle_points[0][1] + object_size // 4)
                    ]
                    pygame.draw.polygon(self.screen, (255, 255, 255, 100), highlight_points)
                                      
        elif self.exercise_id == 'sequence':
            # Демонстрация: сетка объектов с анимацией последовательности
            grid_size = 3
            cell_size = 55
            grid_spacing = 15
            grid_start_x = demo_x + (demo_width - grid_size * (cell_size + grid_spacing) + grid_spacing) // 2
            grid_start_y = demo_y + (demo_height - grid_size * (cell_size + grid_spacing) + grid_spacing) // 2
            
            # Создаем фиксированную последовательность для демонстрации
            sequence = [(0,0), (1,1), (2,2), (0,2)]
            
            # Определяем текущий активный индекс на основе времени анимации
            active_index = int((self.demo_animation_time * 1.2) % (len(sequence) + 1))
            show_hint = active_index == len(sequence)  # В конце показываем подсказку
            
            # Массив для хранения уже активированных ячеек
            activated_cells = sequence[:active_index]
            
            # Отрисовка сетки
            for row in range(grid_size):
                for col in range(grid_size):
                    cell_x = grid_start_x + col * (cell_size + grid_spacing)
                    cell_y = grid_start_y + row * (cell_size + grid_spacing)
                    cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    
                    # Определяем состояние ячейки
                    is_active = (row, col) == sequence[active_index] if active_index < len(sequence) else False
                    is_previously_active = (row, col) in activated_cells
                    
                    # Выбираем цвет в зависимости от состояния
                    if is_active:
                        # Анимация пульсации для активной ячейки
                        pulse = 0.7 + 0.3 * math.sin(self.demo_animation_time * 10)
                        base_color = COLORS['ACCENT_YELLOW']
                        cell_color = tuple(int(c * pulse) for c in base_color)
                    elif is_previously_active:
                        # Подсвечиваем уже активированные ячейки
                        cell_color = COLORS['ACCENT_YELLOW'] + (100,)
                    else:
                        # Обычная ячейка
                        cell_color = COLORS['PRIMARY_BLUE'] + (150,)
                    
                    # Отрисовка тени
                    shadow_rect = cell_rect.copy()
                    shadow_rect.x += 3
                    shadow_rect.y += 3
                    pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_rect, border_radius=8)
                    
                    # Отрисовка ячейки с закругленными углами
                    pygame.draw.rect(self.screen, cell_color, cell_rect, border_radius=8)
                    pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'], cell_rect, width=2, border_radius=8)
                    
                    # Добавляем номер последовательности для активированных ячеек
                    if (row, col) in activated_cells and show_hint:
                        seq_num = activated_cells.index((row, col)) + 1
                        num_text = self.fonts['MEDIUM'].render(str(seq_num), True, COLORS['TEXT_LIGHT'])
                        num_rect = num_text.get_rect(center=cell_rect.center)
                        self.screen.blit(num_text, num_rect)
                        
            # Если показываем подсказку, добавляем поясняющий текст
            if show_hint:
                hint_text = self.fonts['SMALL'].render("Повтори последовательность", True, COLORS['TEXT_DARK'])
                hint_rect = hint_text.get_rect(
                    center=(demo_x + demo_width//2, grid_start_y - 20)
                )
                self.screen.blit(hint_text, hint_rect)
                                  
        elif self.exercise_id == 'fast_fingers':
            # Демонстрация: появляющиеся и исчезающие объекты
            # Определяем параметры анимации
            object_positions = [
                (demo_x + 100, demo_y + demo_height // 2 - 25),
                (demo_x + 250, demo_y + demo_height // 2),
                (demo_x + 400, demo_y + demo_height // 2 + 20)
            ]
            
            # Используем время анимации для определения, какие объекты активны
            animation_cycle = self.demo_animation_time % 6  # 6 секунд на полный цикл
            
            # Определяем, какой объект сейчас активен (появляется или исчезает)
            active_object = int(animation_cycle) % len(object_positions)
            
            # Фаза для текущего активного объекта (0-1)
            phase = animation_cycle % 1
            
            # Направление анимации (появление: 0->0.5, исчезновение: 0.5->1)
            is_appearing = phase < 0.5
            normalized_phase = phase * 2 if is_appearing else (1 - phase) * 2
            
            # Функция для плавной анимации (замедление в начале и конце)
            ease_phase = 0.5 - 0.5 * math.cos(normalized_phase * math.pi)
            
            # Рисуем все объекты с соответствующими эффектами
            for i in range(len(object_positions)):
                x, y = object_positions[i]
                
                # Определяем размер и прозрачность объекта на основе фазы анимации
                if i == active_object:
                    # Активный объект анимируется
                    size_factor = ease_phase  # Размер от 0 до 1
                    alpha = int(255 * ease_phase)  # Прозрачность от 0 до 255
                elif (i == (active_object - 1) % len(object_positions) and not is_appearing):
                    # Предыдущий объект исчез
                    size_factor = 0
                    alpha = 0
                else:
                    # Неактивные объекты отображаются статично
                    size_factor = 1
                    alpha = 180
                
                # Если объект невидимый, пропускаем отрисовку
                if alpha <= 0:
                    continue
                
                # Размеры для разных типов объектов
                base_sizes = [25, 20, 25]  # круг (радиус), квадрат (половина стороны), треугольник (высота)
                size = base_sizes[i] * size_factor
                
                # Цвета с учетом прозрачности
                colors = [
                    COLORS['ACCENT_YELLOW'] + (alpha,),
                    COLORS['POSITIVE_GREEN'] + (alpha,),
                    COLORS['PRIMARY_BLUE'] + (alpha,)
                ]
                
                # Рисуем тень, если объект достаточно видимый
                if alpha > 100:
                    shadow_alpha = int(alpha * 0.5)
                    shadow_offset = 4 * size_factor
                    shadow_colors = [(0, 0, 0, shadow_alpha)] * 3
                    
                    # Тень
                    if i == 0:  # Круг
                        pygame.draw.circle(self.screen, shadow_colors[i], 
                                       (x + shadow_offset, y + shadow_offset), size)
                    elif i == 1:  # Квадрат
                        shadow_rect = pygame.Rect(x - size + shadow_offset, y - size + shadow_offset, 
                                            size * 2, size * 2)
                        pygame.draw.rect(self.screen, shadow_colors[i], shadow_rect)
                    else:  # Треугольник
                        shadow_points = [
                            (x + shadow_offset, y - size + shadow_offset),
                            (x - size + shadow_offset, y + size + shadow_offset),
                            (x + size + shadow_offset, y + size + shadow_offset)
                        ]
                        pygame.draw.polygon(self.screen, shadow_colors[i], shadow_points)
                
                # Рисуем сам объект
                if i == 0:  # Круг
                    pygame.draw.circle(self.screen, colors[i], (x, y), size)
                    # Блик
                    if alpha > 150:
                        pygame.draw.circle(self.screen, (255, 255, 255, alpha // 2), 
                                       (x - size // 2, y - size // 2), size // 3)
                elif i == 1:  # Квадрат
                    rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
                    pygame.draw.rect(self.screen, colors[i], rect, border_radius=int(size // 3))
                    # Блик
                    if alpha > 150:
                        highlight_rect = pygame.Rect(x - size, y - size, size, size)
                        pygame.draw.rect(self.screen, (255, 255, 255, alpha // 2), 
                                      highlight_rect, border_radius=int(size // 4))
                else:  # Треугольник
                    points = [
                        (x, y - size),
                        (x - size, y + size),
                        (x + size, y + size)
                    ]
                    pygame.draw.polygon(self.screen, colors[i], points)
                    # Блик
                    if alpha > 150:
                        highlight_points = [
                            (x, y - size),
                            (x - size // 2, y - size // 2),
                            (x + size // 2, y - size // 2)
                        ]
                        pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), 
                                         highlight_points)
                
                # Добавляем эффект касания для текущего объекта
                if i == active_object and phase > 0.4 and phase < 0.6:
                    # Анимируемый объект: показываем эффект касания (круги расходятся)
                    touch_radius = (phase - 0.4) * 5 * size
                    touch_alpha = int(255 * (0.6 - phase) * 5)  # Постепенно исчезает
                    pygame.draw.circle(self.screen, (255, 255, 255, touch_alpha), 
                                    (x, y), touch_radius, width=2)
                    
    def _update_demo_animation(self, dt):
        """
        Обновление анимации демонстрации упражнения
        
        Args:
            dt: время в секундах с последнего обновления
        """
        if not self.exercise_info:
            return
            
        # Общие настройки демонстрационной области
        demo_width = int(self.width * 0.6)
        demo_height = int(self.height * 0.3)
        demo_x = (self.width - demo_width) // 2
        demo_y = self.height // 2 + 30
        
        # Увеличиваем таймер анимации
        self.demo_animation_time += dt
        
        # Анимация для разных упражнений
        if self.exercise_id == 'pathfinder':
            # Радиус и скорость движения объекта
            radius = min(demo_width, demo_height) * 0.3
            speed = 0.5
            
            # Обновляем позицию объекта по круговой траектории
            center_x = demo_x + demo_width // 2
            center_y = demo_y + demo_height // 2
            
            # Вычисляем позицию объекта
            angle = self.demo_animation_time * speed
            self.demo_object_pos = [
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle)
            ]
            
            # Позиция курсора немного отстает от объекта
            delay = 0.1  # Задержка в секундах
            angle_cursor = (self.demo_animation_time - delay) * speed
            self.demo_cursor_pos = [
                center_x + radius * math.cos(angle_cursor),
                center_y + radius * math.sin(angle_cursor)
            ]
            
        elif self.exercise_id == 'trajectory':
            # Анимация для упражнения "Траектория"
            # Вычисляем прогресс анимации (от 0 до 1 и обратно)
            progress = (math.sin(self.demo_animation_time * 0.8) + 1) / 2
            
            start_x = demo_x + 50
            start_y = demo_y + demo_height // 2
            end_x = demo_x + demo_width - 50
            
            # Позиция курсора движется от начала к концу и обратно
            self.demo_cursor_pos = [
                start_x + (end_x - start_x) * progress,
                start_y
            ]
            
        elif self.exercise_id == 'sorting':
            # Для сортировки - анимируем перемещение объекта в контейнер
            pass  # Реализация будет добавлена позже
            
        elif self.exercise_id == 'sequence':
            # Для последовательности - мигание ячеек в определенном порядке
            pass  # Реализация будет добавлена позже
            
        elif self.exercise_id == 'fast_fingers':
            # Для быстрых пальчиков - появление и исчезновение объектов
            pass  # Реализация будет добавлена позже
