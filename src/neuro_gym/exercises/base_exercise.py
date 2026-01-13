"""
Базовый класс упражнения для приложения NeuroGym
Все упражнения должны наследоваться от этого класса
"""

import pygame
import time
from typing import Iterable

from ..ui.base_screen import BaseScreen
from ..ui.components.pause_menu import PauseMenu, PauseOption
from ..ui.components.exercise_hud import ExerciseHUD
from ..ui.components.result_banner import ResultBanner
from ..config import COLORS, EXERCISE_DURATION
from ..core.result_service import ExerciseResult

class BaseExercise(BaseScreen):
    exercise_id = None
    def __init__(self, screen_manager, screen, difficulty='Легкий', exercise_id=None):
        """
        Инициализация базового класса упражнения
        
        Args:
            screen_manager: менеджер экранов
            screen: поверхность pygame для отрисовки
            difficulty: уровень сложности упражнения
        """
        super().__init__(screen_manager, screen)
        
        self.localization = getattr(self.context, 'localization', None)
        self.result_banner = ResultBanner(self.fonts)
        self.cursor_pos = None

        # Контекстные менеджеры/сервисы
        self.progress_manager = getattr(self.context, 'progress', None)
        self.achievements_manager = getattr(self.context, 'achievements', None)
        self.result_service = getattr(self.context, 'results', None)

        # Уровень сложности упражнения
        self.difficulty = difficulty
        
        # Счет и прогресс
        self.score = 0
        self.accuracy = 100.0  # процент точности выполнения
        
        # Таймер упражнения
        self.start_time = time.time()
        self.elapsed_time = 0
        self.default_duration = EXERCISE_DURATION
        self.duration = self.default_duration  # длительность упражнения в секундах
        
        # Состояние упражнения
        self.is_paused = False
        self.is_completed = False

        # Идентификатор упражнения для реестра и прогресса
        self.exercise_id = exercise_id or getattr(self, 'exercise_id', None)
        if not self.exercise_id:
            self.exercise_id = self.__class__.__name__.lower()
        
        # Создание элементов интерфейса
        self.hud = ExerciseHUD(self)
        self.pause_menu = PauseMenu(self)
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """
        Создание элементов интерфейса упражнения
        """
        # Очистка кнопок и создание общей кнопки паузы через HUD
        self.buttons = []
        self.hud.ensure_pause_button(self._toggle_pause)

    def _reset_runtime_state(self):
        """Сбрасывает динамическое состояние упражнения для повторного входа."""
        self.score = 0
        self.accuracy = 100.0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.duration = self.default_duration
        self.is_paused = False
        self.is_completed = False
        self.result_banner.hide()
        self.pause_menu.hide()
        self._create_ui_elements()

    def on_enter(self, params=None):
        super().on_enter(params)
        params = params or {}
        if 'difficulty' in params:
            self.difficulty = params['difficulty']
        self._reset_runtime_state()
        
    def _toggle_pause(self):
        """
        Переключение состояния паузы
        """
        self.is_paused = not self.is_paused
        if self.is_paused:
            cont = self.localization.get_text('continue') if self.localization else "Продолжить"
            restart = self.localization.get_text('restart') if self.localization else "Начать заново"
            menu = self.localization.get_text('menu') if self.localization else "Меню"
            paused_title = self.localization.get_text('paused') if self.localization else "Пауза"
            options = [
                PauseOption(label=cont, callback=self._toggle_pause, color=COLORS['POSITIVE_GREEN']),
                PauseOption(label=restart, callback=self._restart_exercise),
                PauseOption(label=menu, callback=self._exit_to_menu)
            ]
            self.pause_menu.show(options, message=paused_title)
        else:
            self.pause_menu.hide()
            self._create_ui_elements()
        
    def _restart_exercise(self):
        """
        Перезапуск упражнения
        """
        # Сбрасываем все параметры упражнения
        self.score = 0
        self.accuracy = 100.0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.is_paused = False
        self.is_completed = False
        
        # Возвращаем стандартный UI
        self.pause_menu.hide()
        self._create_ui_elements()
        
    def _exit_to_menu(self):
        """
        Выход в главное меню
        """
        # Показываем диалог подтверждения
        # В реальном приложении здесь должен быть диалог
        self.transition_to('main_menu')
        
    def _complete_exercise(self):
        """
        Завершение упражнения и переход к экрану результатов
        """
        self.is_completed = True
        
        # Дать упражнению возможность посчитать финальный счет
        if hasattr(self, '_calculate_final_score'):
            try:
                self._calculate_final_score()
            except Exception as e:
                print(f'Ошибка вычисления финального счета: {e}')
        
        # Финальные метрики
        final_duration = self.elapsed_time
        final_score = int(self.score)
        final_accuracy = float(self.accuracy)

        # Если упражнение само ведет метрику точности (например, Следопыт), синхронизируем
        if hasattr(self, 'tracking_accuracy'):
            final_accuracy = float(self.tracking_accuracy)

        # Счет, который идет в расчет звезд (по умолчанию используем точность)
        star_score = int(getattr(self, 'star_score', final_accuracy if hasattr(self, 'tracking_accuracy') else final_score))
        xp_gain = int(getattr(self, 'xp_gain', final_score))
        xp_gain = max(0, xp_gain)
        star_score = max(0, star_score)
        
        # Сохранение результата в прогрессе
        try:
            exercise_id = self.exercise_id or self.__class__.__name__.lower()
            result = ExerciseResult(
                exercise_id=exercise_id,
                score=final_score,
                accuracy=final_accuracy,
                duration=final_duration,
                star_score=star_score,
                xp_gain=xp_gain,
            )
            if self.result_service:
                self.result_service.process(result)
            elif self.progress_manager:
                self.progress_manager.update_exercise_result(exercise_id, star_score, xp_gain)
                if self.achievements_manager:
                    self.achievements_manager.check_achievements()
        except Exception as e:
            print(f'Ошибка сохранения результата: {e}')
        
        self.transition_to(
            'results',
            exercise_id=exercise_id,
            score=final_score,
            accuracy=final_accuracy,
            duration=final_duration
        )
        
    def update(self, dt):
        """
        Обновление состояния упражнения
        
        Args:
            dt: время в секундах с последнего обновления
        """
        # Если упражнение на паузе или уже завершено, ничего не делаем
        if self.is_paused or self.is_completed:
            return

        # Обновляем текущую позицию курсора из общего обработчика ввода
        self.cursor_pos = self._get_cursor_position()
            
        # Обновление времени
        self.elapsed_time = time.time() - self.start_time
        
        # Проверка на завершение времени упражнения
        if self.elapsed_time >= self.duration:
            self._complete_exercise()
            
        # Специфичная для упражнения логика будет в классе-наследнике
        self._exercise_specific_update(dt)
        
    def _exercise_specific_update(self, dt):
        """
        Специфичное для упражнения обновление
        Должно быть переопределено в классе-наследнике
        
        Args:
            dt: время в секундах с последнего обновления
        """
        pass
        
    def draw(self):
        """
        Отрисовка упражнения
        """
        # Заливка экрана фоновым цветом
        self.screen.fill(COLORS['BACKGROUND'])

        # Отрисовка игровой области (показываем даже во время паузы, чтобы фон оставался видимым)
        self._draw_exercise_area()

        # Отрисовка информационной панели (счет, таймер и др.)
        self._draw_info_panel()

        # Оверлей паузы и меню, если активна пауза
        if self.is_paused:
            self.pause_menu.draw()

        # Отрисовка кнопок (пауза или пункты меню паузы)
        self.draw_buttons()
        self.result_banner.draw(self.screen)
        
    def _draw_exercise_area(self):
        """
        Отрисовка игровой области упражнения
        Должна быть переопределена в классе-наследнике
        """
        pass
        
    def _draw_info_panel(self):
        """
        Отрисовка информационной панели
        """
        next_y = self.hud.draw_basic(self.score, self.elapsed_time, self.duration)
        self._draw_extra_hud(next_y)

    def _get_cursor_position(self):
        """Единая точка получения позиции курсора с учетом жестового режима."""
        handler = getattr(self.screen_manager.game, 'input_handler', None)
        if handler:
            return handler.get_cursor_position()
        return pygame.mouse.get_pos()

    def _draw_extra_hud(self, y_start: int):
        """Хук для дополнительных метрик HUD в упражнениях."""
        # Реализация в наследниках по мере необходимости
        return

    def show_result_banner(self, title: str, lines: Iterable[str], **kwargs) -> None:
        """Показать стандартный баннер результатов в упражнении."""
        self.result_banner.show(title, lines, **kwargs)

    def hide_result_banner(self) -> None:
        """Спрятать текущий баннер результатов."""
        self.result_banner.hide()