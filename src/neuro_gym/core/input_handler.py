"""
Обработчик ввода для приложения NeuroGym
Отвечает за обработку ввода с клавиатуры, мыши или через распознавание жестов
"""

import pygame
import time
import math

from ..config import GESTURE_DELAY, DWELL_TIME, DWELL_RADIUS, DWELL_COOLDOWN

# Пользовательские события для жестов
GESTURE_CLICK = pygame.USEREVENT + 1
GESTURE_PINCH_START = pygame.USEREVENT + 2
GESTURE_PINCH_END = pygame.USEREVENT + 3
GESTURE_SWIPE_DOWN = pygame.USEREVENT + 4
GESTURE_SWIPE_UP = pygame.USEREVENT + 5
GESTURE_TRACKING_LOST = pygame.USEREVENT + 6


class InputHandler:
    def __init__(self, gesture_recognizer=None):
        """Инициализация обработчика ввода"""
        self.gesture_recognizer = gesture_recognizer
        self.input_mode = "mouse"
        self.cursor_pos = None
        self.hover_start_time = None
        self.hover_position = None
        self.last_pinch_state = False
        self.is_dragging = False
        self.drag_object = None
        self.tracking_lost_notified = False
        self.last_tracking_check = time.time()

        # ── Dwell-клик (задержка наведения) ─────────────────────────
        self._dwell_center = None       # сглаженный центр задержки (x, y)
        self._dwell_progress = 0.0      # прогресс 0.0 … 1.0
        self._dwell_triggered = False   # клик уже сработал
        self._dwell_cooldown_end = 0.0  # время конца cooldown
        self._dwell_prev_time = None    # предыдущий момент для dt
        
    def set_gesture_recognizer(self, gesture_recognizer):
        """Установка распознавателя жестов"""
        self.gesture_recognizer = gesture_recognizer
        
    def set_input_mode(self, mode):
        """Установка режима ввода: 'mouse' или 'gesture'"""
        if mode in ["mouse", "gesture"]:
            self.input_mode = mode
        else:
            print(f"Ошибка: неизвестный режим ввода {mode}")
            
    def get_events(self):
        """Получение всех событий ввода"""
        raw_events = pygame.event.get()

        if self.input_mode == "gesture" and self.gesture_recognizer:
            self.cursor_pos = self.gesture_recognizer.get_cursor_position()

            # В режиме жестов отбрасываем «настоящие» события мыши,
            # чтобы реальный курсор не конфликтовал с виртуальным.
            events = []
            for event in raw_events:
                if event.type in (pygame.MOUSEMOTION,
                                  pygame.MOUSEBUTTONDOWN,
                                  pygame.MOUSEBUTTONUP):
                    continue          # пропускаем физическую мышь
                events.append(event)

            # ── Потеря трекинга ──
            current_time = time.time()
            if current_time - self.last_tracking_check > 1.0:
                self.last_tracking_check = current_time
                if self.gesture_recognizer.is_tracking_lost():
                    if not self.tracking_lost_notified:
                        lost_event = pygame.event.Event(GESTURE_TRACKING_LOST)
                        events.append(lost_event)
                        self.tracking_lost_notified = True
                else:
                    self.tracking_lost_notified = False

            # ── Dwell-клик (задержка наведения = клик) ──
            now = time.time()
            dt = (now - self._dwell_prev_time) if self._dwell_prev_time else 0.0
            dt = min(dt, 0.1)          # защита от больших скачков
            self._dwell_prev_time = now

            if self.cursor_pos and not self.is_dragging:
                if now < self._dwell_cooldown_end:
                    # Cooldown после предыдущего клика
                    self._dwell_progress = 0.0
                elif self._dwell_center is None:
                    # Первая точка — начинаем
                    self._dwell_center = self.cursor_pos
                    self._dwell_progress = 0.0
                    self._dwell_triggered = False
                else:
                    dx = self.cursor_pos[0] - self._dwell_center[0]
                    dy = self.cursor_pos[1] - self._dwell_center[1]
                    dist = math.hypot(dx, dy)

                    if dist <= DWELL_RADIUS:
                        # Курсор рядом с центром → накапливаем прогресс
                        self._dwell_progress = min(
                            1.0, self._dwell_progress + dt / DWELL_TIME)
                    else:
                        # Курсор ушёл — перецентрируем и мягко сбрасываем
                        self._dwell_center = self.cursor_pos
                        self._dwell_progress = max(
                            0.0, self._dwell_progress - 0.15)
                        if self._dwell_progress <= 0.0:
                            self._dwell_triggered = False

                    # Dwell-клик сработал
                    if self._dwell_progress >= 1.0 and not self._dwell_triggered:
                        self._dwell_triggered = True
                        self._dwell_cooldown_end = now + DWELL_COOLDOWN
                        # Генерируем клик
                        click_event = pygame.event.Event(
                            GESTURE_CLICK, {'pos': self.cursor_pos})
                        events.append(click_event)
                        std_click = pygame.event.Event(
                            pygame.MOUSEBUTTONDOWN,
                            {'pos': self.cursor_pos, 'button': 1})
                        events.append(std_click)
                        # Сброс
                        self._dwell_center = None
                        self._dwell_progress = 0.0
            else:
                # Нет курсора или идёт перетаскивание
                self._dwell_center = None
                self._dwell_progress = 0.0
                self._dwell_prev_time = None

            # ── Щипок (для перетаскивания в упражнении Сортировка) ──
            is_pinching = self.gesture_recognizer.is_pinch_gesture()
            if is_pinching and not self.last_pinch_state:
                pinch_start = pygame.event.Event(
                    GESTURE_PINCH_START, {'pos': self.cursor_pos})
                events.append(pinch_start)
                self.is_dragging = True
            elif not is_pinching and self.last_pinch_state:
                pinch_end = pygame.event.Event(
                    GESTURE_PINCH_END, {'pos': self.cursor_pos})
                events.append(pinch_end)
                self.is_dragging = False
                self.drag_object = None
            self.last_pinch_state = is_pinching

            # ── Свайп ──
            swipe_direction = self.gesture_recognizer.get_swipe_direction()
            if swipe_direction:
                if swipe_direction == 'down':
                    events.append(pygame.event.Event(GESTURE_SWIPE_DOWN))
                elif swipe_direction == 'up':
                    events.append(pygame.event.Event(GESTURE_SWIPE_UP))

            # ── Синтетический MOUSEMOTION для hover-состояний кнопок ──
            if self.cursor_pos:
                motion = pygame.event.Event(
                    pygame.MOUSEMOTION,
                    {'pos': self.cursor_pos, 'rel': (0, 0),
                     'buttons': (0, 0, 0)})
                events.append(motion)
        else:
            events = raw_events
            self.cursor_pos = pygame.mouse.get_pos()
        
        return events, self.cursor_pos
    
    def get_cursor_position(self):
        """Получение текущей позиции курсора"""
        if self.input_mode == "gesture" and self.gesture_recognizer:
            return self.gesture_recognizer.get_cursor_position()
        else:
            return pygame.mouse.get_pos()
    
    def is_gesture_mode(self):
        """Проверка активности режима жестов"""
        return self.input_mode == "gesture"

    def get_dwell_progress(self) -> float:
        """Прогресс dwell-клика: 0.0 … 1.0  (только в gesture-режиме)."""
        return self._dwell_progress
