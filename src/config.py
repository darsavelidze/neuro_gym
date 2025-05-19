"""
Файл конфигурации для приложения NeuroGym
Содержит все основные настройки, константы и параметры
"""

import os

# Базовые пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Настройки окна
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "NeuroGym"
FPS = 60

# Цветовая схема в соответствии с ТЗ
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

# Настройки шрифтов
# Пробуем сначала загрузить шрифт из корня проекта, затем из assets
FONT_FILE = os.path.join(BASE_DIR, 'pixeldigivolvecyrillic.otf')
if not os.path.exists(FONT_FILE):
    FONT_FILE = os.path.join(FONTS_DIR, 'pixeldigivolvecyrillic.otf')

FONT_SIZES = {
    'SMALL': 18,
    'MEDIUM': 24,
    'LARGE': 36,
    'EXTRA_LARGE': 48
}

# Уровни сложности
DIFFICULTY_LEVELS = ['Легкий', 'Средний', 'Сложный']
DEFAULT_DIFFICULTY = 'Легкий'

# Настройки звука
SOUND_VOLUME = 0.5          # 50% от максимальной громкости
MUSIC_VOLUME = 0.3          # 30% от максимальной громкости

# Настройки UI
MIN_INTERACTIVE_ELEMENT_SIZE = 64  # минимальный размер интерактивного элемента (64x64 пикселей)
BUTTON_PADDING = 20               # отступы для кнопок
SCREEN_PADDING = 50               # отступы от края экрана

# Настройки распознавания жестов
GESTURE_DELAY = 500               # миллисекунды для распознавания жеста "клик" (задержка)
MAX_LATENCY = 100                 # максимальная задержка между движением и реакцией (мс)

# Дополнительные параметры для распознавания жестов
CLICK_HOLD_TIME = 0.8             # время удержания для клика в секундах
CLICK_THRESHOLD = 20              # допустимое отклонение для клика в пикселях
PINCH_THRESHOLD = 30              # расстояние между пальцами для захвата в пикселях
SWIPE_SPEED_THRESHOLD = 500       # скорость для распознавания свайпа в пикселях/сек
SWIPE_MIN_DISTANCE = 100          # минимальное расстояние для свайпа в пикселях
TRACKING_HISTORY_SIZE = 10        # размер истории для отслеживания движений
LOST_TRACKING_TIMEOUT = 0.5       # время до признания потери отслеживания в секундах

# Настройки упражнений
EXERCISE_DURATION = 60            # стандартная длительность упражнения в секундах

# Список всех упражнений
EXERCISES = [
    {
        'id': 'pathfinder',
        'name': 'Следопыт',
        'description': 'Следуй за движущимся объектом указательным пальцем'
    },
    {
        'id': 'trajectory',
        'name': 'Траектория',
        'description': 'Проведи пальцем по заданному пути, не выходя за границы'
    },
    {
        'id': 'sorting',
        'name': 'Сортировка',
        'description': 'Сортируй объекты, перетаскивая их в правильные контейнеры'
    },
    {
        'id': 'sequence',
        'name': 'Запоминание последовательности',
        'description': 'Запомни и повтори последовательность появления объектов'
    },
    {
        'id': 'fast_fingers',
        'name': 'Ловкие пальчики',
        'description': 'Быстро касайся появляющихся объектов'
    }
]

# Настройки сохранения прогресса
SAVE_FILE = os.path.join(BASE_DIR, 'save_data.json')

# Версия приложения
VERSION = "0.1.0"
