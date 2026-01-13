"""
Трекер руки на основе MediaPipe для приложения NeuroGym.

Использует новый Tasks API (mediapipe >= 0.10.18):
  mp.tasks.vision.HandLandmarker  вместо  mp.solutions.hands.Hands

Отслеживает кончик указательного пальца через веб-камеру
и преобразует его в экранные координаты.  Распознаёт жесты:
  • короткий щипок (thumb + index)  → клик
  • удержание щипка                 → перетаскивание
  • быстрое вертикальное движение   → свайп вверх / вниз

Курсор сглаживается адаптивным 1 € фильтром (One Euro Filter).
"""

import os
import cv2
import mediapipe as mp
import threading
import time
import math

from ..config import (
    ASSETS_DIR,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    SWIPE_SPEED_THRESHOLD, SWIPE_MIN_DISTANCE,
    LOST_TRACKING_TIMEOUT,
)

# ── Индексы ключевых точек MediaPipe Hand Landmarks ────────────────
_THUMB_TIP = 4
_INDEX_TIP = 8
_INDEX_MCP = 5
_WRIST = 0

# ── Путь к файлу модели ────────────────────────────────────────────
_MODEL_PATH = os.path.join(ASSETS_DIR, "models", "hand_landmarker.task")

# ── Пороги щипка с гистерезисом ────────────────────────────────────
_PINCH_ON = 0.40   # начало щипка (пальцы сведены)
_PINCH_OFF = 0.55  # конец щипка  (пальцы разведены)


# ====================================================================
# 1 € Filter — адаптивный низкочастотный фильтр
# ====================================================================
class _OneEuroFilter:
    """Убирает дрожание в покое, не добавляет задержки при быстром движении."""

    def __init__(
        self,
        freq: float = 30.0,
        min_cutoff: float = 1.8,
        beta: float = 0.008,
        d_cutoff: float = 1.0,
    ):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self._x_prev = None
        self._dx_prev = 0.0

    def _alpha(self, cutoff: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau * self.freq)

    def reset(self):
        self._x_prev = None
        self._dx_prev = 0.0

    def __call__(self, x: float, rate: float = 0.0) -> float:
        if rate > 0:
            self.freq = rate
        if self._x_prev is None:
            self._x_prev = x
            return x
        a_d = self._alpha(self.d_cutoff)
        dx = (x - self._x_prev) * self.freq
        dx_hat = a_d * dx + (1 - a_d) * self._dx_prev
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._alpha(cutoff)
        x_hat = a * x + (1 - a) * self._x_prev
        self._x_prev = x_hat
        self._dx_prev = dx_hat
        return x_hat


# ====================================================================
# HandTracker
# ====================================================================
class HandTracker:
    """Отслеживание указательного пальца и распознавание жестов."""

    def __init__(
        self,
        camera_index: int = 0,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.6,
    ):
        self.camera_index = camera_index
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        # Камера / поток
        self._cap = None
        self._landmarker = None
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

        # ── Публичные данные (читать под _lock) ─────────────────────
        self._cursor_pos = None
        self._pinch_active = False
        self._swipe_direction = None
        self._hand_detected = False

        # ── Внутреннее состояние ────────────────────────────────────
        self._last_detection_time = 0.0
        self._pinch_distance = 1.0
        self._was_pinching = False
        self._position_history = []

        # Фильтры
        self._filter_x = _OneEuroFilter()
        self._filter_y = _OneEuroFilter()

        # FPS
        self._fps = 0.0
        self._frame_count = 0
        self._fps_timer = 0.0
        self._current_frame = None

        # Размеры кадра камеры (нужны для нормализации щипка)
        self._frame_w = 640
        self._frame_h = 480

    # ================================================================
    # Публичный интерфейс
    # ================================================================

    def start(self) -> bool:
        """Запуск трекера.  Возвращает True при успехе."""
        if self._running:
            return True

        # Проверяем наличие модели
        if not os.path.isfile(_MODEL_PATH):
            print(f"Ошибка: файл модели не найден: {_MODEL_PATH}")
            return False

        # Открываем камеру
        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            return False
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Создаём HandLandmarker (VIDEO-режим — синхронный покадровый)
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=self.detection_confidence,
            min_hand_presence_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence,
        )
        self._landmarker = HandLandmarker.create_from_options(options)

        self._running = True
        self._last_detection_time = time.time()
        self._fps_timer = time.time()
        self._frame_count = 0
        self._filter_x.reset()
        self._filter_y.reset()

        self._thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        """Остановка трекера и освобождение ресурсов."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._landmarker:
            self._landmarker.close()
            self._landmarker = None
        if self._cap:
            self._cap.release()
            self._cap = None

    # ── Позиция курсора ─────────────────────────────────────────────

    def get_cursor_position(self):
        with self._lock:
            return self._cursor_pos

    # ── Жесты ───────────────────────────────────────────────────────

    def is_pinch_gesture(self) -> bool:
        with self._lock:
            return self._pinch_active

    def get_swipe_direction(self):
        with self._lock:
            d = self._swipe_direction
            self._swipe_direction = None
            return d

    # ── Статус ──────────────────────────────────────────────────────

    def is_tracking_lost(self) -> bool:
        with self._lock:
            return (time.time() - self._last_detection_time) > LOST_TRACKING_TIMEOUT

    def is_hand_detected(self) -> bool:
        with self._lock:
            return self._hand_detected

    def get_fps(self) -> float:
        return self._fps

    def get_current_frame(self):
        with self._lock:
            return self._current_frame

    # ================================================================
    # Основной цикл (daemon-поток)
    # ================================================================

    def _tracking_loop(self):
        # Монотонный счётчик миллисекунд для detect_for_video
        ts_ms = 0

        while self._running:
            if not self._cap or not self._cap.isOpened():
                time.sleep(0.05)
                continue

            ret, frame = self._cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            self._frame_h, self._frame_w = frame.shape[:2]

            # Зеркалим кадр
            frame = cv2.flip(frame, 1)

            # Конвертируем в mediapipe.Image (RGB)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            # Инкрементируем таймстемп (должен строго расти)
            ts_ms += 33  # ≈30 fps

            try:
                result = self._landmarker.detect_for_video(mp_image, ts_ms)
            except Exception:
                time.sleep(0.01)
                continue

            now = time.time()

            # FPS
            self._frame_count += 1
            if now - self._fps_timer >= 1.0:
                self._fps = self._frame_count / (now - self._fps_timer)
                self._frame_count = 0
                self._fps_timer = now

            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]  # список NormalizedLandmark
                self._process_hand(landmarks, now)
                with self._lock:
                    self._hand_detected = True
            else:
                with self._lock:
                    self._hand_detected = False
                    self._pinch_active = False
                    self._was_pinching = False

            with self._lock:
                self._current_frame = frame

            time.sleep(0.003)

    # ================================================================
    # Обработка данных руки
    # ================================================================

    def _process_hand(self, landmarks, now: float):
        """landmarks — список NormalizedLandmark (21 штука)."""
        w = self._frame_w
        h = self._frame_h

        index_tip = landmarks[_INDEX_TIP]
        thumb_tip = landmarks[_THUMB_TIP]
        wrist = landmarks[_WRIST]
        index_mcp = landmarks[_INDEX_MCP]

        # ── Нормализация позиции указательного пальца ───────────────
        margin_x, margin_y = 0.15, 0.12
        nx = (index_tip.x - margin_x) / (1.0 - 2 * margin_x)
        ny = (index_tip.y - margin_y) / (1.0 - 2 * margin_y)
        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        raw_x = nx * WINDOW_WIDTH
        raw_y = ny * WINDOW_HEIGHT

        # ── 1 € фильтр ─────────────────────────────────────────────
        rate = self._fps if self._fps > 0 else 30.0
        sx = self._filter_x(raw_x, rate)
        sy = self._filter_y(raw_y, rate)

        with self._lock:
            self._cursor_pos = (int(sx), int(sy))
            self._last_detection_time = now

        # ── Расстояние щипка (thumb ↔ index), нормированное к ладони
        dx = (thumb_tip.x - index_tip.x) * w
        dy = (thumb_tip.y - index_tip.y) * h
        pinch_dist = math.hypot(dx, dy)

        palm_dx = (wrist.x - index_mcp.x) * w
        palm_dy = (wrist.y - index_mcp.y) * h
        palm_size = max(math.hypot(palm_dx, palm_dy), 1.0)

        norm_pinch = pinch_dist / palm_size

        # ── Щипок с гистерезисом ────────────────────────────────────
        if self._was_pinching:
            is_pinching_now = norm_pinch < _PINCH_OFF
        else:
            is_pinching_now = norm_pinch < _PINCH_ON

        with self._lock:
            self._pinch_distance = norm_pinch
            self._pinch_active = is_pinching_now
            self._was_pinching = is_pinching_now

        # ── Свайп ───────────────────────────────────────────────────
        self._update_swipe(nx, ny, now)

    # ── Определение свайпов ─────────────────────────────────────────

    def _update_swipe(self, nx: float, ny: float, now: float):
        self._position_history.append((nx, ny, now))

        cutoff = now - 0.3
        self._position_history = [
            p for p in self._position_history if p[2] >= cutoff
        ]

        if len(self._position_history) < 4:
            return

        oldest = self._position_history[0]
        newest = self._position_history[-1]
        dt = newest[2] - oldest[2]
        if dt < 0.05:
            return

        dy = (newest[1] - oldest[1]) * WINDOW_HEIGHT
        speed = abs(dy) / dt

        if speed > SWIPE_SPEED_THRESHOLD and abs(dy) > SWIPE_MIN_DISTANCE * 0.3:
            with self._lock:
                self._swipe_direction = 'down' if dy > 0 else 'up'
            self._position_history.clear()
