"""
Экран выбора упражнения для приложения NeuroGym
"""

import pygame
from .base_screen import BaseScreen
from ..config import COLORS, EXERCISES, SCREEN_PADDING

class ExerciseSelection(BaseScreen):
    # Параметры карточек упражнений (используются при отрисовке и обработке кликов)
    CARD_HEIGHT = 120
    CARD_SPACING = 20
    CARD_START_Y = SCREEN_PADDING + 80

    def __init__(self, screen_manager, screen):
        """
        Инициализация экрана выбора упражнения
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
        """
        super().__init__(screen_manager, screen)
        
        # Текущий индекс выбранного упражнения
        self.selected_exercise_index = 0

        self.game = self.screen_manager.game
        
        # Видимое количество упражнений (для скроллинга, если упражнений много)
        self.visible_exercises = 3
        
        # Прогресс по упражнениям (в реальном приложении должен загружаться из сохранения)
        self.exercise_progress = {
            'pathfinder': {'stars': 0},
            'trajectory': {'stars': 0},
            'sorting': {'stars': 0},
            'sequence': {'stars': 0},
            'fast_fingers': {'stars': 0}
        }
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса экрана выбора упражнения
        """
        # Очистка кнопок
        self.buttons = []
        
        # Стандартная кнопка "Назад" в левом верхнем углу
        self.create_back_button('main_menu', 'Назад')
        
        # Кнопка "Начать" для запуска выбранного упражнения
        start_button_width = 150
        start_button_height = 50
        start_button_x = self.width - start_button_width - SCREEN_PADDING
        start_button_y = self.height - start_button_height - SCREEN_PADDING
        
        self.create_button(
            "Начать", 
            start_button_x, start_button_y, 
            start_button_width, start_button_height, 
            action=self._start_selected_exercise,
            color=COLORS['POSITIVE_GREEN'],
            font_size='MEDIUM'
        )
        
        # Кнопки для навигации по списку упражнений (стрелки вверх/вниз)
        arrow_button_size = 40
        arrow_button_x = self.width - arrow_button_size - SCREEN_PADDING
        arrow_up_y = self.height // 2 - arrow_button_size - 10
        arrow_down_y = self.height // 2 + 10
        
        self.arrow_up_button = self.create_button(
            "", 
            arrow_button_x, arrow_up_y, 
            arrow_button_size, arrow_button_size, 
            action=self._select_previous_exercise,
            font_size='SMALL'
         )

        self.arrow_down_button = self.create_button(
            "", 
            arrow_button_x, arrow_down_y, 
            arrow_button_size, arrow_button_size, 
            action=self._select_next_exercise,
            font_size='SMALL'
         )
        
    def _select_previous_exercise(self):
        """
        Выбор предыдущего упражнения в списке
        """
        if self.selected_exercise_index > 0:
            self.selected_exercise_index -= 1
            
    def _select_next_exercise(self):
        """
        Выбор следующего упражнения в списке
        """
        if self.selected_exercise_index < len(EXERCISES) - 1:
            self.selected_exercise_index += 1
            
    def _start_selected_exercise(self):
        """
        Запуск выбранного упражнения
        """
        selected_exercise = EXERCISES[self.selected_exercise_index]
        exercise_id = selected_exercise['id']
        # Переход к экрану инструкций с передачей идентификатора упражнения
        self.transition_to('instructions', exercise_id=exercise_id)
        
    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий экрана выбора упражнения
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        super().handle_events(events, cursor_pos)
        
        for event in events:
            # Обработка кликов по карточкам упражнений
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._check_exercise_cards_click(event.pos)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._select_previous_exercise()
                elif event.key == pygame.K_DOWN:
                    self._select_next_exercise()
                elif event.key == pygame.K_RETURN:
                    self._start_selected_exercise()
    
    def update(self, dt):
        """
        Обновление экрана выбора упражнения
        
        Args:
            dt: время в секундах с последнего обновления
        """
        pass
        
    def draw(self):
        """
        Отрисовка экрана выбора упражнения
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Отрисовка заголовка
        title_text = self.fonts['LARGE'].render("Выбор упражнения", True, COLORS['PRIMARY_BLUE'])
        title_rect = title_text.get_rect(center=(self.width // 2, SCREEN_PADDING + 30))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка списка упражнений
        self._draw_exercise_list()
        
        # Отрисовка кнопок
        self.draw_buttons()
        self._draw_arrow_icons()
        
        # Отображение информации о выбранном уровне сложности
        difficulty_name = self.game.get_difficulty()
        difficulty_label = self.fonts['MEDIUM'].render(f"Уровень сложности: {difficulty_name}", True, COLORS['TEXT_DARK'])
        difficulty_rect = difficulty_label.get_rect(
            center=(self.width // 2, self.height - SCREEN_PADDING - 80)
        )
        self.screen.blit(difficulty_label, difficulty_rect)
        
    def _card_layout(self):
        """Возвращает (card_width, card_x, start_index, end_index) для текущей раскладки."""
        card_width = int(self.width * 0.7)
        card_x = (self.width - card_width) // 2
        start_index = max(0, min(self.selected_exercise_index, len(EXERCISES) - self.visible_exercises))
        end_index = min(start_index + self.visible_exercises, len(EXERCISES))
        return card_width, card_x, start_index, end_index

    def _draw_exercise_list(self):
        """
        Отрисовка списка упражнений с информацией о каждом
        """
        card_width, card_x, start_index, end_index = self._card_layout()
        
        for i in range(start_index, end_index):
            exercise = EXERCISES[i]
            
            # Координаты текущей карточки
            y_pos = self.CARD_START_Y + (i - start_index) * (self.CARD_HEIGHT + self.CARD_SPACING)
            
            # Цвет карточки (выделяем выбранное упражнение)
            card_color = COLORS['PRIMARY_BLUE'] if i == self.selected_exercise_index else COLORS['PRIMARY_BLUE'] + (80,)
            
            # Отрисовка фона карточки
            pygame.draw.rect(self.screen, card_color, 
                          (card_x, y_pos, card_width, self.CARD_HEIGHT))
            
            # Отрисовка названия упражнения
            name_text = self.fonts['LARGE'].render(exercise['name'], True, COLORS['TEXT_LIGHT'])
            name_rect = name_text.get_rect(
                topleft=(card_x + 20, y_pos + 15)
            )
            self.screen.blit(name_text, name_rect)
            
            # Отрисовка описания упражнения
            desc_text = self.fonts['SMALL'].render(exercise['description'], True, COLORS['TEXT_LIGHT'])
            desc_rect = desc_text.get_rect(
                topleft=(card_x + 20, y_pos + 55)
            )
            self.screen.blit(desc_text, desc_rect)
            
            # Отрисовка прогресса упражнения (звезды)
            self._draw_exercise_progress(exercise['id'], card_x + card_width - 120, y_pos + self.CARD_HEIGHT - 30)
    
    def _check_exercise_cards_click(self, pos):
        """
        Проверка клика по карточкам упражнений
        
        Args:
            pos: координаты клика (x, y)
        """
        card_width, card_x, start_index, end_index = self._card_layout()
        
        for i in range(start_index, end_index):
            y_pos = self.CARD_START_Y + (i - start_index) * (self.CARD_HEIGHT + self.CARD_SPACING)
            card_rect = pygame.Rect(card_x, y_pos, card_width, self.CARD_HEIGHT)
            
            if card_rect.collidepoint(pos):
                self.selected_exercise_index = i
                # При двойном клике переходим на экран инструкций
                if pygame.time.get_ticks() - getattr(self, 'last_click_time', 0) < 500:
                    exercise_id = EXERCISES[self.selected_exercise_index]['id']
                    self.transition_to('instructions', exercise_id=exercise_id)
                self.last_click_time = pygame.time.get_ticks()
                return True
                
        return False

    def _draw_arrow_icons(self):
        """Рисует стрелки поверх кнопок навигации, чтобы избежать проблем с символами шрифта."""
        arrow_color = COLORS['TEXT_LIGHT']
        size = 10
        if getattr(self, 'arrow_up_button', None):
            rect = self.arrow_up_button['rect']
            cx, cy = rect.center
            points = [
                (cx, cy - size),
                (cx - size, cy + size),
                (cx + size, cy + size)
            ]
            pygame.draw.polygon(self.screen, arrow_color, points)
        if getattr(self, 'arrow_down_button', None):
            rect = self.arrow_down_button['rect']
            cx, cy = rect.center
            points = [
                (cx - size, cy - size),
                (cx + size, cy - size),
                (cx, cy + size)
            ]
            pygame.draw.polygon(self.screen, arrow_color, points)
    
    def _draw_exercise_progress(self, exercise_id, x, y):
        """
        Отрисовка прогресса упражнения в виде звезд
        
        Args:
            exercise_id: идентификатор упражнения
            x, y: координаты для отрисовки
        """
        # Получаем прогресс для данного упражнения
        stars = self.exercise_progress.get(exercise_id, {}).get('stars', 0)
        max_stars = 3
        
        # Размер звезды
        star_size = 25
        star_spacing = 5
        
        for i in range(max_stars):
            # Координаты текущей звезды
            star_x = x + i * (star_size + star_spacing)
            
            # Цвет звезды (золотой для заработанных, серый для незаработанных)
            star_color = COLORS['ACCENT_YELLOW'] if i < stars else COLORS['PRIMARY_BLUE'] + (50,)
            
            # Рисуем звезду (упрощенную, в виде круга)
            pygame.draw.circle(self.screen, star_color, (star_x, y), star_size // 2)
