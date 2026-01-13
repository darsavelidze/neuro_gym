#!/usr/bin/env python3
"""
Скрипт для запуска приложения NeuroGym
"""

import sys
import os

# Подавляем предупреждения macOS о дублировании SDL-классов
# (pygame и opencv-python оба содержат libSDL2)
os.environ.setdefault('OBJC_DISABLE_INITIALIZE_FORK_SAFETY', 'YES')

# Добавляем путь к исходным файлам (src layout)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """
    Главная функция для запуска приложения
    """
    try:
        print("=" * 60)
        print("🎮 Запуск приложения NeuroGym...")
        print("=" * 60)
        
        from neuro_gym.core.game import Game
        
        # Создаем и запускаем игру
        game = Game()
        game.start()
        
    except KeyboardInterrupt:
        print("\n\n👋 Приложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
