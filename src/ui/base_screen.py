"""
Базовый класс экрана для приложения NeuroGym
Все экраны приложения должны наследоваться от этого класса
"""

import pygame
import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from config import COLORS, FONT_FILE, FONT_SIZES

class BaseScreen:
    def __init__(self, screen_manager, screen):
        """
        Инициализация базового класса экрана
        
        Args:
            screen_manager: менеджер экранов для управления переходами между экранами
            screen: поверхность pygame для отрисовки
        """
        self.screen_manager = screen_manager
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.running = True
        self.fonts = self._initialize_fonts()
        self.buttons = []
        self.next_screen = None
    
    def _initialize_fonts(self):
        """
        Инициализация шрифтов разных размеров
        
        Returns:
            dict: словарь с различными размерами шрифтов
        """
        fonts = {}
        try:
            for size_name, size in FONT_SIZES.items():
                fonts[size_name] = pygame.font.Font(FONT_FILE, size)
        except Exception as e:
            print(f"Ошибка загрузки шрифта: {e}")
            # Если основной шрифт не загружен, используем системный шрифт
            for size_name, size in FONT_SIZES.items():
                fonts[size_name] = pygame.font.SysFont('Arial', size)
        return fonts
    
    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий (клавиатура, мышь, жесты)
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            # Обработка событий мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            
            # Обработка движения мыши для эффекта наведения
            elif event.type == pygame.MOUSEMOTION:
                self._update_button_hover_states(event.pos)
            
            # Обработка клавиатуры
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
        # Обработка жеста задержки (если есть позиция курсора)
        if cursor_pos:
            self._handle_gesture_hover(cursor_pos)
            self._update_button_hover_states(cursor_pos)
    
    def _handle_click(self, pos):
        """
        Обработка клика мышью или жеста
        
        Args:
            pos: координаты (x, y) клика или жеста
        """
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                # Добавляем эффект нажатия (анимация)
                button['pressed'] = True
                button['press_time'] = pygame.time.get_ticks()
                
                # Вызываем действие кнопки
                if 'action' in button:
                    button['action']()
    
    def _handle_gesture_hover(self, pos):
        """
        Обработка жеста задержки (наведение и удержание)
        Вызывается при каждом обновлении для проверки задержки на элементах
        
        Args:
            pos: координаты (x, y) курсора жеста
        """
        # Реализация будет дополнена в классе-наследнике
        pass
    
    def _handle_keydown(self, event):
        """
        Обработка нажатий клавиш
        
        Args:
            event: событие нажатия клавиши
        """
        if event.key == pygame.K_ESCAPE:
            self.running = False
    
    def _update_button_hover_states(self, pos):
        """
        Обновление состояния наведения для всех кнопок
        
        Args:
            pos: координаты курсора (x, y)
        """
        for button in self.buttons:
            # Обновляем состояние наведения
            prev_state = button['is_hovered']
            button['is_hovered'] = button['rect'].collidepoint(pos)
            
            # Звуковой эффект при наведении (если состояние изменилось с False на True)
            if not prev_state and button['is_hovered']:
                # Здесь в будущем можно добавить звук наведения
                pass
    
    def update(self, dt):
        """
        Обновление состояния экрана
        
        Args:
            dt: время в секундах с последнего обновления
        """
        pass
    
    def draw(self):
        """
        Отрисовка экрана
        """
        # Заливка фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
    
    def _check_button_collision(self, rect, safety_margin=5):
        """
        Проверка пересечения кнопки с другими кнопками
        
        Args:
            rect: прямоугольник проверяемой кнопки
            safety_margin: дополнительный отступ для предотвращения слишком близкого расположения
            
        Returns:
            bool: True, если пересечение найдено, иначе False
        """
        # Увеличиваем rect на safety_margin для проверки "близкого расположения"
        check_rect = rect.inflate(safety_margin * 2, safety_margin * 2)
        
        for button in self.buttons:
            if check_rect.colliderect(button['rect']):
                return True
        return False
    
    def create_button(self, text, x, y, width, height, action=None, 
                     color=COLORS['PRIMARY_BLUE'], hover_color=None, 
                     text_color=COLORS['TEXT_LIGHT'], font_size='MEDIUM'):
        """
        Создание кнопки
        
        Args:
            text: текст кнопки
            x, y: координаты верхнего левого угла кнопки
            width, height: ширина и высота кнопки
            action: функция, вызываемая при нажатии на кнопку
            color: цвет кнопки
            hover_color: цвет кнопки при наведении
            text_color: цвет текста
            font_size: размер шрифта
            
        Returns:
            dict: словарь с параметрами кнопки
        """
        if hover_color is None:
            # Если цвет при наведении не задан, делаем его заметно светлее основного
            # для лучшей обратной связи
            hover_color = tuple(min(c + 40, 255) for c in color)
        
        # Создаем прямоугольник для кнопки
        rect = pygame.Rect(x, y, width, height)
        
        # Проверка пересечения с существующими кнопками
        if self._check_button_collision(rect):
            print(f"Предупреждение: кнопка '{text}' пересекается с другими кнопками!")
        
        button = {
            'rect': rect,
            'text': text,
            'color': color,
            'hover_color': hover_color,
            'text_color': text_color,
            'font': self.fonts[font_size],
            'action': action,
            'is_hovered': False,
            'hover_time': 0,      # для отслеживания времени наведения
            'pressed': False,     # состояние нажатия
            'press_time': 0,      # время последнего нажатия
            'press_duration': 150 # длительность анимации нажатия в миллисекундах
        }
        
        self.buttons.append(button)
        return button
    
    def draw_buttons(self):
        """
        Отрисовка всех кнопок
        """
        current_time = pygame.time.get_ticks()
        
        for button in self.buttons:
            # Обработка анимации нажатия
            if button['pressed']:
                # Если время анимации истекло, сбрасываем состояние нажатия
                if current_time - button['press_time'] > button['press_duration']:
                    button['pressed'] = False
            
            # Определение цвета и смещения в зависимости от состояния
            button_rect = button['rect'].copy()
            color = button['hover_color'] if button['is_hovered'] else button['color']
            
            # Эффект нажатия - немного затемняем цвет и смещаем кнопку вниз
            if button['pressed']:
                # Затемняем цвет кнопки при нажатии
                color = tuple(max(0, c - 30) for c in color)
                # Смещаем кнопку на 2 пикселя вниз для эффекта нажатия
                button_rect.y += 2
            
            # Параметры для скругленных углов
            border_radius = min(10, button_rect.width // 4, button_rect.height // 4)
            
            # Отрисовка тени кнопки (смещение на 3 пикселя вниз и вправо)
            # Не рисуем тень для нажатой кнопки
            if not button['pressed']:
                shadow_rect = button_rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=border_radius)
            
            # Отрисовка прямоугольника кнопки со скругленными углами
            pygame.draw.rect(self.screen, color, button_rect, border_radius=border_radius)
            
            # Добавление эффекта обводки при наведении (только если кнопка не нажата)
            if button['is_hovered'] and not button['pressed']:
                border_color = (255, 255, 255, 150)  # Белая полупрозрачная обводка
                pygame.draw.rect(self.screen, border_color, button_rect, 
                              width=2, border_radius=border_radius)
            
            # Добавление внутренней подсветки для кнопки (эффект объема)
            highlight_rect = button_rect.copy()
            highlight_rect.height = max(3, button_rect.height // 8)
            pygame.draw.rect(self.screen, (255, 255, 255, 50), highlight_rect, 
                          border_radius=border_radius)
            
            # Отрисовка текста на кнопке
            text_surface = button['font'].render(button['text'], True, button['text_color'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def transition_to(self, next_screen, **params):
        """
        Переход к следующему экрану
        
        Args:
            next_screen: идентификатор следующего экрана
            **params: дополнительные параметры для передачи экрану
        """
        # Только устанавливаем идентификатор следующего экрана
        # Фактический переход будет выполнен в игровом цикле
        self.next_screen = next_screen
        # Сохраняем параметры для передачи следующему экрану
        setattr(self, 'transition_params', params)
