"""
Менеджер прогресса для приложения NeuroGym
Отвечает за сохранение и загрузку прогресса пользователя
"""

import os
import json
import time
import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from config import SAVE_FILE

class ProgressManager:
    def __init__(self):
        """
        Инициализация менеджера прогресса
        """
        # Структура данных прогресса
        self.progress_data = {
            'user': {
                'last_played': None,
                'total_time': 0,
                'difficulty': 'Легкий'
            },
            'exercises': {
                'pathfinder': {'best_score': 0, 'stars': 0, 'times_played': 0},
                'trajectory': {'best_score': 0, 'stars': 0, 'times_played': 0},
                'sorting': {'best_score': 0, 'stars': 0, 'times_played': 0},
                'sequence': {'best_score': 0, 'stars': 0, 'times_played': 0},
                'fast_fingers': {'best_score': 0, 'stars': 0, 'times_played': 0}
            },
            'achievements': [],
            'collected_items': []
        }
        
        # Путь к файлу сохранения
        self.save_file = SAVE_FILE
        
        # Загрузка сохраненных данных, если файл существует
        self.load_progress()
        
    def load_progress(self):
        """
        Загрузка сохраненного прогресса
        """
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as file:
                    loaded_data = json.load(file)
                    # Обновляем текущие данные загруженными
                    self._merge_progress_data(loaded_data)
                    print("Прогресс успешно загружен")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки прогресса: {e}")
                # Создаем резервную копию поврежденного файла
                if os.path.exists(self.save_file):
                    backup_file = f"{self.save_file}.backup.{int(time.time())}"
                    try:
                        os.rename(self.save_file, backup_file)
                        print(f"Создана резервная копия поврежденного файла: {backup_file}")
                    except Exception as backup_error:
                        print(f"Не удалось создать резервную копию: {backup_error}")
    
    def _merge_progress_data(self, loaded_data):
        """
        Слияние загруженных данных с текущей структурой
        
        Args:
            loaded_data: загруженные данные
        """
        # Обновляем данные пользователя
        if 'user' in loaded_data:
            self.progress_data['user'].update(loaded_data['user'])
            
        # Обновляем данные упражнений
        if 'exercises' in loaded_data:
            for exercise_id, exercise_data in loaded_data['exercises'].items():
                if exercise_id in self.progress_data['exercises']:
                    self.progress_data['exercises'][exercise_id].update(exercise_data)
                    
        # Обновляем данные достижений
        if 'achievements' in loaded_data:
            self.progress_data['achievements'] = loaded_data['achievements']
            
        # Обновляем данные коллекционных предметов
        if 'collected_items' in loaded_data:
            self.progress_data['collected_items'] = loaded_data['collected_items']
        
    def save_progress(self):
        """
        Сохранение прогресса в файл
        """
        try:
            # Обновляем время последней игры
            self.progress_data['user']['last_played'] = time.time()
            
            # Создаем директорию для файла сохранения, если она не существует
            save_dir = os.path.dirname(self.save_file)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            # Сохраняем в файл с читаемым форматированием
            with open(self.save_file, 'w', encoding='utf-8') as file:
                json.dump(self.progress_data, file, ensure_ascii=False, indent=2)
                print("Прогресс успешно сохранен")
        except IOError as e:
            print(f"Ошибка сохранения прогресса: {e}")
    
    def update_exercise_result(self, exercise_id, score):
        """
        Обновление результата упражнения
        
        Args:
            exercise_id: идентификатор упражнения
            score: набранные очки
            
        Returns:
            int: количество заработанных звезд (от 1 до 3)
        """
        if exercise_id in self.progress_data['exercises']:
            # Увеличиваем счетчик прохождений
            self.progress_data['exercises'][exercise_id]['times_played'] += 1
            
            # Обновляем лучший счет, если текущий результат лучше
            if score > self.progress_data['exercises'][exercise_id]['best_score']:
                self.progress_data['exercises'][exercise_id]['best_score'] = score
                
            # Рассчитываем звезды (1-3) в зависимости от счета
            stars = 1
            if score >= 80:
                stars = 3
            elif score >= 50:
                stars = 2
                
            # Сохраняем максимальное количество звезд
            if stars > self.progress_data['exercises'][exercise_id]['stars']:
                self.progress_data['exercises'][exercise_id]['stars'] = stars
                
            # Автоматически сохраняем прогресс
            self.save_progress()
            
            return stars
        return 0
        
    def add_achievement(self, achievement_id):
        """
        Добавление достижения
        
        Args:
            achievement_id: идентификатор достижения
            
        Returns:
            bool: True, если достижение добавлено впервые, иначе False
        """
        if achievement_id not in self.progress_data['achievements']:
            self.progress_data['achievements'].append(achievement_id)
            self.save_progress()
            return True
        return False
        
    def add_collected_item(self, item_id):
        """
        Добавление коллекционного предмета
        
        Args:
            item_id: идентификатор предмета
            
        Returns:
            bool: True, если предмет добавлен впервые, иначе False
        """
        if item_id not in self.progress_data['collected_items']:
            self.progress_data['collected_items'].append(item_id)
            self.save_progress()
            return True
        return False
        
    def set_difficulty(self, difficulty):
        """
        Установка уровня сложности
        
        Args:
            difficulty: уровень сложности ('Легкий', 'Средний', 'Сложный')
        """
        if difficulty in ['Легкий', 'Средний', 'Сложный']:
            self.progress_data['user']['difficulty'] = difficulty
            self.save_progress()
            
    def get_difficulty(self):
        """
        Получение текущего уровня сложности
        
        Returns:
            str: текущий уровень сложности
        """
        return self.progress_data['user']['difficulty']
        
    def get_total_stars(self):
        """
        Получение общего количества звезд
        
        Returns:
            int: общее количество звезд
        """
        return sum(exercise['stars'] for exercise in self.progress_data['exercises'].values())
        
    def get_exercise_data(self, exercise_id):
        """
        Получение данных упражнения
        
        Args:
            exercise_id: идентификатор упражнения
            
        Returns:
            dict: данные упражнения или None, если упражнение не найдено
        """
        return self.progress_data['exercises'].get(exercise_id)
        
    def reset_progress(self, full_reset=False):
        """
        Сброс прогресса
        
        Args:
            full_reset: если True, сбрасывает весь прогресс, иначе только результаты упражнений
        """
        if full_reset:
            # Сбрасываем все данные
            self.progress_data = {
                'user': {
                    'last_played': None,
                    'total_time': 0,
                    'difficulty': 'Легкий'
                },
                'exercises': {
                    'pathfinder': {'best_score': 0, 'stars': 0, 'times_played': 0},
                    'trajectory': {'best_score': 0, 'stars': 0, 'times_played': 0},
                    'sorting': {'best_score': 0, 'stars': 0, 'times_played': 0},
                    'sequence': {'best_score': 0, 'stars': 0, 'times_played': 0},
                    'fast_fingers': {'best_score': 0, 'stars': 0, 'times_played': 0}
                },
                'achievements': [],
                'collected_items': []
            }
        else:
            # Сбрасываем только результаты упражнений
            for exercise in self.progress_data['exercises']:
                self.progress_data['exercises'][exercise] = {'best_score': 0, 'stars': 0, 'times_played': 0}
        
        # Сохраняем изменения
        self.save_progress()
