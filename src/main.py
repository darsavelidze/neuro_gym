"""
Главный файл приложения NeuroGym
"""

import sys
import os

# Добавляем путь к исходным файлам в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game

def main():
    """
    Основная функция для запуска приложения
    """
    # Создание и запуск игры
    game = Game()
    game.start()

if __name__ == "__main__":
    main()