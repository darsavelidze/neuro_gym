    def start(self):
        """
        Запуск основного игрового цикла
        """
        # Начинаем с экрана загрузки
        self.screen_manager.go_to('loading')
        
        # Устанавливаем флаг работы игры
        self.running = True
        
        # Основной игровой цикл
        while self.running:
            # Фиксируем время кадра
            dt = self.clock.tick(FPS) / 1000.0  # переводим в секунды
            
            # Получаем текущий экран
            current_screen = self.screen_manager.get_current_screen()
            if not current_screen:
                print("Ошибка: текущий экран не найден")
                break
            
            # Обрабатываем события
            events = pygame.event.get()
            self._process_events(events, current_screen)
            
            # Если игра остановлена, выходим из цикла
            if not self.running:
                break
                
            # Обновляем текущий экран
            current_screen.update(dt)
            
            # Отрисовываем текущий экран
            current_screen.draw()
            
            # Отрисовка диалогового окна камеры, если оно активно
            if self.camera_controller.dialog and self.camera_controller.dialog['active']:
                self.camera_controller.draw_dialog(
                    self.screen,
                    self.screen_manager.get_current_screen().fonts['MEDIUM'],
                    self.localization_manager.get_language()
                )
            
            # Обновляем экран
            pygame.display.flip()
        
        # Завершение игры
        self._cleanup()
        
    def _process_events(self, events, current_screen):
        """
        Обработка событий pygame
        
        Args:
            events: список событий pygame
            current_screen: текущий активный экран
        """
        # Координаты курсора для жестов или мыши
        cursor_pos = self.input_handler.get_cursor_position()
        
        # Проверка событий
        for event in events:
            # Выход из приложения
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            # Пользовательское событие для обратного вызова (используется в camera_controller)
            elif event.type == pygame.USEREVENT and 'callback' in event.dict:
                event.dict['callback']()
            
            # Нажатие кнопки мыши
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Если активно диалоговое окно контроллера камеры, обрабатываем его
                if self.camera_controller.dialog and self.camera_controller.dialog['active']:
                    self.camera_controller.handle_dialog_click(event.pos)
                else:
                    # Иначе передаем событие текущему экрану
                    current_screen.handle_events([event], cursor_pos)
            
            # Другие события, которые не требуют специальной обработки, передаем текущему экрану
            else:
                current_screen.handle_events([event], cursor_pos)
                
    def _cleanup(self):
        """
        Очистка ресурсов перед завершением игры
        """
        # Сохраняем прогресс
        self.progress_manager.save_progress()
        
        # Завершаем работу pygame
        pygame.quit()
        sys.exit()
