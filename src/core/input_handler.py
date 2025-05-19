"""
Обработчик ввода для приложения NeuroGym
Отвечает за обработку ввода с клавиатуры, мыши или через распознавание жестов
"""

import pygame
import sys
import time
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from config import GESTURE_DELAY

# Определение пользовательских событий для жестов
GESTURE_CLICK = pygame.USEREVENT + 1
GESTURE_PINCH_START = pygame.USEREVENT + 2
GESTURE_PINCH_END = pygame.USEREVENT + 3
GESTURE_SWIPE_DOWN = pygame.USEREVENT + 4
GESTURE_SWIPE_UP = pygame.USEREVENT + 5
GESTURE_TRACKING_LOST = pygame.USEREVENT + 6

class InputHandler:
    def __init__(self, gesture_recognizer=None):
        """
        Инициализация обработчика ввода
        
        Args:
            gesture_recognizer: объект для распознавания жестов (опционально)
        """
        self.gesture_recognizer = gesture_recognizer
        self.input_mode = "mouse"  # "mouse" или "gesture"
        self.cursor_pos = None
        self.hover_start_time = None
        self.hover_position = None
        
        # Состояния жестов
        self.last_pinch_state = False
        self.is_dragging = False
        self.drag_object = None
        self.tracking_lost_notified = False
        self.last_tracking_check = time.time()
        
    def set_gesture_recognizer(self, gesture_recognizer):
        """
        Установка распознавателя жестов
        
        Args:
            gesture_recognizer: объект для распознавания жестов
        """
        self.gesture_recognizer = gesture_recognizer
        
    def set_input_mode(self, mode):
        """
        Установка режима ввода
        
        Args:
            mode: "mouse" или "gesture"
        """
        if mode in ["mouse", "gesture"]:
            self.input_mode = mode
        else:
            print(f"Ошибка: неизвестный режим ввода {mode}")
            
    def get_events(self):
        """
        Получение всех событий ввода
        
        Returns:
            tuple: (events, cursor_pos) где events - список событий pygame,
                  а cursor_pos - координаты курсора или None
        """
        # Получение стандартных событий pygame
        events = pygame.event.get()
        
        # Если используем режим жестов и распознаватель инициализирован
        if self.input_mode == "gesture" and self.gesture_recognizer:
            # Получаем позицию курсора от распознавателя жестов
            self.cursor_pos = self.gesture_recognizer.get_cursor_position()
            
            # Проверка потери отслеживания руки
            current_time = time.time()
            if current_time - self.last_tracking_check > 1.0:  # Проверяем раз в секунду
                self.last_tracking_check = current_time
                if self.gesture_recognizer.is_tracking_lost():
                    if not self.tracking_lost_notified:
                        # Создаем событие о потере отслеживания руки
                        lost_event = pygame.event.Event(GESTURE_TRACKING_LOST)
                        events.append(lost_event)
                        self.tracking_lost_notified = True
                else:
                    self.tracking_lost_notified = False
            
            # Обработка жеста "клик" (задержка пальца)
            if self.gesture_recognizer.is_click_gesture():
                if self.cursor_pos:
                    # Создаем пользовательское событие клика
                    click_event = pygame.event.Event(GESTURE_CLICK, {'pos': self.cursor_pos})
                    events.append(click_event)
                    # И стандартное событие клика мыши для совместимости
                    std_click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                                       {'pos': self.cursor_pos, 'button': 1})
                    events.append(std_click_event)
            
            # Обработка жеста "захват" (pinch)
            current_pinch_state = self.gesture_recognizer.is_pinch_gesture()
            
            # Обнаружено начало захвата
            if current_pinch_state and not self.last_pinch_state:
                if self.cursor_pos:
                    # Создаем событие начала захвата
                    pinch_event = pygame.event.Event(GESTURE_PINCH_START, {'pos': self.cursor_pos})
                    events.append(pinch_event)
                    # И стандартное событие нажатия для совместимости
                    std_down_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                                      {'pos': self.cursor_pos, 'button': 1})
                    events.append(std_down_event)
                    
                    self.is_dragging = True
            
            # Обнаружено окончание захвата
            elif not current_pinch_state and self.last_pinch_state:
                if self.cursor_pos:
                    # Создаем событие окончания захвата
                    release_event = pygame.event.Event(GESTURE_PINCH_END, {'pos': self.cursor_pos})
                    events.append(release_event)
                    # И стандартное событие отпускания для совместимости
                    std_up_event = pygame.event.Event(pygame.MOUSEBUTTONUP, 
                                                    {'pos': self.cursor_pos, 'button': 1})
                    events.append(std_up_event)
                    
                    self.is_dragging = False
            
            # Обновляем состояние захвата
            self.last_pinch_state = current_pinch_state
            
            # Обработка перетаскивания (если захват активен)
            if self.is_dragging and self.cursor_pos:
                drag_event = pygame.event.Event(pygame.MOUSEMOTION, 
                                              {'pos': self.cursor_pos, 'buttons': (1, 0, 0)})
                events.append(drag_event)
            
            # Обработка жеста "свайп вниз" (для навигации назад)
            if self.gesture_recognizer.is_swipe_down_gesture():
                swipe_event = pygame.event.Event(GESTURE_SWIPE_DOWN)
                events.append(swipe_event)
                
                # Также эмулируем нажатие клавиши Escape для совместимости
                key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
                events.append(key_event)
            
            # Обработка жеста "свайп вверх"
            if self.gesture_recognizer.is_swipe_up_gesture():
                swipe_event = pygame.event.Event(GESTURE_SWIPE_UP)
                events.append(swipe_event)
                
        else:
            # В режиме мыши просто берем позицию курсора
            self.cursor_pos = pygame.mouse.get_pos()
            
        return events, self.cursor_pos
            
    def _check_gesture_click(self):
        """
        Проверка распознавания жеста "клик" (задержка пальца)
        
        Returns:
            bool: True, если жест клика распознан
        """
        current_time = pygame.time.get_ticks()
        
        # Если палец не двигается и находится в одной позиции достаточно долго
        if self.cursor_pos:
            # Новое наведение или перемещение курсора
            if (not self.hover_position or 
                self._distance(self.hover_position, self.cursor_pos) > 10):
                self.hover_position = self.cursor_pos
                self.hover_start_time = current_time
                return False
                
            # Если курсор был в одном месте достаточно долго
            if current_time - self.hover_start_time > GESTURE_DELAY:
                self.hover_start_time = current_time
                return True
                
        return False
        
    def _distance(self, pos1, pos2):
        """
        Расчет расстояния между двумя точками
        
        Args:
            pos1: первая позиция (x1, y1)
            pos2: вторая позиция (x2, y2)
            
        Returns:
            float: расстояние между точками
        """
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    def get_cursor_position(self):
        """
        Получение текущей позиции курсора (мыши или указательного пальца)
        
        Returns:
            tuple: (x, y) координаты курсора или None, если курсор не определен
        """
        if self.input_mode == "mouse":
            # Для режима мыши используем текущее положение курсора pygame
            return pygame.mouse.get_pos()
        elif self.input_mode == "gesture" and self.gesture_recognizer:
            # Для режима жестов используем положение указательного пальца
            # Получаем позицию прямо из распознавателя жестов
            if self.gesture_recognizer.cursor_position:
                return self.gesture_recognizer.cursor_position
                
        # Если не удалось определить положение, возвращаем последнее известное или None
        return self.cursor_pos
        
    def check_auto_switch_input_mode(self):
        """
        Автоматически переключает режим ввода в зависимости от доступности и работоспособности камеры
        
        Returns:
            str: новый режим ввода или None, если нет изменений
        """
        # Если текущий режим - жесты, но отслеживание потеряно на длительное время
        if self.input_mode == "gesture" and self.gesture_recognizer:
            if self.gesture_recognizer.is_tracking_lost():
                # Переключаемся на управление мышью
                self.set_input_mode("mouse")
                return "mouse"
                
        # Если текущий режим - мышь, но камера доступна и распознаватель инициализирован
        elif self.input_mode == "mouse" and self.gesture_recognizer:
            # Если камера доступна и рука обнаружена
            if not self.gesture_recognizer.is_tracking_lost():
                # Переключаемся на управление жестами
                self.set_input_mode("gesture")
                return "gesture"
                
        # Режим остался прежним
        return None
    
    def is_dragging(self):
        """
        Проверяет, находится ли интерфейс в состоянии перетаскивания
        
        Returns:
            bool: True, если активно перетаскивание
        """
        if self.input_mode == "mouse":
            return pygame.mouse.get_pressed()[0]  # Левая кнопка мыши нажата
        else:
            return self.is_dragging
