"""
Система локализации для приложения NeuroGym
Отвечает за перевод интерфейса на различные языки
"""

class LocalizationManager:
    def __init__(self):
        """
        Инициализация менеджера локализации
        """
        # Доступные языки
        self.languages = ['ru', 'en']
        
        # Язык по умолчанию
        self.current_language = 'ru'
        
        # Словари локализации
        self.translations = self._initialize_translations()
        
    def _initialize_translations(self):
        """
        Инициализация словарей локализации
        
        Returns:
            dict: словари с переводами
        """
        return {
            # Общие элементы интерфейса
            'app_name': {'ru': 'NeuroGym', 'en': 'NeuroGym'},
            'back': {'ru': 'Назад', 'en': 'Back'},
            'next': {'ru': 'Далее', 'en': 'Next'},
            'ok': {'ru': 'OK', 'en': 'OK'},
            'cancel': {'ru': 'Отмена', 'en': 'Cancel'},
            'start': {'ru': 'НАЧАТЬ', 'en': 'START'},
            'exit': {'ru': 'Выход', 'en': 'Exit'},
            'loading': {'ru': 'Загрузка...', 'en': 'Loading...'},
            'paused': {'ru': 'Пауза', 'en': 'Paused'},
            'continue': {'ru': 'Продолжить', 'en': 'Continue'},
            'restart': {'ru': 'Заново', 'en': 'Restart'},
            'menu': {'ru': 'Меню', 'en': 'Menu'},
            
            # Главное меню
            'main_menu': {'ru': 'Главное меню', 'en': 'Main Menu'},
            'exercises': {'ru': 'Упражнения', 'en': 'Exercises'},
            'achievements': {'ru': 'Достижения', 'en': 'Achievements'},
            'settings': {'ru': 'Настройки', 'en': 'Settings'},
            
            # Уровни сложности
            'difficulty': {'ru': 'Сложность', 'en': 'Difficulty'},
            'easy': {'ru': 'Легкий', 'en': 'Easy'},
            'medium': {'ru': 'Средний', 'en': 'Medium'},
            'hard': {'ru': 'Сложный', 'en': 'Hard'},
            
            # Упражнения
            'exercise_pathfinder': {'ru': 'Следопыт', 'en': 'Pathfinder'},
            'exercise_trajectory': {'ru': 'Траектория', 'en': 'Trajectory'},
            'exercise_sorting': {'ru': 'Сортировка', 'en': 'Sorting'},
            'exercise_sequence': {'ru': 'Запоминание последовательности', 'en': 'Sequence Memory'},
            'exercise_fast_fingers': {'ru': 'Ловкие пальчики', 'en': 'Fast Fingers'},
            
            # Описания упражнений
            'desc_pathfinder': {
                'ru': 'Следуй за движущимся объектом указательным пальцем. Старайся удерживать палец на объекте.',
                'en': 'Follow the moving object with your index finger. Try to keep your finger on the object.'
            },
            'desc_trajectory': {
                'ru': 'Проведи пальцем по линии от начала до конца. Старайся не выходить за границы.',
                'en': 'Trace the line with your finger from start to finish. Try not to go outside the boundaries.'
            },
            'desc_sorting': {
                'ru': 'Перетащи предметы в соответствующие контейнеры, распределяя их по группам.',
                'en': 'Drag items to their corresponding containers, sorting them into groups.'
            },
            'desc_sequence': {
                'ru': 'Запомни и повтори последовательность подсвеченных объектов, нажимая на них в том же порядке.',
                'en': 'Remember and repeat the sequence of highlighted objects by tapping them in the same order.'
            },
            'desc_fast_fingers': {
                'ru': 'Быстро касайся появляющихся на экране объектов, прежде чем они исчезнут.',
                'en': 'Quickly touch objects appearing on the screen before they disappear.'
            },
            
            # Настройки
            'sound_effects': {'ru': 'Звуковые эффекты', 'en': 'Sound Effects'},
            'music': {'ru': 'Музыка', 'en': 'Music'},
            'language': {'ru': 'Язык', 'en': 'Language'},
            'input_mode': {'ru': 'Режим управления', 'en': 'Input Mode'},
            'input_mouse': {'ru': 'Мышь', 'en': 'Mouse'},
            'input_hand': {'ru': 'Рука (камера)', 'en': 'Hand (camera)'},
            'hand_tracking_started': {
                'ru': 'Управление рукой включено',
                'en': 'Hand tracking enabled'
            },
            'hand_tracking_failed': {
                'ru': 'Не удалось включить камеру. Проверьте подключение.',
                'en': 'Failed to enable camera. Check connection.'
            },
            'reset_progress': {'ru': 'Сбросить прогресс', 'en': 'Reset Progress'},
            'confirm_reset': {
                'ru': 'Вы действительно хотите сбросить весь прогресс?',
                'en': 'Are you sure you want to reset all progress?'
            },
            
            # Игровые элементы
            'score': {'ru': 'Счёт', 'en': 'Score'},
            'time': {'ru': 'Время', 'en': 'Time'},
            'stars': {'ru': 'Звёзды', 'en': 'Stars'},
            'best': {'ru': 'Лучший', 'en': 'Best'},
            'completed': {'ru': 'Завершено', 'en': 'Completed'},
            'well_done': {'ru': 'Отлично!', 'en': 'Well done!'},
            'try_again': {'ru': 'Попробуй ещё раз', 'en': 'Try again'},
            'level': {'ru': 'Уровень', 'en': 'Level'},
            'hits': {'ru': 'Попадания', 'en': 'Hits'},
            'misses': {'ru': 'Промахи', 'en': 'Misses'},
            'combo': {'ru': 'Комбо', 'en': 'Combo'},
            'target': {'ru': 'Цель', 'en': 'Target'},
            'errors': {'ru': 'Ошибки', 'en': 'Errors'},
            'max_combo': {'ru': 'Макс. комбо', 'en': 'Max combo'},
            'placed': {'ru': 'Размещено', 'en': 'Placed'},
            'too_many_errors': {'ru': 'Слишком много ошибок', 'en': 'Too many errors'},
            'time_over': {'ru': 'Время вышло!', 'en': 'Time is over!'},
            'great_job': {'ru': 'Отличная работа!', 'en': 'Great job!'},
            'congrats': {'ru': 'Поздравляем!', 'en': 'Congratulations!'},
            'remember_sequence': {'ru': 'Запоминайте последовательность...', 'en': 'Remember the sequence...'},
            'repeat_sequence': {'ru': 'Повторите последовательность', 'en': 'Repeat the sequence'},
            'all_levels_done': {'ru': 'Все уровни пройдены!', 'en': 'All levels completed!'},
            
            # Экран результатов
            'exercise_completed': {'ru': 'Упражнение завершено', 'en': 'Exercise Completed'},
            'your_score': {'ru': 'Ваш счёт', 'en': 'Your Score'},
            'best_score': {'ru': 'Лучший результат', 'en': 'Best Score'},
            'new_record': {'ru': 'Новый рекорд!', 'en': 'New Record!'},
            'new_achievement': {'ru': 'Новое достижение!', 'en': 'New Achievement!'},
            'retry': {'ru': 'Попробовать ещё', 'en': 'Try Again'},
            'next_exercise': {'ru': 'Следующее упражнение', 'en': 'Next Exercise'},
            
            # Сообщения об ошибках
            'camera_error': {'ru': 'Ошибка камеры', 'en': 'Camera Error'},
            'camera_not_available': {
                'ru': 'Камера недоступна. Управление переключено на мышь.',
                'en': 'Camera not available. Control switched to mouse.'
            },
            'exercise_error': {'ru': 'Ошибка упражнения', 'en': 'Exercise Error'},
            'save_error': {'ru': 'Ошибка сохранения', 'en': 'Save Error'}
        }
        
    def get_text(self, key, language=None):
        """
        Получение локализованного текста по ключу
        
        Args:
            key: ключ текста
            language: язык (если None, используется текущий язык)
            
        Returns:
            str: локализованный текст или ключ, если текст не найден
        """
        if language is None:
            language = self.current_language
            
        if key not in self.translations:
            return key
            
        if language not in self.translations[key]:
            # Возвращаем текст на языке по умолчанию или ключ
            return self.translations[key].get('ru', key)
            
        return self.translations[key][language]
    
    def set_language(self, language):
        """
        Установка текущего языка
        
        Args:
            language: код языка ('ru' или 'en')
        """
        if language in self.languages:
            self.current_language = language
            
    def get_language(self):
        """
        Получение текущего языка
        
        Returns:
            str: текущий язык
        """
        return self.current_language
        
    def get_language_name(self, language=None):
        """
        Получение названия языка
        
        Args:
            language: код языка (если None, используется текущий язык)
            
        Returns:
            str: название языка
        """
        if language is None:
            language = self.current_language
            
        language_names = {
            'ru': 'Русский',
            'en': 'English'
        }
        
        return language_names.get(language, language)
