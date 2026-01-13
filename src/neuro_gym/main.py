"""
Главный файл приложения NeuroGym
"""

from .core.game import Game


def main():
    """Основная функция для запуска приложения"""
    game = Game()
    game.start()


if __name__ == "__main__":
    main()