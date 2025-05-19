"""
Основной класс игры для приложения NeuroGym
Объединяет компоненты приложения и реализует основной игровой цикл
"""

import pygame
import sys
import os
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS, VERSION
from core.screen_manager import ScreenManager
from core.input_handler import InputHandler
from core.mouse_tracker import MouseTracker
from core.sound_manager import SoundManager
from core.progress_manager import ProgressManager
from core.achievements_manager import AchievementsManager
from core.camera_controller import CameraController
from core.localization_manager import LocalizationManager
from ui.loading_screen import LoadingScreen
from ui.main_menu import MainMenu
from ui.exercise_selection import ExerciseSelection
from ui.instructions_screen import InstructionsScreen
from ui.settings_screen import SettingsScreen
from ui.results_screen import ResultsScreen
from ui.achievements_screen import AchievementsScreen
from exercises.pathfinder import Pathfinder
from exercises.trajectory import Trajectory
from exercises.sorting import Sorting
from exercises.sequence import Sequence
from exercises.fast_fingers import FastFingers

class Game:
    def __init__(self):
        """
        Инициализация основного класса игры
        """
        # Инициализация pygame
        pygame.init()
        pygame.mixer.init()  # Инициализация звукового микшера
        
        # Создание окна
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"{WINDOW_TITLE} - v{VERSION}")
        
        # Инициализация часов для контроля FPS
        self.clock = pygame.time.Clock()
        
        # Инициализация основных менеджеров
        self.sound_manager = SoundManager()
        self.progress_manager = ProgressManager()
        self.localization_manager = LocalizationManager()
        
        # Инициализация компонентов ввода
        self.mouse_tracker = MouseTracker()
        self.input_handler = InputHandler(self.mouse_tracker)
        self.camera_controller = CameraController(self.input_handler)
        
        # Инициализация менеджера экранов и передача ссылки на игру
        self.screen_manager = ScreenManager(self.screen)
        self.screen_manager.game = self  # Для доступа менеджера экранов к другим компонентам
        
        # Инициализация менеджера достижений (требует прогресс и звуки)
        self.achievements_manager = AchievementsManager(self.progress_manager, self.sound_manager)
        
        # Регистрация экранов
        self._register_screens()
        
        # Инициализация состояния игры
        self.running = False
        self.current_difficulty = self.progress_manager.get_difficulty()  # Получаем сложность из сохранения
        
        # Проверка доступности камеры
        self.camera_controller.check_camera_availability()
        
    def _register_screens(self):
        """
        Регистрация всех экранов приложения
        """
        self.screen_manager.register_screen('loading', LoadingScreen)
        self.screen_manager.register_screen('main_menu', MainMenu)
        self.screen_manager.register_screen('exercise_selection', ExerciseSelection)
        self.screen_manager.register_screen('instructions', InstructionsScreen)
        self.screen_manager.register_screen('settings', SettingsScreen)
        self.screen_manager.register_screen('results', ResultsScreen)
        self.screen_manager.register_screen('achievements', AchievementsScreen)
        
        # Регистрация упражнений
        self.screen_manager.register_screen('pathfinder', Pathfinder)
        self.screen_manager.register_screen('trajectory', Trajectory)
        self.screen_manager.register_screen('sorting', Sorting)
        self.screen_manager.register_screen('sequence', Sequence)
        self.screen_manager.register_screen('fast_fingers', FastFingers)
        
    def set_difficulty(self, difficulty):
        """
        Установка уровня сложности
        
        Args:
            difficulty: выбранный уровень сложности ('Легкий', 'Средний', 'Сложный')
        """
        if difficulty in ['Легкий', 'Средний', 'Сложный']:
            self.current_difficulty = difficulty
            self.progress_manager.set_difficulty(difficulty)
            
    def update_exercise_result(self, exercise_id, score):
        """
        Обновление результатов упражнения
        
        Args:
            exercise_id: идентификатор упражнения
            score: набранные очки
            
        Returns:
            int: количество заработанных звезд (от 1 до 3)
        """
        stars = self.progress_manager.update_exercise_result(exercise_id, score)
        
        # Проверяем, не получены ли новые достижения
        new_achievements = self.achievements_manager.check_achievements()
        
        return stars, new_achievements
        
    def _save_progress(self):
        """
        Сохранение прогресса пользователя
        """
        # Упрощенная версия сохранения прогресса
        # В реальном приложении здесь должна быть запись в файл
        pass
        
    def set_difficulty(self, difficulty):
        """
        Установка уровня сложности
        
        Args:
            difficulty: выбранный уровень сложности
        """
        self.current_difficulty = difficulty
        
    def get_difficulty(self):
        """
        Получение текущего уровня сложности
        
        Returns:
            str: текущий уровень сложности
        """
        return self.current_difficulty
        
    def start(self):
        """
        Запуск основного игрового цикла
        """
        self.running = True
        
        # Запускаем отслеживание мыши
        self.mouse_tracker.start()
        self.input_handler.set_input_mode("mouse")
        
        # Переход на экран загрузки
        current_screen = self.screen_manager.go_to('loading')
        
        # Основной игровой цикл
        while self.running and current_screen:
            # Расчет времени, прошедшего с предыдущего кадра
            dt = self.clock.tick(FPS) / 1000.0
            
            # Получение всех событий pygame
            events = pygame.event.get()
            
            # Проверка на выход из приложения и специальные события
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                
                # Обработка пользовательских событий (например, от camera_controller)
                elif event.type == pygame.USEREVENT and 'callback' in event.dict:
                    event.dict['callback']()
                    
                # Обработка нажатия клавиш для глобальных действий
                elif event.type == pygame.KEYDOWN:
                    # Выход из приложения по Escape
                    if event.key == pygame.K_ESCAPE:
                        # Тут можно добавить диалоговое окно подтверждения выхода
                        pass
                        
            # Если пользователь закрыл окно, выходим из цикла
            if not self.running:
                break
            
            # Получение позиции курсора
            cursor_pos = self.input_handler.get_cursor_position()
            
            # Если активно диалоговое окно камеры, обрабатываем его
            if self.camera_controller.dialog and self.camera_controller.dialog['active']:
                # Обработка кликов по диалоговому окну
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.camera_controller.handle_dialog_click(event.pos):
                            # Если клик был обработан диалоговым окном, не передаем его экрану
                            continue
            else:
                # Обработка событий текущим экраном
                current_screen.handle_events(events, cursor_pos)
            
            # Обновление состояния текущего экрана
            current_screen.update(dt)
            
            # Отрисовка текущего экрана
            current_screen.draw()
            
            # Отрисовка диалогового окна камеры поверх экрана, если оно активно
            if self.camera_controller.dialog and self.camera_controller.dialog['active']:
                self.camera_controller.draw_dialog(
                    self.screen,
                    current_screen.fonts['MEDIUM'],
                    self.localization_manager.get_language()
                )
            
            # Отрисовка курсора при управлении жестами
            if self.input_handler.input_mode == "gesture" and cursor_pos:
                # Создаем и отрисовываем указатель для режима жестов
                cursor_size = 20
                cursor_color = (0, 120, 255)  # Синий цвет курсора
                
                # Рисуем круглый указатель
                pygame.draw.circle(self.screen, cursor_color, cursor_pos, cursor_size)
                pygame.draw.circle(self.screen, (255, 255, 255), cursor_pos, cursor_size - 4)
                pygame.draw.circle(self.screen, cursor_color, cursor_pos, cursor_size - 8)
            
            # Вывод кадра на экран
            pygame.display.flip()
            
            # Проверка перехода к следующему экрану
            if current_screen.next_screen:
                # Получаем имя следующего экрана
                next_screen_id = current_screen.next_screen
                
                # Проверяем, есть ли параметры для передачи следующему экрану
                params = {}
                if hasattr(current_screen, 'transition_params'):
                    params = current_screen.transition_params
                
                # Сбрасываем переменную next_screen, чтобы избежать циклического перехода
                current_screen.next_screen = None
                
                # Если указан конкретный экран, переходим к нему с параметрами
                current_screen = self.screen_manager.go_to(next_screen_id, **params)
                
                # Для отладки - можно раскомментировать при необходимости
                # print(f"Переход к экрану: {next_screen_id} с параметрами: {params}")
                
            elif not current_screen.running:
                # Если текущий экран больше не активен, выходим
                self.running = False
        
        # Сохраняем прогресс перед выходом
        self.progress_manager.save_progress()
        
        # Очистка ресурсов перед выходом
        self.mouse_tracker.stop()
        
        # Завершение работы pygame
        pygame.quit()
        sys.exit()
        
    def exit(self):
        """
        Выход из игры с сохранением прогресса
        """
        self._save_progress()
        self.running = False
