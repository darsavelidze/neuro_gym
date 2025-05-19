"""
Система контроля камеры для приложения NeuroGym
Отвечает за проверку доступности камеры и переключение режима управления
"""

import cv2
import pygame
import threading
import time
import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')

class CameraController:
    def __init__(self, input_handler):
        """
        Инициализация контроллера камеры
        
        Args:
            input_handler: обработчик ввода
        """
        self.input_handler = input_handler
        self.camera = None
        self.camera_available = False
        self.camera_error = None
        self.checking = False
        
        # Диалоговое окно для сообщений
        self.dialog = None
        
    def check_camera_availability(self, callback=None):
        """
        Проверка доступности камеры
        
        Args:
            callback: функция обратного вызова после завершения проверки
        """
        if self.checking:
            return
            
        self.checking = True
        
        # Запускаем проверку в отдельном потоке, чтобы не блокировать основной поток
        threading.Thread(target=self._camera_check_thread, args=(callback,), daemon=True).start()
        
    def _camera_check_thread(self, callback):
        """
        Поток для проверки доступности камеры
        
        Args:
            callback: функция обратного вызова после завершения проверки
        """
        error_message = None
        
        try:
            # Пытаемся открыть камеру
            camera = cv2.VideoCapture(0)
            
            # Проверка, открылась ли камера
            if not camera.isOpened():
                self.camera_available = False
                error_message = "Камера недоступна. Проверьте подключение камеры или разрешения доступа."
            else:
                # Проверяем, можем ли мы получить кадр
                ret, frame = camera.read()
                if not ret:
                    self.camera_available = False
                    error_message = "Не удалось получить изображение с камеры. Проверьте, не используется ли камера другим приложением."
                else:
                    self.camera_available = True
                
                # Закрываем камеру
                camera.release()
        except Exception as e:
            self.camera_available = False
            error_message = f"Ошибка при работе с камерой: {str(e)}"
        
        self.camera_error = error_message
        self.checking = False
        
        # Если камера недоступна, переключаемся на управление мышью
        if not self.camera_available:
            self.input_handler.set_input_mode('mouse')
            
        # Вызываем функцию обратного вызова в основном потоке
        if callback:
            # Используем pygame для выполнения функции в основном потоке
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'callback': callback}))
    
    def show_camera_error_dialog(self, screen):
        """
        Отображение диалогового окна с ошибкой камеры
        
        Args:
            screen: поверхность pygame для отрисовки
        """
        if not self.camera_error:
            return
            
        # Создаём диалоговое окно с сообщением об ошибке
        self.dialog = {
            'active': True,
            'message': self.camera_error,
            'message_en': self.camera_error.replace("Камера недоступна", "Camera not available")
                                         .replace("Проверьте подключение камеры или разрешения доступа", 
                                                 "Check camera connection or access permissions")
                                         .replace("Не удалось получить изображение с камеры", 
                                                 "Failed to get image from camera")
                                         .replace("Проверьте, не используется ли камера другим приложением", 
                                                 "Check if the camera is used by another application")
                                         .replace("Ошибка при работе с камерой", 
                                                 "Camera error"),
            'buttons': [
                {
                    'text': 'OK',
                    'text_en': 'OK',
                    'action': self.close_dialog
                }
            ],
            'screen': screen
        }
    
    def close_dialog(self):
        """
        Закрытие диалогового окна
        """
        if self.dialog:
            self.dialog['active'] = False
            self.dialog = None
    
    def draw_dialog(self, screen, font, language='ru'):
        """
        Отрисовка диалогового окна
        
        Args:
            screen: поверхность pygame для отрисовки
            font: шрифт для текста
            language: язык интерфейса ('ru' или 'en')
        """
        if not self.dialog or not self.dialog['active']:
            return
            
        # Параметры диалогового окна
        screen_width, screen_height = screen.get_size()
        dialog_width = int(screen_width * 0.6)
        dialog_height = int(screen_height * 0.3)
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        
        # Рисуем затемнение фона
        dark_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 150))  # полупрозрачный черный
        screen.blit(dark_overlay, (0, 0))
        
        # Рисуем фон диалогового окна
        pygame.draw.rect(screen, (50, 50, 70), 
                      (dialog_x, dialog_y, dialog_width, dialog_height), 
                      border_radius=15)
        pygame.draw.rect(screen, (80, 80, 100), 
                      (dialog_x, dialog_y, dialog_width, dialog_height), 
                      width=2, border_radius=15)
        
        # Отображаем сообщение
        message = self.dialog['message'] if language == 'ru' else self.dialog['message_en']
        
        # Разбиваем сообщение на строки
        max_width = dialog_width - 40
        words = message.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
                
        lines.append(current_line)
        
        # Отображаем строки текста
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(dialog_x + dialog_width // 2, 
                                                    dialog_y + 80 + i * line_height))
            screen.blit(text_surface, text_rect)
        
        # Отображаем заголовок
        header = "Уведомление" if language == 'ru' else "Notification"
        header_surface = font.render(header, True, (255, 255, 255))
        header_rect = header_surface.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 30))
        screen.blit(header_surface, header_rect)
        
        # Отображаем кнопки
        button_width = 120
        button_height = 40
        button_y = dialog_y + dialog_height - 60
        
        # Центрируем кнопки по горизонтали
        buttons_total_width = len(self.dialog['buttons']) * button_width + (len(self.dialog['buttons']) - 1) * 20
        button_x_start = dialog_x + (dialog_width - buttons_total_width) // 2
        
        for i, button in enumerate(self.dialog['buttons']):
            button_x = button_x_start + i * (button_width + 20)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Рисуем кнопку
            pygame.draw.rect(screen, (80, 100, 120), button_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 140, 160), button_rect, width=2, border_radius=8)
            
            # Текст на кнопке
            button_text = button['text'] if language == 'ru' else button['text_en']
            button_text_surface = font.render(button_text, True, (255, 255, 255))
            button_text_rect = button_text_surface.get_rect(center=button_rect.center)
            screen.blit(button_text_surface, button_text_rect)
            
            # Сохраняем прямоугольник кнопки для обработки кликов
            button['rect'] = button_rect
    
    def handle_dialog_click(self, pos):
        """
        Обработка клика по диалоговому окну
        
        Args:
            pos: позиция клика (x, y)
            
        Returns:
            bool: True, если клик был обработан, иначе False
        """
        if not self.dialog or not self.dialog['active']:
            return False
            
        for button in self.dialog['buttons']:
            if 'rect' in button and button['rect'].collidepoint(pos):
                if 'action' in button:
                    button['action']()
                return True
                
        return True  # Возвращаем True для всех кликов по диалоговому окну
