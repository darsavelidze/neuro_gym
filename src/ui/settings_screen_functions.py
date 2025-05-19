    def _back_to_main_menu(self):
        """
        Возврат в главное меню с сохранением настроек
        """
        # Воспроизводим звук нажатия кнопки
        self.sound_manager.play_sound('button_click')
        
        # Переходим в главное меню
        self.transition_to('main_menu')
