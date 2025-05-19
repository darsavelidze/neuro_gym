"""
Менеджер достижений для приложения NeuroGym
Отвечает за отслеживание и управление достижениями пользователя
"""

import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')

class AchievementsManager:
    def __init__(self, progress_manager, sound_manager):
        """
        Инициализация менеджера достижений
        
        Args:
            progress_manager: менеджер прогресса
            sound_manager: менеджер звуков
        """
        self.progress_manager = progress_manager
        self.sound_manager = sound_manager
        self.achievements = self._initialize_achievements()
        
    def _initialize_achievements(self):
        """
        Инициализация списка достижений
        
        Returns:
            list: список достижений
        """
        return [
            {
                'id': 'first_steps',
                'name': 'Первые шаги',
                'name_en': 'First Steps',
                'description': 'Пройди любое упражнение впервые',
                'description_en': 'Complete any exercise for the first time',
                'icon': 'achievement_first.png',
                'condition': lambda data: any(ex['times_played'] > 0 for ex in data['exercises'].values())
            },
            {
                'id': 'star_collector_10',
                'name': 'Коллекционер звёзд',
                'name_en': 'Star Collector',
                'description': 'Собери 10 звёзд в общей сложности',
                'description_en': 'Collect 10 stars in total',
                'icon': 'achievement_stars.png',
                'condition': lambda data: sum(ex['stars'] for ex in data['exercises'].values()) >= 10
            },
            {
                'id': 'master_pathfinder',
                'name': 'Мастер Следопыта',
                'name_en': 'Pathfinder Master',
                'description': 'Получи 3 звезды в упражнении "Следопыт"',
                'description_en': 'Get 3 stars in the "Pathfinder" exercise',
                'icon': 'achievement_pathfinder.png',
                'condition': lambda data: data['exercises']['pathfinder']['stars'] >= 3
            },
            {
                'id': 'trajectory_expert',
                'name': 'Эксперт Траектории',
                'name_en': 'Trajectory Expert',
                'description': 'Получи 3 звезды в упражнении "Траектория"',
                'description_en': 'Get 3 stars in the "Trajectory" exercise',
                'icon': 'achievement_trajectory.png',
                'condition': lambda data: data['exercises']['trajectory']['stars'] >= 3
            },
            {
                'id': 'sorting_guru',
                'name': 'Гуру Сортировки',
                'name_en': 'Sorting Guru',
                'description': 'Получи 3 звезды в упражнении "Сортировка"',
                'description_en': 'Get 3 stars in the "Sorting" exercise',
                'icon': 'achievement_sorting.png',
                'condition': lambda data: data['exercises']['sorting']['stars'] >= 3
            },
            {
                'id': 'memory_master',
                'name': 'Мастер Памяти',
                'name_en': 'Memory Master',
                'description': 'Получи 3 звезды в упражнении "Запоминание последовательности"',
                'description_en': 'Get 3 stars in the "Sequence Memory" exercise',
                'icon': 'achievement_sequence.png',
                'condition': lambda data: data['exercises']['sequence']['stars'] >= 3
            },
            {
                'id': 'quick_fingers',
                'name': 'Быстрые Пальчики',
                'name_en': 'Fast Fingers',
                'description': 'Получи 3 звезды в упражнении "Ловкие пальчики"',
                'description_en': 'Get 3 stars in the "Fast Fingers" exercise',
                'icon': 'achievement_fast_fingers.png',
                'condition': lambda data: data['exercises']['fast_fingers']['stars'] >= 3
            },
            {
                'id': 'all_star',
                'name': 'Золотой фонд',
                'name_en': 'Gold Collection',
                'description': 'Получи 3 звезды во всех упражнениях',
                'description_en': 'Get 3 stars in all exercises',
                'icon': 'achievement_all_star.png',
                'condition': lambda data: all(ex['stars'] >= 3 for ex in data['exercises'].values())
            },
            {
                'id': 'persistent_player',
                'name': 'Настойчивость',
                'name_en': 'Persistence',
                'description': 'Пройди упражнения 20 раз в общей сложности',
                'description_en': 'Complete exercises 20 times in total',
                'icon': 'achievement_persistent.png',
                'condition': lambda data: sum(ex['times_played'] for ex in data['exercises'].values()) >= 20
            }
        ]
    
    def check_achievements(self):
        """
        Проверка условий получения достижений
        
        Returns:
            list: список новых достижений
        """
        new_achievements = []
        
        for achievement in self.achievements:
            # Если достижение еще не получено
            if achievement['id'] not in self.progress_manager.progress_data['achievements']:
                # Проверяем условие получения
                if achievement['condition'](self.progress_manager.progress_data):
                    # Добавляем достижение в список полученных
                    if self.progress_manager.add_achievement(achievement['id']):
                        new_achievements.append(achievement)
                        # Воспроизводим звук получения достижения
                        self.sound_manager.play_sound('achievement')
        
        return new_achievements
    
    def get_all_achievements(self, language='ru'):
        """
        Получение списка всех достижений с указанием, получены ли они
        
        Args:
            language: язык для текстовых полей ('ru' или 'en')
            
        Returns:
            list: список достижений
        """
        result = []
        achieved_ids = self.progress_manager.progress_data['achievements']
        
        for achievement in self.achievements:
            is_achieved = achievement['id'] in achieved_ids
            
            # Выбираем названия и описания в зависимости от языка
            name_key = 'name' if language == 'ru' else 'name_en'
            desc_key = 'description' if language == 'ru' else 'description_en'
            
            result.append({
                'id': achievement['id'],
                'name': achievement[name_key],
                'description': achievement[desc_key],
                'icon': achievement['icon'],
                'achieved': is_achieved
            })
            
        return result
