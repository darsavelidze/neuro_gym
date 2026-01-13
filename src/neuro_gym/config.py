"""
Файл конфигурации для приложения NeuroGym
Содержит все основные настройки, константы и параметры
"""

import os

# ==================== Базовые пути ====================
# Корень проекта (на уровень выше каталога src/neuro_gym)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

def get_asset_path(*parts):
    """Возвращает путь внутри директории assets."""
    return os.path.join(ASSETS_DIR, *parts)

# ==================== Настройки окна ====================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "NeuroGym"
FPS = 60

# ==================== Цветовая схема ====================
COLORS = {
    'PRIMARY_BLUE': (106, 139, 200),     # #6A8BC8 - для фона и основных элементов
    'ACCENT_YELLOW': (240, 215, 140),    # #F0D78C - для акцентов и выделения
    'POSITIVE_GREEN': (125, 213, 143),   # #7DD58F - для положительной обратной связи
    'NEGATIVE_RED': (235, 138, 132),     # #EB8A84 - для отрицательной обратной связи
    'TEXT_DARK': (51, 51, 51),           # #333333 - темно-серый текст на светлом фоне
    'TEXT_LIGHT': (238, 238, 238),       # #EEEEEE - светло-серый текст на темном фоне
    'BACKGROUND': (240, 240, 245),       # #F0F0F5 - светлый фон
    'BLACK': (0, 0, 0),                  # Чёрный цвет
    'WHITE': (255, 255, 255),            # Белый цвет
}

# ==================== Настройки шрифтов ====================
FONT_FILE = os.path.join(BASE_DIR, 'pixeldigivolvecyrillic.otf')
if not os.path.exists(FONT_FILE):
    FONT_FILE = os.path.join(FONTS_DIR, 'pixeldigivolvecyrillic.otf')

FONT_SIZES = {
    'SMALL': 18,
    'MEDIUM': 24,
    'LARGE': 36,
    'EXTRA_LARGE': 48
}

# ==================== Уровни сложности ====================
DIFFICULTY_LEVELS = ['Легкий', 'Средний', 'Сложный']
DEFAULT_DIFFICULTY = 'Легкий'

# ==================== Настройки звука ====================
SOUND_VOLUME = 0.5
MUSIC_VOLUME = 0.3

# ==================== Настройки UI ====================
MIN_INTERACTIVE_ELEMENT_SIZE = 64
BUTTON_PADDING = 20
SCREEN_PADDING = 50

# ==================== Настройки распознавания жестов ====================
GESTURE_DELAY = 500
MAX_LATENCY = 100
CLICK_HOLD_TIME = 0.8
CLICK_THRESHOLD = 20
PINCH_THRESHOLD = 30
SWIPE_SPEED_THRESHOLD = 500
SWIPE_MIN_DISTANCE = 100
TRACKING_HISTORY_SIZE = 10
LOST_TRACKING_TIMEOUT = 0.5

# ==================== Настройки dwell-клика (задержка наведения) ====================
DWELL_TIME = 1.0        # секунд удержания для клика
DWELL_RADIUS = 50       # пикселей — допустимое смещение курсора во время dwell
DWELL_COOLDOWN = 0.4    # секунд паузы после dwell-клика

# ==================== Настройки упражнений ====================
EXERCISE_DURATION = 60

# ==================== Список упражнений ====================
EXERCISES = [
    {
        'id': 'pathfinder',
        'name': 'Следопыт',
        'description': 'Следуй за движущимся объектом указательным пальцем',
        'screen': 'neuro_gym.exercises.pathfinder.Pathfinder'
    },
    {
        'id': 'trajectory',
        'name': 'Траектория',
        'description': 'Проведи пальцем по заданному пути, не выходя за границы',
        'screen': 'neuro_gym.exercises.trajectory.Trajectory'
    },
    {
        'id': 'sorting',
        'name': 'Сортировка',
        'description': 'Сортируй объекты, перетаскивая их в правильные контейнеры',
        'screen': 'neuro_gym.exercises.sorting.Sorting'
    },
    {
        'id': 'sequence',
        'name': 'Запоминание последовательности',
        'description': 'Запомни и повтори последовательность появления объектов',
        'screen': 'neuro_gym.exercises.sequence.Sequence'
    },
    {
        'id': 'fast_fingers',
        'name': 'Ловкие пальчики',
        'description': 'Быстро касайся появляющихся объектов',
        'screen': 'neuro_gym.exercises.fast_fingers.FastFingers'
    }
]

# ==================== Настройки сохранения ====================
SAVE_FILE = os.path.join(BASE_DIR, 'save_data.json')

# ==================== Версия приложения ====================
VERSION = "0.1.0"
