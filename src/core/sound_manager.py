"""
Менеджер звуков для приложения NeuroGym
Отвечает за воспроизведение звуковых эффектов и управление звуком
"""

import pygame
import os
import sys
sys.path.append('/Users/sandro/Downloads/neuro_gym/src')
from config import SOUND_VOLUME, MUSIC_VOLUME

class SoundManager:
    def __init__(self):
        """
        Инициализация менеджера звуков
        """
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.sound_volume = SOUND_VOLUME
        self.music_volume = MUSIC_VOLUME
        self._load_sounds()
        
    def _load_sounds(self):
        """
        Загрузка звуковых эффектов из директории assets/sounds
        """
        sound_files = {
            'button_click': 'click.wav',
            'success': 'success.wav',
            'error': 'error.wav',
            'level_complete': 'complete.wav',
            'achievement': 'achievement.wav',
            'star': 'star.wav'
        }
        
        # Директория со звуками
        sound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sounds')
        
        # Загрузка звуков
        for sound_name, file_name in sound_files.items():
            sound_path = os.path.join(sound_dir, file_name)
            if os.path.exists(sound_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    # Установка громкости по умолчанию
                    self.sounds[sound_name].set_volume(self.sound_volume)
                except Exception as e:
                    print(f"Ошибка загрузки звука {file_name}: {e}")
            else:
                print(f"Предупреждение: звуковой файл {sound_path} не найден")
                
    def play_sound(self, sound_name):
        """
        Воспроизведение звукового эффекта
        
        Args:
            sound_name: имя звукового эффекта из звуковой библиотеки
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def play_music(self, music_name):
        """
        Воспроизведение фоновой музыки
        
        Args:
            music_name: имя музыкального файла без расширения
        """
        music_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sounds')
        music_path = os.path.join(music_dir, f"{music_name}.mp3")
        
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Проигрывание в цикле
            except Exception as e:
                print(f"Ошибка загрузки музыки {music_name}: {e}")
        else:
            print(f"Предупреждение: музыкальный файл {music_path} не найден")
            
    def stop_music(self):
        """
        Остановка музыки
        """
        pygame.mixer.music.stop()
        
    def set_sound_volume(self, volume):
        """
        Установка громкости звуковых эффектов
        
        Args:
            volume: значение от 0.0 до 1.0
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        # Обновляем громкость для всех звуков
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
        
    def set_music_volume(self, volume):
        """
        Установка громкости фоновой музыки
        
        Args:
            volume: значение от 0.0 до 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
