"""
Экран настроек для приложения NeuroGym
Позволяет пользователю настроить громкость, язык и другие параметры
"""

import pygame
from .base_screen import BaseScreen
from ..config import COLORS, SCREEN_PADDING

class SettingsScreen(BaseScreen):
    def __init__(self, screen_manager, screen):
        """
        Инициализация экрана настроек
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
        """
        super().__init__(screen_manager, screen)
        
        # Получаем ссылки на менеджеры
        self.sound_manager = self.screen_manager.game.sound_manager
        self.localization = self.screen_manager.game.localization_manager
        
        # Настройки (загружаем текущие значения из менеджеров)
        self.sound_volume = int(self.sound_manager.sound_volume * 100)  # от 0 до 100
        self.music_volume = int(self.sound_manager.music_volume * 100)  # от 0 до 100
        self.language = "ru" if self.localization.get_language() == "ru" else "en"
        
        # Режим ввода: 'mouse' или 'gesture'
        self.input_mode = self.screen_manager.game.input_handler.input_mode
        
        # Активный элемент ползунка (None, если не активен)
        self.active_slider = None
        
        # Создание элементов интерфейса
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса экрана настроек
        """
        # Очистка кнопок
        self.buttons = []
        
        # Стандартная кнопка "Назад" в левом верхнем углу
        self.create_back_button('main_menu', self.localization.get_text('back'))
        
        # Кнопки выбора языка
        lang_button_width = 150
        lang_button_height = 50
        lang_button_spacing = 20
        lang_start_x = (self.width - 2 * lang_button_width - lang_button_spacing) // 2
        lang_y = self.height // 2 + 100
        
        # Кнопка "Русский"
        self.create_button(
            "Русский", 
            lang_start_x, lang_y, 
            lang_button_width, lang_button_height, 
            action=lambda: self._set_language("ru"),
            color=COLORS['PRIMARY_BLUE'] if self.language == "ru" else COLORS['PRIMARY_BLUE'] + (80,),
            text_color=COLORS['TEXT_LIGHT'],
            font_size='MEDIUM'
        )
        
        # Кнопка "English"
        self.create_button(
            "English", 
            lang_start_x + lang_button_width + lang_button_spacing, lang_y, 
            lang_button_width, lang_button_height, 
            action=lambda: self._set_language("en"),
            color=COLORS['PRIMARY_BLUE'] if self.language == "en" else COLORS['PRIMARY_BLUE'] + (80,),
            text_color=COLORS['TEXT_LIGHT'],
            font_size='MEDIUM'
        )
        
        # Кнопки выбора режима ввода
        input_button_width = 180
        input_button_height = 50
        input_button_spacing = 20
        input_start_x = (self.width - 2 * input_button_width - input_button_spacing) // 2
        input_y = lang_y + 90

        mouse_label = self.localization.get_text('input_mouse') if self.localization else "Мышь"
        hand_label = self.localization.get_text('input_hand') if self.localization else "Рука (камера)"

        # Кнопка «Мышь»
        self.create_button(
            mouse_label,
            input_start_x, input_y,
            input_button_width, input_button_height,
            action=lambda: self._set_input_mode("mouse"),
            color=COLORS['PRIMARY_BLUE'] if self.input_mode == "mouse" else COLORS['PRIMARY_BLUE'] + (80,),
            text_color=COLORS['TEXT_LIGHT'],
            font_size='MEDIUM'
        )

        # Кнопка «Рука (камера)»
        self.create_button(
            hand_label,
            input_start_x + input_button_width + input_button_spacing, input_y,
            input_button_width, input_button_height,
            action=lambda: self._set_input_mode("gesture"),
            color=COLORS['POSITIVE_GREEN'] if self.input_mode == "gesture" else COLORS['PRIMARY_BLUE'] + (80,),
            text_color=COLORS['TEXT_LIGHT'],
            font_size='MEDIUM'
        )
        
        # Авторазмещение кнопок в нижней части экрана, чтобы они не перекрывались
        container_top = self.height // 2 + 90
        container_rect = pygame.Rect(
            self.layout_padding,
            container_top,
            self.width - 2 * self.layout_padding,
            self.height - container_top - self.layout_padding
        )
        self.auto_layout_vertical(container_rect, alignment='center')
        
    def _set_language(self, language):
        """
        Установка языка интерфейса
        
        Args:
            language: выбранный язык ("ru" или "en")
        """
        # Обновляем локальную переменную
        self.language = language
        
        # Устанавливаем язык в менеджере локализации
        self.localization.set_language(language)
        
        # Воспроизводим звук нажатия кнопки
        self.sound_manager.play_sound('button_click')
        
        # Пересоздаем элементы интерфейса для обновления внешнего вида кнопок
        self._create_ui_elements()

    def _set_input_mode(self, mode):
        """
        Переключение режима управления: 'mouse' или 'gesture'.
        
        Args:
            mode: режим ввода ("mouse" или "gesture")
        """
        self.sound_manager.play_sound('button_click')
        self.screen_manager.game.set_input_mode(mode)
        self.input_mode = self.screen_manager.game.input_handler.input_mode
        self._create_ui_elements()
        
    def handle_events(self, events, cursor_pos=None):
        """
        Обработка событий экрана настроек
        
        Args:
            events: список событий pygame
            cursor_pos: координаты курсора (x, y) при использовании жестов
        """
        # Сначала обрабатываем базовые события
        super().handle_events(events, cursor_pos)
        
        # Затем обрабатываем специфичные для настроек события
        mouse_pos = pygame.mouse.get_pos() if not cursor_pos else cursor_pos
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Проверка нажатия на ползунок регулировки громкости звуков
                if self._is_point_in_sound_slider(mouse_pos):
                    self.active_slider = "sound"
                    self._update_slider_value(mouse_pos)
                # Проверка нажатия на ползунок регулировки громкости музыки
                elif self._is_point_in_music_slider(mouse_pos):
                    self.active_slider = "music"
                    self._update_slider_value(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Прекращаем перетаскивание ползунка
                self.active_slider = None
                
            elif event.type == pygame.MOUSEMOTION:
                # Если перетаскиваем ползунок, обновляем его значение
                if self.active_slider:
                    self._update_slider_value(mouse_pos)
    
    def _is_point_in_sound_slider(self, pos):
        """
        Проверка, находится ли точка в области ползунка регулировки громкости звуков
        
        Args:
            pos: координаты точки (x, y)
            
        Returns:
            bool: True, если точка находится в области ползунка
        """
        slider_x, slider_y, slider_width, slider_height = self._get_sound_slider_rect()
        return (slider_x <= pos[0] <= slider_x + slider_width and
                slider_y - 10 <= pos[1] <= slider_y + slider_height + 10)
    
    def _is_point_in_music_slider(self, pos):
        """
        Проверка, находится ли точка в области ползунка регулировки громкости музыки
        
        Args:
            pos: координаты точки (x, y)
            
        Returns:
            bool: True, если точка находится в области ползунка
        """
        slider_x, slider_y, slider_width, slider_height = self._get_music_slider_rect()
        return (slider_x <= pos[0] <= slider_x + slider_width and
                slider_y - 10 <= pos[1] <= slider_y + slider_height + 10)
    
    def _update_slider_value(self, pos):
        """
        Обновление значения активного ползунка
        
        Args:
            pos: координаты курсора (x, y)
        """
        if not self.active_slider:
            return
            
        if self.active_slider == "sound":
            slider_x, _, slider_width, _ = self._get_sound_slider_rect()
            # Рассчитываем новое значение громкости звуков
            rel_x = max(0, min(pos[0] - slider_x, slider_width))
            self.sound_volume = int((rel_x / slider_width) * 100)
            # Обновляем громкость в звуковом менеджере
            self.sound_manager.set_sound_volume(self.sound_volume / 100.0)
            
        elif self.active_slider == "music":
            slider_x, _, slider_width, _ = self._get_music_slider_rect()
            # Рассчитываем новое значение громкости музыки
            rel_x = max(0, min(pos[0] - slider_x, slider_width))
            self.music_volume = int((rel_x / slider_width) * 100)
            # Обновляем громкость в звуковом менеджере
            self.sound_manager.set_music_volume(self.music_volume / 100.0)
    
    def _get_sound_slider_rect(self):
        """
        Получение координат и размеров ползунка регулировки громкости звуков
        
        Returns:
            tuple: (x, y, width, height)
        """
        slider_width = 300
        slider_height = 10
        slider_x = (self.width - slider_width) // 2
        slider_y = self.height // 3
        return slider_x, slider_y, slider_width, slider_height
    
    def _get_music_slider_rect(self):
        """
        Получение координат и размеров ползунка регулировки громкости музыки
        
        Returns:
            tuple: (x, y, width, height)
        """
        slider_width = 300
        slider_height = 10
        slider_x = (self.width - slider_width) // 2
        slider_y = self.height // 3 + 60
        return slider_x, slider_y, slider_width, slider_height
    
    def update(self, dt):
        """
        Обновление экрана настроек
        
        Args:
            dt: время в секундах с последнего обновления
        """
        pass
        
    def draw(self):
        """
        Отрисовка экрана настроек
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Отрисовка заголовка
        title_text = self.fonts['LARGE'].render(self.localization.get_text('settings'), True, COLORS['PRIMARY_BLUE'])
        title_rect = title_text.get_rect(center=(self.width // 2, SCREEN_PADDING + 50))
        self.screen.blit(title_text, title_rect)
        
        # Отрисовка элементов управления настройками
        self._draw_volume_sliders()
        self._draw_language_selector()
        self._draw_input_mode_selector()
        
        # Отрисовка кнопок
        self.draw_buttons()
    
    def _draw_volume_sliders(self):
        """
        Отрисовка ползунков регулировки громкости
        """
        # Параметры ползунков
        sound_label = self.fonts['MEDIUM'].render(self.localization.get_text('sound_effects'), True, COLORS['TEXT_DARK'])
        sound_label_rect = sound_label.get_rect(
            center=(self.width // 2, self.height // 3 - 30)
        )
        self.screen.blit(sound_label, sound_label_rect)
        
        music_label = self.fonts['MEDIUM'].render(self.localization.get_text('music'), True, COLORS['TEXT_DARK'])
        music_label_rect = music_label.get_rect(
            center=(self.width // 2, self.height // 3 + 30)
        )
        self.screen.blit(music_label, music_label_rect)
        
        # Отрисовка ползунка громкости звуков
        sound_slider_x, sound_slider_y, sound_slider_width, sound_slider_height = self._get_sound_slider_rect()
        
        # Фон ползунка
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (80,), 
                       (sound_slider_x, sound_slider_y, sound_slider_width, sound_slider_height))
        
        # Заполнение ползунка в зависимости от значения
        filled_width = int(sound_slider_width * (self.sound_volume / 100))
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'], 
                       (sound_slider_x, sound_slider_y, filled_width, sound_slider_height))
        
        # Отрисовка ползунка громкости музыки
        music_slider_x, music_slider_y, music_slider_width, music_slider_height = self._get_music_slider_rect()
        
        # Фон ползунка
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'] + (80,), 
                       (music_slider_x, music_slider_y, music_slider_width, music_slider_height))
        
        # Заполнение ползунка в зависимости от значения
        filled_width = int(music_slider_width * (self.music_volume / 100))
        pygame.draw.rect(self.screen, COLORS['PRIMARY_BLUE'], 
                       (music_slider_x, music_slider_y, filled_width, music_slider_height))
        
        # Отображение текущих значений громкости
        sound_value = self.fonts['SMALL'].render(f"{self.sound_volume}%", True, COLORS['TEXT_DARK'])
        sound_value_rect = sound_value.get_rect(
            left=sound_slider_x + sound_slider_width + 10,
            centery=sound_slider_y + sound_slider_height // 2
        )
        self.screen.blit(sound_value, sound_value_rect)
        
        music_value = self.fonts['SMALL'].render(f"{self.music_volume}%", True, COLORS['TEXT_DARK'])
        music_value_rect = music_value.get_rect(
            left=music_slider_x + music_slider_width + 10,
            centery=music_slider_y + music_slider_height // 2
        )
        self.screen.blit(music_value, music_value_rect)
    
    def _draw_language_selector(self):
        """
        Отрисовка селектора языка
        """
        # Заголовок настройки языка
        lang_label = self.fonts['MEDIUM'].render(self.localization.get_text('language'), True, COLORS['TEXT_DARK'])
        lang_label_rect = lang_label.get_rect(
            center=(self.width // 2, self.height // 2 + 60)
        )
        self.screen.blit(lang_label, lang_label_rect)

    def _draw_input_mode_selector(self):
        """
        Отрисовка селектора режима ввода (мышь / рука)
        """
        label_text = self.localization.get_text('input_mode') if self.localization else "Режим управления"
        input_label = self.fonts['MEDIUM'].render(label_text, True, COLORS['TEXT_DARK'])
        input_label_rect = input_label.get_rect(
            center=(self.width // 2, self.height // 2 + 150)
        )
        self.screen.blit(input_label, input_label_rect)
