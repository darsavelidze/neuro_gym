"""
Основной класс игры для приложения NeuroGym
Объединяет компоненты приложения и реализует основной игровой цикл
"""

import math
import pygame

from ..config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS, VERSION, COLORS
from .context import AppContext
from .screen_manager import ScreenManager
from .input_handler import InputHandler
from .mouse_tracker import MouseTracker
from .hand_tracker import HandTracker
from .sound_manager import SoundManager
from .progress_manager import ProgressManager
from .achievements_manager import AchievementsManager
from .camera_controller import CameraController
from .localization_manager import LocalizationManager
from .registry import ALL_SCREENS
from .result_service import ResultService

class Game:
    def __init__(self):
        """Инициализация основного класса игры"""
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"{WINDOW_TITLE} - v{VERSION}")
        self.clock = pygame.time.Clock()
        
        # Инициализация менеджеров
        self.sound_manager = SoundManager()
        self.progress_manager = ProgressManager()
        self.localization_manager = LocalizationManager()
        
        self.mouse_tracker = MouseTracker()
        self.hand_tracker = HandTracker()
        self.input_handler = InputHandler(self.mouse_tracker)
        self.camera_controller = CameraController(self.input_handler)
        
        self.achievements_manager = AchievementsManager(self.progress_manager, self.sound_manager)
        self.result_service = ResultService(self.progress_manager, self.achievements_manager)

        self.context = AppContext(
            sound=self.sound_manager,
            progress=self.progress_manager,
            localization=self.localization_manager,
            input_handler=self.input_handler,
            camera=self.camera_controller,
            achievements=self.achievements_manager,
            mouse_tracker=self.mouse_tracker,
            results=self.result_service,
        )

        self.screen_manager = ScreenManager(self.screen, context=self.context, game=self)

        self._register_screens()
        
        self.running = False
        self.current_difficulty = self.progress_manager.get_difficulty()
        
        # Проверка камеры
        self.camera_controller.check_camera_availability()
        
    def _register_screens(self):
        """Регистрация всех экранов приложения"""
        for screen_id, screen_class in ALL_SCREENS:
            self.screen_manager.register_screen(screen_id, screen_class)
        
    def set_input_mode(self, mode: str):
        """Переключение режима управления: 'mouse' или 'gesture'."""
        if mode == 'gesture':
            ok = self.hand_tracker.start()
            if ok:
                self.input_handler.set_gesture_recognizer(self.hand_tracker)
                self.input_handler.set_input_mode('gesture')
            else:
                # Камера недоступна — остаёмся на мыши
                self.input_handler.set_input_mode('mouse')
                self.camera_controller.camera_error = (
                    "Камера недоступна. Проверьте подключение."
                )
        else:
            self.hand_tracker.stop()
            self.input_handler.set_gesture_recognizer(self.mouse_tracker)
            self.input_handler.set_input_mode('mouse')

    def set_difficulty(self, difficulty):
        """Установка уровня сложности"""
        if difficulty in ['Легкий', 'Средний', 'Сложный']:
            self.current_difficulty = difficulty
            self.progress_manager.set_difficulty(difficulty)

    def stop(self):
        """Безопасная остановка игрового цикла."""
        self.running = False

    # ── Цвета курсора жестов (вынесены из цикла для читаемости) ──
    _CURSOR_BLUE = (0, 120, 255)
    _CURSOR_WHITE = (255, 255, 255)
    _DWELL_GREEN = (0, 200, 80)
    _HINT_GRAY = (80, 80, 80)

    def _draw_gesture_overlay(self, cursor_pos, fonts):
        """Рисует индикатор руки и курсор поверх текущего экрана."""
        hand_ok = self.hand_tracker.is_hand_detected()
        pinching = self.hand_tracker.is_pinch_gesture()
        dwell = self.input_handler.get_dwell_progress()

        # Индикатор статуса руки (верхний правый угол)
        sw = self.screen.get_width()
        dot_color = COLORS['POSITIVE_GREEN'] if hand_ok else COLORS['NEGATIVE_RED']
        pygame.draw.circle(self.screen, dot_color, (sw - 26, 26), 10)

        hint_font = fonts.get('SMALL')
        if hint_font:
            hint = "[H] рука" if hand_ok else "[H] нет руки"
            hint_surf = hint_font.render(hint, True, self._HINT_GRAY)
            self.screen.blit(hint_surf, (sw - 42 - hint_surf.get_width(), 18))

        # Курсор — только если рука найдена
        if not (cursor_pos and hand_ok):
            return

        cx, cy = cursor_pos
        if pinching:
            pygame.draw.circle(self.screen, self._CURSOR_BLUE, cursor_pos, 18)
            pygame.draw.circle(self.screen, self._CURSOR_WHITE, cursor_pos, 11)
        else:
            pygame.draw.circle(self.screen, self._CURSOR_BLUE, cursor_pos, 18, 3)
            pygame.draw.circle(self.screen, self._CURSOR_WHITE, cursor_pos, 14, 2)
            pygame.draw.circle(self.screen, self._CURSOR_BLUE, cursor_pos, 4)

        # Дуга прогресса dwell-клика
        if 0.0 < dwell < 1.0 and not pinching:
            arc_radius = 24
            arc_rect = pygame.Rect(
                cx - arc_radius, cy - arc_radius,
                arc_radius * 2, arc_radius * 2)
            start_angle = math.pi / 2
            end_angle = start_angle - dwell * 2 * math.pi
            pygame.draw.arc(self.screen, self._DWELL_GREEN, arc_rect, end_angle, start_angle, 4)

    def update_exercise_result(self, exercise_id, score, xp_gain=0):
        """Обновление результатов упражнения и начисление опыта"""
        stars = self.progress_manager.update_exercise_result(exercise_id, score, xp_gain)
        new_achievements = self.achievements_manager.check_achievements()
        return stars, new_achievements
        
    def get_difficulty(self):
        """Получение текущего уровня сложности"""
        return self.current_difficulty
        
    def start(self):
        """Запуск основного игрового цикла"""
        self.running = True
        self.mouse_tracker.start()
        self.input_handler.set_input_mode("mouse")
        current_screen = self.screen_manager.go_to('loading')
        try:
            # Игровой цикл
            while self.running and current_screen:
                dt = self.clock.tick(FPS) / 1000.0
                events, cursor_pos = self.input_handler.get_events()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.stop()
                        break
                    elif event.type == pygame.USEREVENT and 'callback' in event.dict:
                        event.dict['callback']()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                        # H — переключение мышь ↔ рука
                        if self.input_handler.input_mode == 'mouse':
                            self.set_input_mode('gesture')
                        else:
                            self.set_input_mode('mouse')
                        
                # Выход из цикла
                if not self.running:
                    break
                
                # Обработка диалогового окна камеры
                if self.camera_controller.dialog and self.camera_controller.dialog['active']:
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.camera_controller.handle_dialog_click(event.pos):
                                continue
                else:
                    current_screen.handle_events(events, cursor_pos)
                
                current_screen.update(dt)
                current_screen.draw()
                
                # Диалог камеры поверх экрана
                if self.camera_controller.dialog and self.camera_controller.dialog['active']:
                    self.camera_controller.draw_dialog(
                        self.screen,
                        current_screen.fonts['MEDIUM'],
                        self.localization_manager.get_language()
                    )
                
                # Курсор и индикатор для режима жестов
                if self.input_handler.input_mode == "gesture":
                    self._draw_gesture_overlay(cursor_pos, current_screen.fonts)

                pygame.display.flip()
                
                # Переход к следующему экрану
                if current_screen.next_screen:
                    next_screen_id = current_screen.next_screen
                    params = {}
                    if hasattr(current_screen, 'transition_params'):
                        params = current_screen.transition_params
                    current_screen.next_screen = None
                    current_screen = self.screen_manager.go_to(next_screen_id, **params)
                elif not current_screen.running:
                    self.running = False
        finally:
            self.progress_manager.save_progress()
            self.hand_tracker.stop()
            self.mouse_tracker.stop()
            pygame.quit()
