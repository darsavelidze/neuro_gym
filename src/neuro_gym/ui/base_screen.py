"""
Базовый класс экрана для приложения NeuroGym
Все экраны приложения должны наследоваться от этого класса
"""

import pygame

from ..config import COLORS, FONT_FILE, FONT_SIZES


class BaseScreen:
    def __init__(self, screen_manager, screen):
        """Инициализация базового класса экрана"""
        self.screen_manager = screen_manager
        self.context = getattr(screen_manager, 'context', None)
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.running = True
        self.fonts = self._initialize_fonts()
        self.buttons = []
        self.next_screen = None
        self.layout_padding = 16
        self.layout_spacing = 12
        self.back_button = None  # Стандартная кнопка назад
    
    def _initialize_fonts(self):
        """Инициализация шрифтов разных размеров"""
        fonts = {}
        try:
            for size_name, size in FONT_SIZES.items():
                fonts[size_name] = pygame.font.Font(FONT_FILE, size)
        except Exception as e:
            print(f"Ошибка загрузки шрифта: {e}")
            for size_name, size in FONT_SIZES.items():
                fonts[size_name] = pygame.font.SysFont('Arial', size)
        return fonts
    
    def handle_events(self, events, cursor_pos=None):
        """Обработка событий (клавиатура, мышь, жесты)"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                if hasattr(self.screen_manager, 'stop'):
                    self.screen_manager.stop()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self._update_button_hover_states(event.pos)
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
        if cursor_pos:
            self._handle_gesture_hover(cursor_pos)
            self._update_button_hover_states(cursor_pos)

    def set_context(self, context):
        """Устанавливает общий контекст зависимостей для экрана."""
        self.context = context

    def on_enter(self, params=None):
        """Хук при входе на экран (может быть переопределен)."""
        self.running = True
        self.transition_params = params or {}

    def on_exit(self):
        """Хук при выходе с экрана (может быть переопределен)."""
        return
    
    def _handle_click(self, pos):
        """Обработка клика мышью или жеста"""
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                button['pressed'] = True
                button['press_time'] = pygame.time.get_ticks()
                if 'action' in button:
                    button['action']()
    
    def _handle_gesture_hover(self, pos):
        """Обработка жеста задержки (наведение и удержание)"""
        pass
    
    def _handle_keydown(self, event):
        """Обработка нажатий клавиш"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
    
    def _update_button_hover_states(self, pos):
        """Обновление состояния наведения для всех кнопок"""
        for button in self.buttons:
            button['is_hovered'] = button['rect'].collidepoint(pos)
    
    def update(self, dt):
        """Обновление состояния экрана"""
        pass
    
    def draw(self):
        """Отрисовка экрана"""
        self.screen.fill(COLORS['BACKGROUND'])
    
    def _check_button_collision(self, rect, safety_margin=5):
        """Проверка пересечения кнопки с другими кнопками"""
        check_rect = rect.inflate(safety_margin * 2, safety_margin * 2)
        for button in self.buttons:
            if check_rect.colliderect(button['rect']):
                return True
        return False
    
    def _resolve_button_position(self, rect):
        """Сдвигаем кнопку вниз, если она пересекается с существующими"""
        if not self.buttons:
            return rect
        safety_margin = self.layout_spacing
        max_iterations = 50
        iterations = 0
        while self._check_button_collision(rect, safety_margin) and iterations < max_iterations:
            rect.y += safety_margin
            if rect.bottom > self.height - self.layout_padding:
                rect.y = self.height - self.layout_padding - rect.height
                break
            iterations += 1
        return rect
    
    def auto_layout_vertical(self, container_rect=None, alignment='center'):
        """Авторазмещение кнопок вертикально с равными отступами"""
        if not self.buttons:
            return
        if container_rect is None:
            container_rect = pygame.Rect(self.layout_padding, self.layout_padding,
                                         self.width - 2 * self.layout_padding,
                                         self.height - 2 * self.layout_padding)
        y = container_rect.top
        for btn in self.buttons:
            r = btn['rect']
            r.y = y
            if alignment == 'left':
                r.x = container_rect.left
            elif alignment == 'right':
                r.x = container_rect.right - r.width
            else:
                r.x = container_rect.centerx - r.width // 2
            y = r.bottom + self.layout_spacing
    
    def create_button(self, text, x, y, width, height, action=None, 
                     color=COLORS['PRIMARY_BLUE'], hover_color=None, 
                     text_color=COLORS['TEXT_LIGHT'], font_size='MEDIUM'):
        """Создание кнопки"""
        if hover_color is None:
            hover_color = tuple(min(c + 40, 255) for c in color)
        
        rect = pygame.Rect(x, y, width, height)
        
        if self._check_button_collision(rect):
            rect = self._resolve_button_position(rect)
        
        button = {
            'rect': rect,
            'text': text,
            'color': color,
            'hover_color': hover_color,
            'text_color': text_color,
            'font': self.fonts[font_size],
            'action': action,
            'is_hovered': False,
            'hover_time': 0,
            'pressed': False,
            'press_time': 0,
            'press_duration': 150
        }
        
        self.buttons.append(button)
        return button
    
    def draw_buttons(self):
        """Отрисовка всех кнопок"""
        current_time = pygame.time.get_ticks()
        for button in self.buttons:
            rect = button['rect']
            base_color = button['hover_color'] if button['is_hovered'] else button['color']
            
            if button['pressed'] and current_time - button['press_time'] < button['press_duration']:
                shade = 30
                draw_color = tuple(max(c - shade, 0) for c in base_color)
            else:
                button['pressed'] = False
                draw_color = base_color
            
            pygame.draw.rect(self.screen, draw_color, rect, border_radius=10)
            
            text_surface = button['font'].render(button['text'], True, button['text_color'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
            pygame.draw.rect(self.screen, COLORS['BLACK'], rect, width=1, border_radius=10)
    
    def transition_to(self, next_screen, **params):
        """Переход к следующему экрану"""
        self.next_screen = next_screen
        self.transition_params = params
    
    def create_back_button(self, back_screen='main_menu', back_text='Назад'):
        """
        Создание стандартной кнопки "Назад" в левом верхнем углу
        
        Args:
            back_screen: экран, на который происходит возврат
            back_text: текст на кнопке
        """
        back_button_width = 120
        back_button_height = 50
        back_button_x = 20
        back_button_y = 20
        
        self.back_button = self.create_button(
            back_text,
            back_button_x,
            back_button_y,
            back_button_width,
            back_button_height,
            action=lambda: self.transition_to(back_screen),
            color=COLORS['PRIMARY_BLUE'],
            font_size='MEDIUM'
        )
        
        return self.back_button
