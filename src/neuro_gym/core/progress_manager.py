"""
Менеджер прогресса для приложения NeuroGym
Отвечает за сохранение и загрузку прогресса пользователя
"""

import os
import json
import time

from ..config import SAVE_FILE, EXERCISES

# Идентификаторы всех упражнений (из конфигурации)
_EXERCISE_IDS = [ex['id'] for ex in EXERCISES]


def _default_exercise_entry():
    """Возвращает начальные данные для одного упражнения."""
    return {'best_score': 0, 'stars': 0, 'times_played': 0, 'xp': 0}


def _default_progress_data(level_step: int):
    """Возвращает пустую структуру прогресса."""
    return {
        'user': {
            'last_played': None,
            'total_time': 0,
            'difficulty': 'Легкий'
        },
        'exercises': {eid: _default_exercise_entry() for eid in _EXERCISE_IDS},
        'achievements': [],
        'collected_items': [],
        'experience': {
            'total_xp': 0,
            'level': 1,
            'next_level_xp': level_step,
            'per_exercise': {eid: 0 for eid in _EXERCISE_IDS}
        }
    }


class ProgressManager:
    def __init__(self):
        """Инициализация менеджера прогресса"""
        self.level_step = 200
        self.progress_data = _default_progress_data(self.level_step)
        self.save_file = SAVE_FILE
        self.load_progress()
        
    def load_progress(self):
        """Загрузка сохраненного прогресса"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as file:
                    loaded_data = json.load(file)
                    self._merge_progress_data(loaded_data)
                    print("Прогресс успешно загружен")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки прогресса: {e}")
                if os.path.exists(self.save_file):
                    backup_file = f"{self.save_file}.backup.{int(time.time())}"
                    try:
                        os.rename(self.save_file, backup_file)
                        print(f"Создана резервная копия: {backup_file}")
                    except Exception as backup_error:
                        print(f"Не удалось создать резервную копию: {backup_error}")
    
    def _merge_progress_data(self, loaded_data):
        """Слияние загруженных данных с текущей структурой"""
        if 'user' in loaded_data:
            self.progress_data['user'].update(loaded_data['user'])
            
        if 'exercises' in loaded_data:
            for exercise_id, exercise_data in loaded_data['exercises'].items():
                if exercise_id not in self.progress_data['exercises']:
                    self.progress_data['exercises'][exercise_id] = _default_exercise_entry()
                self.progress_data['exercises'][exercise_id].update(exercise_data)
                self.progress_data['exercises'][exercise_id].setdefault('xp', 0)
                    
        if 'achievements' in loaded_data:
            self.progress_data['achievements'] = loaded_data['achievements']
            
        if 'collected_items' in loaded_data:
            self.progress_data['collected_items'] = loaded_data['collected_items']

        if 'experience' in loaded_data:
            exp = loaded_data['experience']
            self.progress_data['experience']['total_xp'] = exp.get('total_xp', self.progress_data['experience']['total_xp'])
            self.progress_data['experience']['level'] = exp.get('level', self.progress_data['experience']['level'])
            self.progress_data['experience']['next_level_xp'] = exp.get('next_level_xp', self.level_step)
            per_ex = exp.get('per_exercise', {})
            for ex_id in self.progress_data['exercises']:
                self.progress_data['experience']['per_exercise'].setdefault(ex_id, 0)
                if ex_id in per_ex:
                    self.progress_data['experience']['per_exercise'][ex_id] = per_ex[ex_id]

        # На случай если в сохранении не было блока опыта
        else:
            self._recalculate_level()
        
    def save_progress(self):
        """Сохранение прогресса в файл"""
        try:
            self.progress_data['user']['last_played'] = time.time()
            
            save_dir = os.path.dirname(self.save_file)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            with open(self.save_file, 'w', encoding='utf-8') as file:
                json.dump(self.progress_data, file, ensure_ascii=False, indent=2)
                print("Прогресс успешно сохранен")
        except IOError as e:
            print(f"Ошибка сохранения прогресса: {e}")
    
    def update_exercise_result(self, exercise_id, score, xp_gain=0):
        """Обновление результата упражнения и начисление опыта"""
        self._ensure_exercise_entry(exercise_id)

        exercise = self.progress_data['exercises'][exercise_id]
        exercise['times_played'] += 1
        
        if score > exercise['best_score']:
            exercise['best_score'] = score
            
        stars = 1
        if score >= 80:
            stars = 3
        elif score >= 50:
            stars = 2
            
        if stars > exercise['stars']:
            exercise['stars'] = stars

        if xp_gain > 0:
            self.add_experience(exercise_id, xp_gain, save=False)
            exercise['xp'] += xp_gain
        
        self.save_progress()
        return stars
        
    def add_achievement(self, achievement_id):
        """Добавление достижения"""
        if achievement_id not in self.progress_data['achievements']:
            self.progress_data['achievements'].append(achievement_id)
            self.save_progress()
            return True
        return False

    def add_experience(self, exercise_id, xp_gain, save=True):
        """Начисление опыта за упражнение"""
        if xp_gain <= 0:
            return {'level_up': False}

        self._ensure_exercise_entry(exercise_id)
        exp_block = self.progress_data['experience']
        exp_block['total_xp'] += xp_gain
        exp_block['per_exercise'][exercise_id] = exp_block['per_exercise'].get(exercise_id, 0) + xp_gain

        previous_level = exp_block['level']
        self._recalculate_level()
        leveled_up = exp_block['level'] > previous_level
        
        if save:
            self.save_progress()

        return {'level_up': leveled_up, 'level': exp_block['level'], 'total_xp': exp_block['total_xp']}

    def _recalculate_level(self):
        """Пересчет уровня пользователя по общему опыту"""
        exp_block = self.progress_data['experience']
        total_xp = exp_block.get('total_xp', 0)
        exp_block['level'] = max(1, total_xp // self.level_step + 1)
        exp_block['next_level_xp'] = exp_block['level'] * self.level_step

    def get_level_info(self):
        """Возвращает информацию об уровне и прогрессе опыта"""
        exp_block = self.progress_data['experience']
        level = exp_block.get('level', 1)
        total_xp = exp_block.get('total_xp', 0)
        next_level_xp = exp_block.get('next_level_xp', self.level_step)
        current_level_floor = (level - 1) * self.level_step
        xp_into_level = max(0, total_xp - current_level_floor)
        xp_to_next = max(0, next_level_xp - total_xp)

        return {
            'level': level,
            'total_xp': total_xp,
            'xp_into_level': xp_into_level,
            'xp_to_next': xp_to_next,
            'level_cap': self.level_step
        }
        
    def add_collected_item(self, item_id):
        """Добавление коллекционного предмета"""
        if item_id not in self.progress_data['collected_items']:
            self.progress_data['collected_items'].append(item_id)
            self.save_progress()
            return True
        return False
        
    def set_difficulty(self, difficulty):
        """Установка уровня сложности"""
        if difficulty in ['Легкий', 'Средний', 'Сложный']:
            self.progress_data['user']['difficulty'] = difficulty
            self.save_progress()
            
    def get_difficulty(self):
        """Получение текущего уровня сложности"""
        return self.progress_data['user']['difficulty']
        
    def get_total_stars(self):
        """Получение общего количества звезд"""
        return sum(exercise['stars'] for exercise in self.progress_data['exercises'].values())
        
    def get_exercise_data(self, exercise_id):
        """Получение данных упражнения"""
        return self.progress_data['exercises'].get(exercise_id)
        
    def reset_progress(self, full_reset=False):
        """Сброс прогресса"""
        if full_reset:
            self.progress_data = _default_progress_data(self.level_step)
        else:
            for exercise in self.progress_data['exercises']:
                self.progress_data['exercises'][exercise] = _default_exercise_entry()
                self.progress_data['experience']['per_exercise'][exercise] = 0

        self.progress_data['experience']['total_xp'] = 0
        self.progress_data['experience']['level'] = 1
        self.progress_data['experience']['next_level_xp'] = self.level_step

        self.save_progress()

    def _ensure_exercise_entry(self, exercise_id):
        """Гарантирует наличие записи об упражнении в прогрессе"""
        if exercise_id not in self.progress_data['exercises']:
            self.progress_data['exercises'][exercise_id] = _default_exercise_entry()
        if 'experience' not in self.progress_data:
            self.progress_data['experience'] = {
                'total_xp': 0,
                'level': 1,
                'next_level_xp': self.level_step,
                'per_exercise': {}
            }
        self.progress_data['experience']['per_exercise'].setdefault(exercise_id, 0)
