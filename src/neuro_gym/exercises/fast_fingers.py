"""Упражнение "Ловкие пальчики" с разделением модели и рендера."""

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pygame

from .base_exercise import BaseExercise
from ..config import COLORS
from ..core.exercise_config import get_exercise_setting


Color = Tuple[int, int, int]


@dataclass
class SpawnedObject:
    type: str
    x: int
    y: int
    size: int
    color: Color
    timer: float
    animation: float = 1.0
    state: str = "appearing"
    hit: bool = False


@dataclass
class HitEffect:
    x: int
    y: int
    color: Color
    duration: float = 0.3
    max_size: int = 50


@dataclass
class FastFingersSettings:
    appear_time: float
    max_objects: int
    object_types: List[str]
    spawn_interval: float
    target_score: int


class FastFingersModel:
    """Чистая модель состояния без рендера."""

    def __init__(self, width: int, height: int, settings: FastFingersSettings):
        self.width = width
        self.height = height
        self.settings = settings
        self.reset()

    def reset(self) -> None:
        self.objects: List[SpawnedObject] = []
        self.effects: List[HitEffect] = []
        self.object_timer = self.settings.spawn_interval
        self.hits = 0
        self.misses = 0
        self.combo = 0
        self.max_combo = 0

    def update(self, dt: float) -> None:
        self._spawn_if_needed(dt)
        self._update_objects(dt)
        self._update_effects(dt)

    def _spawn_if_needed(self, dt: float) -> None:
        self.object_timer -= dt
        if self.object_timer <= 0 and len(self.objects) < self.settings.max_objects:
            self.objects.append(self._generate_object())
            self.object_timer = self.settings.spawn_interval

    def _generate_object(self) -> SpawnedObject:
        base_size = random.randint(40, 60)
        margin = base_size * 2
        x, y = self._find_free_spot(base_size, margin)

        object_type = random.choice(self.settings.object_types)
        color = random.choice([
            COLORS['ACCENT_YELLOW'], COLORS['POSITIVE_GREEN'],
            COLORS['PRIMARY_BLUE'], COLORS['NEGATIVE_RED']
        ])

        return SpawnedObject(
            type=object_type,
            x=x,
            y=y,
            size=base_size,
            color=color,
            timer=self.settings.appear_time,
        )

    def _find_free_spot(self, base_size: int, margin: int) -> Tuple[int, int]:
        for _ in range(20):
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)
            if not any(self._overlaps(x, y, base_size, obj) for obj in self.objects):
                return x, y
        return (
            random.randint(margin, self.width - margin),
            random.randint(margin, self.height - margin),
        )

    @staticmethod
    def _overlaps(x: int, y: int, size: int, obj: SpawnedObject) -> bool:
        dx = x - obj.x
        dy = y - obj.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (size + obj.size)

    def _update_objects(self, dt: float) -> None:
        for obj in list(self.objects):
            if obj.state == 'appearing':
                obj.animation = min(1.0, obj.animation + dt * 3)
                if obj.animation >= 1.0:
                    obj.state = 'visible'
            elif obj.state == 'visible':
                obj.timer -= dt
                if obj.timer <= 0:
                    obj.state = 'disappearing'
                    obj.animation = 1.0
                    if not obj.hit:
                        self.misses += 1
                        self.combo = 0
            elif obj.state in ('disappearing', 'hit'):
                obj.animation = max(0.0, obj.animation - dt * 3)
                if obj.animation <= 0.0:
                    self.objects.remove(obj)

    def _update_effects(self, dt: float) -> None:
        for eff in list(self.effects):
            eff.duration -= dt
            if eff.duration <= 0:
                self.effects.remove(eff)

    def hit_test(self, pos: Tuple[int, int]) -> Optional[int]:
        for i, obj in enumerate(self.objects):
            if obj.state == 'visible' and not obj.hit:
                dx = pos[0] - obj.x
                dy = pos[1] - obj.y
                if math.sqrt(dx * dx + dy * dy) <= obj.size:
                    return i
        return None

    def register_hit(self, index: int) -> None:
        obj = self.objects[index]
        obj.hit = True
        obj.state = 'hit'
        self.hits += 1
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.effects.append(HitEffect(x=obj.x, y=obj.y, color=obj.color))

    def register_miss(self) -> None:
        self.misses += 1
        self.combo = 0


class FastFingersRenderer:
    """Изолированный рендерер, чтобы логику можно было тестировать отдельно."""

    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts

    def draw_objects(self, objects: List[SpawnedObject]) -> None:
        for obj in objects:
            self._draw_object(obj)

    def draw_effects(self, effects: List[HitEffect]) -> None:
        for effect in effects:
            self._draw_effect(effect)

    def _draw_object(self, obj: SpawnedObject) -> None:
        current_size = obj.size * obj.animation
        alpha = min(255, int(255 * obj.animation))
        color = obj.color[:3] + (alpha,)

        if obj.type == 'circle':
            self._draw_circle(obj, current_size, alpha, color)
        elif obj.type == 'square':
            self._draw_square(obj, current_size, alpha, color)
        elif obj.type == 'triangle':
            self._draw_triangle(obj, current_size, alpha, color)
        elif obj.type == 'star':
            self._draw_star(obj, current_size, alpha, color)
        elif obj.type == 'pentagon':
            self._draw_pentagon(obj, current_size, alpha, color)

    def _draw_circle(self, obj, current_size, alpha, color):
        if alpha > 100:
            shadow_alpha = int(alpha * 0.5)
            shadow_color = (0, 0, 0, shadow_alpha)
            pygame.draw.circle(self.screen, shadow_color, (obj.x + 3, obj.y + 3), current_size)
        pygame.draw.circle(self.screen, color, (obj.x, obj.y), current_size)
        if alpha > 100:
            highlight_size = current_size * 0.4
            highlight_x = obj.x - current_size * 0.3
            highlight_y = obj.y - current_size * 0.3
            pygame.draw.circle(self.screen, (255, 255, 255, alpha // 2), (highlight_x, highlight_y), highlight_size)

    def _draw_square(self, obj, current_size, alpha, color):
        half_size = current_size
        rect = pygame.Rect(obj.x - half_size, obj.y - half_size, half_size * 2, half_size * 2)
        if alpha > 100:
            shadow_rect = rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, (0, 0, 0, int(alpha * 0.5)), shadow_rect, border_radius=int(current_size * 0.2))
        pygame.draw.rect(self.screen, color, rect, border_radius=int(current_size * 0.2))
        if alpha > 100:
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width * 0.6, rect.height * 0.3)
            pygame.draw.rect(self.screen, (255, 255, 255, alpha // 2), highlight_rect, border_radius=int(current_size * 0.1))

    def _draw_triangle(self, obj, current_size, alpha, color):
        points = [
            (obj.x, obj.y - current_size),
            (obj.x - current_size, obj.y + current_size),
            (obj.x + current_size, obj.y + current_size)
        ]
        if alpha > 100:
            shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
            pygame.draw.polygon(self.screen, (0, 0, 0, int(alpha * 0.5)), shadow_points)
        pygame.draw.polygon(self.screen, color, points)
        if alpha > 100:
            highlight_points = [
                points[0],
                (points[0][0] - current_size * 0.5, points[0][1] + current_size * 0.5),
                (points[0][0] + current_size * 0.5, points[0][1] + current_size * 0.5)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), highlight_points)

    def _draw_star(self, obj, current_size, alpha, color):
        num_points = 5
        outer_radius = current_size
        inner_radius = current_size * 0.5
        points = []
        for i in range(num_points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = math.pi * i / num_points - math.pi / 2
            points.append((obj.x + radius * math.cos(angle), obj.y + radius * math.sin(angle)))
        if alpha > 100:
            shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
            pygame.draw.polygon(self.screen, (0, 0, 0, int(alpha * 0.5)), shadow_points)
        pygame.draw.polygon(self.screen, color, points)
        if alpha > 100:
            highlight_points = [points[0], points[9], points[1]]
            pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), highlight_points)

    def _draw_pentagon(self, obj, current_size, alpha, color):
        points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5 - math.pi / 2
            points.append((obj.x + current_size * math.cos(angle), obj.y + current_size * math.sin(angle)))
        if alpha > 100:
            shadow_points = [(p[0] + 3, p[1] + 3) for p in points]
            pygame.draw.polygon(self.screen, (0, 0, 0, int(alpha * 0.5)), shadow_points)
        pygame.draw.polygon(self.screen, color, points)
        if alpha > 100:
            highlight_points = [
                points[0],
                ((points[0][0] + points[4][0]) // 2, (points[0][1] + points[4][1]) // 2),
                ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
            ]
            pygame.draw.polygon(self.screen, (255, 255, 255, alpha // 2), highlight_points)

    def _draw_effect(self, effect: HitEffect):
        progress = 1 - (effect.duration / 0.3)
        current_size = effect.max_size * progress
        alpha = int(255 * (1 - progress))
        color = effect.color[:3] + (alpha,)
        pygame.draw.circle(self.screen, color, (effect.x, effect.y), current_size, width=2)


class FastFingers(BaseExercise):
    exercise_id = 'fast_fingers'

    def __init__(self, screen_manager, screen, difficulty='Легкий'):
        super().__init__(screen_manager, screen, difficulty)
        self.settings = self._load_settings(difficulty)
        self.model = FastFingersModel(self.width, self.height, self.settings)
        self.renderer = FastFingersRenderer(self.screen, self.fonts)

    def _load_settings(self, difficulty: str) -> FastFingersSettings:
        return FastFingersSettings(
            appear_time=get_exercise_setting(self.exercise_id, difficulty, 'appear_time', 2.0),
            max_objects=get_exercise_setting(self.exercise_id, difficulty, 'max_objects', 3),
            object_types=get_exercise_setting(self.exercise_id, difficulty, 'object_types', ['circle', 'square', 'triangle']),
            spawn_interval=get_exercise_setting(self.exercise_id, difficulty, 'spawn_interval', 1.0),
            target_score=get_exercise_setting(self.exercise_id, difficulty, 'target_score', 30),
        )

    def on_enter(self, params=None):
        super().on_enter(params)
        # Перечитываем настройки при смене сложности
        self.settings = self._load_settings(self.difficulty)
        self.model = FastFingersModel(self.width, self.height, self.settings)
        self.renderer = FastFingersRenderer(self.screen, self.fonts)

    @property
    def hits(self) -> int:
        return self.model.hits

    @property
    def misses(self) -> int:
        return self.model.misses

    @property
    def combo(self) -> int:
        return self.model.combo

    @property
    def max_combo(self) -> int:
        return self.model.max_combo

    @property
    def target_score(self) -> int:
        return self.settings.target_score

    def _calculate_final_score(self):
        base_score = int(self.hits * 2)
        miss_penalty = min(50, self.misses * 3)
        combo_bonus = self.max_combo * 2
        final_score = min(100, max(0, base_score - miss_penalty + combo_bonus))
        self.score = final_score

    def _exercise_specific_update(self, dt):
        self.model.update(dt)

    def _draw_exercise_area(self):
        self.renderer.draw_effects(self.model.effects)
        self.renderer.draw_objects(self.model.objects)

        if self.elapsed_time >= self.duration:
            loc = getattr(self, 'localization', None)
            good = loc.get_text('great_job') if loc else "Отличная работа!"
            time_over = loc.get_text('time_over') if loc else "Время вышло!"
            title = good if self.hits >= self.target_score else time_over

            hits_label = loc.get_text('hits') if loc else 'Попадания'
            misses_label = loc.get_text('misses') if loc else 'Промахи'
            max_combo_label = loc.get_text('max_combo') if loc else 'Макс. комбо'
            score_label = loc.get_text('score') if loc else 'Счёт'

            lines = [
                f"{hits_label}: {self.hits}   {misses_label}: {self.misses}   {max_combo_label}: {self.max_combo}",
                f"{score_label}: {self.score}"
            ]

            self.show_result_banner(title, lines, text_align='left')
        else:
            self.hide_result_banner()

    def _draw_extra_hud(self, y_start):
        loc = getattr(self, 'localization', None)
        hits_label = loc.get_text('hits') if loc else 'Попадания'
        combo_label = loc.get_text('combo') if loc else 'Комбо'
        target_label = loc.get_text('target') if loc else 'Цель'

        hits_text = self.fonts['MEDIUM'].render(
            f"{hits_label}: {self.hits}/{self.target_score} {target_label.lower() if target_label else ''}".strip(),
            True, COLORS['TEXT_DARK']
        )
        hits_rect = hits_text.get_rect(topleft=(20, y_start))
        self.screen.blit(hits_text, hits_rect)

        combo_text = self.fonts['MEDIUM'].render(f"{combo_label}: {self.combo}", True, COLORS['TEXT_DARK'])
        combo_rect = combo_text.get_rect(topleft=(20, hits_rect.bottom + 8))
        self.screen.blit(combo_text, combo_rect)

    def handle_events(self, events, cursor_pos=None):
        super().handle_events(events, cursor_pos)
        if self.is_paused or self.is_completed:
            return

        mouse_pos = cursor_pos if cursor_pos else self._get_cursor_position()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = event.pos if hasattr(event, 'pos') else mouse_pos
                self._process_hit(click_pos, count_miss=True)

        # Жестовое управление (hover-hit)
        if cursor_pos:
            self._process_hit(cursor_pos, count_miss=False)

    def _process_hit(self, pos, count_miss: bool):
        idx = self.model.hit_test(pos)
        if idx is not None:
            self.model.register_hit(idx)
        elif count_miss:
            self.model.register_miss()
