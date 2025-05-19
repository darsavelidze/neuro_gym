"""
Менеджер экранов для приложения NeuroGym
Отвечает за переключение между различными экранами приложения
"""

import pygame
import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')

class ScreenManager:
    def __init__(self, screen):
        """
        Инициализация менеджера экранов
        
        Args:
            screen: поверхность pygame для отрисовки
        """
        self.screen = screen
        self.screens = {}
        self.current_screen = None
        self.screen_history = []
        self.screen_params = {}
        
    def register_screen(self, screen_id, screen_class):
        """
        Регистрация нового экрана
        
        Args:
            screen_id: идентификатор экрана
            screen_class: класс экрана (должен быть наследником BaseScreen)
        """
        self.screens[screen_id] = screen_class
        
    def go_to(self, screen_id, **params):
        """
        Переход к указанному экрану
        
        Args:
            screen_id: идентификатор экрана для перехода
            **params: дополнительные параметры для передачи экрану
        """
        if screen_id in self.screens:
            self.screen_history.append(self.current_screen)
            self.screen_params[screen_id] = params
            self.current_screen = screen_id
            return self.get_current_screen()
        else:
            print(f"Ошибка: экран {screen_id} не найден")
            return None
            
    def go_back(self):
        """
        Возврат к предыдущему экрану
        
        Returns:
            объект экрана или None, если истории нет
        """
        if self.screen_history:
            previous_screen = self.screen_history.pop()
            self.current_screen = previous_screen
            return self.get_current_screen()
        return None
        
    def get_current_screen(self):
        """
        Получение текущего активного экрана
        
        Returns:
            объект текущего экрана или None, если экрана нет
        """
        if not self.current_screen or self.current_screen not in self.screens:
            return None
            
        # Создаем экземпляр класса экрана с передачей ему менеджера экранов и поверхности
        params = self.screen_params.get(self.current_screen, {})
        screen_instance = self.screens[self.current_screen](self, self.screen, **params)
        return screen_instance
