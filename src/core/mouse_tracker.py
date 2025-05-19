"""
Простой трекер мыши для приложения NeuroGym
Отслеживает позицию курсора мыши для управления интерфейсом
"""

import pygame
import threading
import time

class MouseTracker:
    """
    Класс для отслеживания позиции курсора мыши
    """
    def __init__(self):
        """
        Инициализация трекера мыши
        """
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.cursor_position = None
        
        # Метрики производительности (только для совместимости)
        self.fps = 0
        self.frame_count = 0
        self.fps_timer = time.time()
        
    def start(self):
        """
        Запуск трекера мыши в отдельном потоке
        
        Returns:
            bool: True, так как запуск всегда успешен
        """
        # Запуск отслеживания в отдельном потоке
        self.running = True
        self.thread = threading.Thread(target=self._track_mouse)
        self.thread.daemon = True
        self.thread.start()
        
        return True
        
    def stop(self):
        """
        Остановка трекера мыши
        """
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
            
    def get_cursor_position(self):
        """
        Получение текущей позиции курсора мыши
        
        Returns:
            tuple: (x, y) координаты курсора
        """
        with self.lock:
            return self.cursor_position
    
    def is_tracking_lost(self):
        """
        Проверяет, не потеряно ли отслеживание мыши
        В случае с мышью всегда возвращает False, так как мышь не может быть "потеряна"
        
        Returns:
            bool: Всегда False для мыши
        """
        return False
    
    def get_current_frame(self):
        """
        Заглушка для совместимости с предыдущим API
        
        Returns:
            None: Всегда возвращает None, так как нет кадра с камеры
        """
        return None
    
    def _track_mouse(self):
        """
        Метод для отслеживания позиции мыши
        Запускается в отдельном потоке
        """
        while self.running:
            # Получение текущей позиции мыши
            pos = pygame.mouse.get_pos()
            
            # Обновление счетчика FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.fps_timer > 1.0:
                self.fps = self.frame_count / (current_time - self.fps_timer)
                self.frame_count = 0
                self.fps_timer = current_time
            
            # Обновление позиции с блокировкой для потокобезопасности
            with self.lock:
                self.cursor_position = pos
                
            # Небольшая задержка для экономии ресурсов
            time.sleep(0.016)  # ~60 обновлений в секунду
