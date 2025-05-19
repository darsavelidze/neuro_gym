"""
Экран главного меню приложения NeuroGym
"""

import pygame
import sys
import math
import random
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from ui.base_screen import BaseScreen
from config import COLORS, DIFFICULTY_LEVELS, BUTTON_PADDING, SCREEN_PADDING

class MainMenu(BaseScreen):
    def __init__(self, screen_manager, screen):
        """
        Инициализация экрана главного меню
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
        """
        super().__init__(screen_manager, screen)
        
        # Получаем ссылки на менеджеры
        self.progress_manager = self.screen_manager.game.progress_manager
        self.localization = self.screen_manager.game.localization_manager
        self.sound_manager = self.screen_manager.game.sound_manager
        
        # Активный уровень сложности (получаем из менеджера прогресса)
        difficulty = self.progress_manager.get_difficulty()
        self.selected_difficulty = DIFFICULTY_LEVELS.index(difficulty) if difficulty in DIFFICULTY_LEVELS else 0
        
        # Получаем количество собранных звезд из менеджера прогресса
        self.stars_collected = self.progress_manager.get_total_stars()
        
        # Инициализация анимированного фона
        self.particles = []
        self.init_particles(20)  # Создаем 20 частиц для фона
        self.last_particle_time = pygame.time.get_ticks()
        self.particle_spawn_delay = 2000  # Миллисекунды между созданием новых частиц
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса главного меню
        """
        # Очистка кнопок
        self.buttons = []
        
        # Определение размеров и отступов
        button_width = int(self.width * 0.4)
        button_height = 70
        button_spacing = 20
        start_y = int(self.height * 0.35)
        
        # Центрирование кнопок по горизонтали
        button_x = (self.width - button_width) // 2
        
        # Кнопка "Упражнения"
        self.create_button(
            self.localization.get_text('exercises'), 
            button_x, start_y, 
            button_width, button_height, 
            action=lambda: self.transition_to('exercise_selection'),
            font_size='LARGE'
        )
        
        # Кнопка "Достижения"
        self.create_button(
            self.localization.get_text('achievements'), 
            button_x, start_y + button_height + button_spacing, 
            button_width, button_height,
            action=lambda: self.transition_to('achievements'),
            font_size='LARGE'
        )
        
        # Кнопка "Настройки"
        self.create_button(
            self.localization.get_text('settings'), 
            button_x, start_y + 2 * (button_height + button_spacing), 
            button_width, button_height,
            action=lambda: self.transition_to('settings'),
            font_size='LARGE'
        )
        
        # Кнопка "Выход"
        self.create_button(
            self.localization.get_text('exit'), 
            button_x, self.height - button_height - SCREEN_PADDING, 
            button_width, button_height,
            action=self._exit_game,
            color=COLORS['NEGATIVE_RED'],
            font_size='LARGE'
        )
        
        # Создание кнопок уровня сложности
        diff_button_width = int(button_width / 3) - 10
        diff_button_height = 50
        diff_y = start_y + 3 * (button_height + button_spacing) + button_spacing
        
        # Локализованные названия уровней сложности
        diff_names = [
            self.localization.get_text('easy'),
            self.localization.get_text('medium'),
            self.localization.get_text('hard')
        ]
        
        for i, diff in enumerate(DIFFICULTY_LEVELS):
            diff_x = button_x + i * (diff_button_width + 10)
            self.create_button(
                diff_names[i], 
                diff_x, diff_y, 
                diff_button_width, diff_button_height,
                action=lambda i=i: self._set_difficulty(i),
                color=COLORS['PRIMARY_BLUE'] if i != self.selected_difficulty else COLORS['ACCENT_YELLOW'],
                text_color=COLORS['TEXT_LIGHT'] if i != self.selected_difficulty else COLORS['TEXT_DARK'],
                font_size='MEDIUM'
            )
            
    def _set_difficulty(self, difficulty_index):
        """
        Установка уровня сложности
        
        Args:
            difficulty_index: индекс выбранного уровня сложности
        """
        self.selected_difficulty = difficulty_index
        
        # Сохраняем выбранную сложность в менеджере прогресса
        difficulty = DIFFICULTY_LEVELS[difficulty_index]
        self.screen_manager.game.set_difficulty(difficulty)
        
        # Воспроизводим звук нажатия кнопки
        self.sound_manager.play_sound('button_click')
        
        # Пересоздаем элементы интерфейса для обновления внешнего вида кнопок сложности
        self._create_ui_elements()
        
    def _exit_game(self):
        """
        Выход из игры
        """
        # Воспроизводим звук нажатия кнопки перед выходом
        self.sound_manager.play_sound('button_click')
        
        # Сохраняем прогресс пользователя
        self.progress_manager.save_progress()
        
        # Завершаем работу игры
        self.running = False
        
    def update(self, dt):
        """
        Обновление главного меню
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Обновление частиц фона
        self.update_particles(dt)
        
    def draw(self):
        """
        Отрисовка главного меню
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Отрисовка фона с частицами
        self.draw_particles()
        
        # Отрисовка заголовка
        title_text = self.fonts['EXTRA_LARGE'].render(self.localization.get_text('app_name'), True, COLORS['PRIMARY_BLUE'])
        title_rect = title_text.get_rect(center=(self.width // 2, self.height * 0.15))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка кнопок
        self.draw_buttons()
        
        # Обновляем количество звезд из менеджера прогресса
        self.stars_collected = self.progress_manager.get_total_stars()
        
        # Отрисовка метки выбора уровня сложности
        difficulty_label = self.fonts['MEDIUM'].render(f"{self.localization.get_text('difficulty')}:", True, COLORS['TEXT_DARK'])
        diff_label_rect = difficulty_label.get_rect(
            center=(self.width // 2, self.height * 0.58 - 30)
        )
        self.screen.blit(difficulty_label, diff_label_rect)
        
        # Отображение собранных звездочек (с визуальными звездами)
        stars_text = self.localization.get_text('stars_collected')
        stars_label = self.fonts['MEDIUM'].render(stars_text, True, COLORS['TEXT_DARK'])
        stars_rect = stars_label.get_rect(
            center=(self.width // 2, self.height * 0.75 - 30)
        )
        self.screen.blit(stars_label, stars_rect)
        
        # Рисуем визуальные звезды
        self._draw_star_display(self.width // 2, self.height * 0.75 + 10, self.stars_collected)
        
        # Отображение индикатора общего прогресса
        self._draw_progress_indicator()
        
    def _draw_progress_indicator(self):
        """
        Отрисовка индикатора общего прогресса
        """
        # Параметры индикатора прогресса
        progress_width = int(self.width * 0.5)
        progress_height = 24  # Увеличенная высота для лучшего вида
        progress_x = (self.width - progress_width) // 2
        progress_y = int(self.height * 0.8)
        
        # Фон индикатора с закругленными углами и небольшой тенью
        shadow_offset = 3
        pygame.draw.rect(self.screen, (0, 0, 0, 80), 
                       (progress_x - 2 + shadow_offset, progress_y - 2 + shadow_offset, 
                        progress_width + 4, progress_height + 4),
                       border_radius=12)
                       
        # Фон индикатора
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'], 
                       (progress_x - 2, progress_y - 2, 
                        progress_width + 4, progress_height + 4),
                       border_radius=12)
        
        # Расчет прогресса на основе данных из менеджера прогресса
        # Максимальное количество звезд = 15 (3 звезды * 5 упражнений)
        max_stars = 15
        progress_percent = min(1.0, self.stars_collected / max_stars)
        filled_width = int(progress_width * progress_percent)
        
        # Создаем градиент для заполненной части
        if filled_width > 0:
            # Создаем временную поверхность для градиента
            gradient_surface = pygame.Surface((filled_width, progress_height), pygame.SRCALPHA)
            
            # Определяем цвета для градиента
            start_color = COLORS['ACCENT_YELLOW']
            end_color = COLORS['POSITIVE_GREEN']
            
            # Рисуем градиент
            for x in range(filled_width):
                blend_factor = x / filled_width
                color = [
                    int(start_color[0] * (1 - blend_factor) + end_color[0] * blend_factor),
                    int(start_color[1] * (1 - blend_factor) + end_color[1] * blend_factor),
                    int(start_color[2] * (1 - blend_factor) + end_color[2] * blend_factor)
                ]
                pygame.draw.line(gradient_surface, color, (x, 0), (x, progress_height))
            
            # Рисуем закругленные углы
            pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'], 
                        (progress_x, progress_y, filled_width, progress_height),
                        border_radius=10)
                        
            # Накладываем градиент
            self.screen.blit(gradient_surface, (progress_x, progress_y))
            
            # Добавляем мягкий блик сверху для 3D-эффекта
            highlight_height = progress_height // 3
            highlight_rect = pygame.Rect(progress_x, progress_y, filled_width, highlight_height)
            pygame.draw.rect(gradient_surface, (255, 255, 255, 80), 
                        (0, 0, filled_width, highlight_height), 
                        border_radius=10)
            self.screen.blit(gradient_surface, (progress_x, progress_y), 
                         special_flags=pygame.BLEND_RGBA_ADD)
                       
        # Добавляем текст с процентом завершения
        percent_text = f"{int(progress_percent * 100)}%"
        
        # Создаем текст с тенью для лучшей читаемости
        text_shadow = self.fonts['SMALL'].render(percent_text, True, (0, 0, 0, 150))
        text_shadow_rect = text_shadow.get_rect(center=(progress_x + progress_width // 2 + 1, progress_y + progress_height // 2 + 1))
        
        percent_label = self.fonts['SMALL'].render(percent_text, True, COLORS['TEXT_LIGHT'])
        percent_rect = percent_label.get_rect(center=(progress_x + progress_width // 2, progress_y + progress_height // 2))
        
        # Отрисовка тени и текста
        self.screen.blit(text_shadow, text_shadow_rect)
        self.screen.blit(percent_label, percent_rect)
        
        # Добавляем текст с общим прогрессом под индикатором
        progress_text = f"{self.stars_collected}/{max_stars} {self.localization.get_text('stars')}"
        progress_label = self.fonts['SMALL'].render(progress_text, True, COLORS['TEXT_DARK'])
        progress_rect = progress_label.get_rect(center=(progress_x + progress_width // 2, progress_y + progress_height + 20))
        self.screen.blit(progress_label, progress_rect)
        
    def _draw_star_display(self, center_x, center_y, star_count):
        """
        Отрисовка визуального отображения звезд
        
        Args:
            center_x: x-координата центра отображения
            center_y: y-координата центра отображения
            star_count: количество собранных звезд
        """
        # Настройки отображения звезд
        star_size = 40
        star_spacing = 10
        max_stars_per_row = 5
        
        # Определение количества строк и звезд в последней строке
        rows = (star_count + max_stars_per_row - 1) // max_stars_per_row
        stars_in_last_row = star_count % max_stars_per_row
        if stars_in_last_row == 0 and star_count > 0:
            stars_in_last_row = max_stars_per_row
        
        # Отрисовка звезд
        for row in range(min(rows, 3)):  # Максимум 3 ряда для компактности
            # Определение количества звезд в текущей строке
            if row == rows - 1 and stars_in_last_row != max_stars_per_row:
                stars_in_row = stars_in_last_row
            else:
                stars_in_row = max_stars_per_row
                
            # Если это последний ряд и звезд больше 15, отображаем +N
            if row == 2 and star_count > 15:
                extra_stars = star_count - 15
                stars_in_row = max_stars_per_row - 1  # Освобождаем место для "+N"
                
            # Вычисление общей ширины строки
            row_width = stars_in_row * (star_size + star_spacing) - star_spacing
            
            # Начальная позиция для текущей строки
            start_x = center_x - row_width / 2
            current_y = center_y + row * (star_size + 5)
            
            # Отрисовка звезд текущей строки
            for i in range(stars_in_row):
                current_x = start_x + i * (star_size + star_spacing)
                self._draw_star(current_x, current_y, star_size, COLORS['ACCENT_YELLOW'])
            
            # Если есть дополнительные звезды, отображаем "+N"
            if row == 2 and star_count > 15:
                plus_text = f"+{extra_stars}"
                plus_label = self.fonts['MEDIUM'].render(plus_text, True, COLORS['ACCENT_YELLOW'])
                plus_rect = plus_label.get_rect(
                    center=(start_x + row_width + star_size//2, current_y + star_size//2)
                )
                self.screen.blit(plus_label, plus_rect)
    
    def _draw_star(self, x, y, size, color):
        """
        Отрисовка звезды
        
        Args:
            x: x-координата центра звезды
            y: y-координата центра звезды
            size: размер звезды
            color: цвет звезды
        """
        # Вершины пятиконечной звезды
        points = []
        for i in range(10):
            radius = size / 2 if i % 2 == 0 else size / 5
            angle = math.pi / 2 + i * math.pi * 2 / 10
            points.append((
                x + radius * math.cos(angle),
                y + radius * math.sin(angle)
            ))
        
        # Рисуем тень
        shadow_points = [(x + 3, y + 3) for x, y in points]
        pygame.draw.polygon(self.screen, (0, 0, 0, 80), shadow_points)
        
        # Рисуем основную звезду
        pygame.draw.polygon(self.screen, color, points)
        
        # Добавляем блик для 3D-эффекта
        inner_points = []
        inner_size = size * 0.7
        for i in range(10):
            radius = inner_size / 2 if i % 2 == 0 else inner_size / 5
            angle = math.pi / 2 + i * math.pi * 2 / 10
            inner_points.append((
                x + radius * math.cos(angle),
                y + radius * math.sin(angle)
            ))
        
        # Рисуем внутреннюю часть звезды немного светлее
        lighter_color = (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40))
        pygame.draw.polygon(self.screen, lighter_color, inner_points)
    
    def init_particles(self, count):
        """
        Инициализация частиц для анимированного фона
        
        Args:
            count: количество создаваемых частиц
        """
        for _ in range(count):
            self._create_particle()
            
    def _create_particle(self):
        """
        Создание новой частицы для анимированного фона
        """
        # Случайная позиция
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        
        # Случайная скорость (медленное движение)
        speed_x = random.uniform(-0.5, 0.5)
        speed_y = random.uniform(-0.5, 0.5)
        
        # Случайный размер
        size = random.randint(5, 15)
        
        # Случайная прозрачность (очень прозрачные)
        alpha = random.randint(10, 40)
        
        # Случайный тип (0 - круг, 1 - квадрат, 2 - звезда)
        particle_type = random.choice([0, 1, 2])
        
        # Случайный цвет (из палитры приложения)
        base_color = random.choice([
            COLORS['PRIMARY_BLUE'],
            COLORS['ACCENT_YELLOW'],
            COLORS['POSITIVE_GREEN']
        ])
        
        # Добавляем частицу
        self.particles.append({
            'x': x,
            'y': y,
            'speed_x': speed_x,
            'speed_y': speed_y,
            'size': size,
            'alpha': alpha,
            'type': particle_type,
            'color': base_color,
            'angle': random.uniform(0, 360),  # Для вращения
            'rotation_speed': random.uniform(-0.5, 0.5)  # Скорость вращения
        })
        
    def update_particles(self, dt):
        """
        Обновление частиц анимированного фона
        
        Args:
            dt: время в секундах с последнего обновления
        """
        current_time = pygame.time.get_ticks()
        
        # Периодически добавляем новые частицы
        if current_time - self.last_particle_time > self.particle_spawn_delay:
            self._create_particle()
            self.last_particle_time = current_time
            
            # Если частиц слишком много, удаляем несколько
            if len(self.particles) > 30:
                self.particles = self.particles[-25:]  # Оставляем только 25 последних
                
        # Обновляем позиции всех частиц
        for particle in self.particles:
            # Обновление позиции
            particle['x'] += particle['speed_x'] * 60 * dt
            particle['y'] += particle['speed_y'] * 60 * dt
            
            # Обновление угла вращения
            particle['angle'] += particle['rotation_speed'] * 60 * dt
            
            # Если частица вышла за пределы экрана, возвращаем её с противоположной стороны
            if particle['x'] < -30:
                particle['x'] = self.width + 30
            elif particle['x'] > self.width + 30:
                particle['x'] = -30
                
            if particle['y'] < -30:
                particle['y'] = self.height + 30
            elif particle['y'] > self.height + 30:
                particle['y'] = -30
                
            # Медленно меняем прозрачность
            if random.random() < 0.01:
                particle['alpha'] += random.uniform(-2, 2)
                particle['alpha'] = max(5, min(40, particle['alpha']))
        
    def draw_particles(self):
        """
        Отрисовка частиц анимированного фона
        """
        for particle in self.particles:
            # Создаем цвет с заданной прозрачностью
            color = particle['color'] + (particle['alpha'],)
            
            # В зависимости от типа частицы выбираем способ отрисовки
            if particle['type'] == 0:  # Круг
                pygame.draw.circle(self.screen, color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
            elif particle['type'] == 1:  # Квадрат
                # Создаем повернутый прямоугольник
                rect = pygame.Rect(0, 0, particle['size'] * 1.5, particle['size'] * 1.5)
                rect.center = (int(particle['x']), int(particle['y']))
                
                # Создаем поверхность для поворота
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(surf, color, surf.get_rect(), border_radius=2)
                
                # Поворачиваем и отрисовываем
                rotated_surf = pygame.transform.rotate(surf, particle['angle'])
                rotated_rect = rotated_surf.get_rect(center=rect.center)
                self.screen.blit(rotated_surf, rotated_rect)
                
            elif particle['type'] == 2:  # Звезда
                # Упрощенная версия звезды (4 точки)
                size = particle['size'] * 1.2
                points = []
                
                for i in range(8):
                    angle = particle['angle'] + i * math.pi / 4
                    radius = size if i % 2 == 0 else size / 2
                    points.append((
                        particle['x'] + radius * math.cos(angle),
                        particle['y'] + radius * math.sin(angle)
                    ))
                    
                pygame.draw.polygon(self.screen, color, points)
