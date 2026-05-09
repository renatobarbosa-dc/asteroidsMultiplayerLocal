"""Client-side rendering (pygame)."""

import pygame as pg

from core import config as C
from core.entities import Asteroid, Bullet, PowerUp, Ship, UFO, BlackHole
from core.scene import SceneState


class Renderer:
    """Draws scenes and entities without coupling game rules to Game."""

    def __init__(
        self,
        screen: pg.Surface,
        config: object = C,
        fonts: dict[str, pg.font.Font] | None = None,
    ) -> None:
        self.screen = screen
        self.config = config
        safe_fonts = fonts or {}
        self.font = safe_fonts["font"]
        self.big = safe_fonts["big"]

        self._draw_dispatch: dict[type, callable] = {
            Bullet: self._draw_bullet,
            Asteroid: self._draw_asteroid,
            PowerUp: self._draw_powerup,
            Ship: self._draw_ship,
            UFO: self._draw_ufo,
            BlackHole: self._draw_black_hole,
        }

    def clear(self) -> None:
        self.screen.fill(self.config.BLACK)

    def draw_world(self, world: object) -> None:
        sprites = getattr(world, "all_sprites", [])
        for sprite in sprites:
            drawer = self._draw_dispatch.get(type(sprite))
            if drawer is not None:
                drawer(sprite)

    def draw_hud(
        self,
        score: int,
        lives: int,
        wave: int,
        state: SceneState,
        double_shot_time: float = 0.0,
        shield_time: float = 0.0,
        shield_cool: float = 0.0,
        time_stop_timer: float = 0.0,
        time_stop_cool: float = 0.0,
        ship=None,
    ) -> None:
        if state != SceneState.PLAY:
            return

        text = f"SCORE {score:06d}   LIVES {lives}   WAVE {wave}"
        label = self.font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (10, 10))

        bar_w = 180
        bar_h = 10
        bar_x = self.config.WIDTH - 250

        if double_shot_time > 0.0:
            max_time = float(self.config.DOUBLE_SHOT_DURATION)
            ratio = min(1.0, max(0.0, double_shot_time / max_time))

            info = self.font.render(
                f"DOUBLE SHOT {double_shot_time:0.1f}s",
                True,
                self.config.WHITE,
            )
            self.screen.blit(info, (bar_x, 10))

            border = pg.Rect(bar_x, 40, bar_w, bar_h)
            fill = pg.Rect(bar_x, 40, int(bar_w * ratio), bar_h)
            pg.draw.rect(self.screen, self.config.WHITE, border, width=1)
            if fill.width > 0:
                pg.draw.rect(self.screen, self.config.WHITE, fill, width=0)

        if ship:
            ratio = ship.special_energy / self.config.SPECIAL_MAX
            x = 10
            y = 60
            w = 150
            h = 8

            special_label = "SPECIAL"
            if ratio >= 1.0:
                special_label = "FULL SPECIAL"

            label = self.font.render(special_label, True, self.config.WHITE)
            self.screen.blit(label, (x, y - 20))

            border = pg.Rect(x, y, w, h)
            fill = pg.Rect(x, y, int(w * ratio), h)
            pg.draw.rect(self.screen, self.config.WHITE, border, 1)
            if fill.width > 0:
                pg.draw.rect(self.screen, self.config.WHITE, fill)

            border = pg.Rect(x, y, w, h)
            fill = pg.Rect(x, y, int(w * ratio), h)
            pg.draw.rect(self.screen, self.config.WHITE, border, 1)
            if fill.width > 0:
                pg.draw.rect(self.screen, self.config.WHITE, fill)

        if shield_time > 0.0:
            shield_label = f"SHIELD ACTIVE {shield_time:0.1f}s"
            shield_ratio = min(
                1.0, max(0.0, shield_time / self.config.SHIP_SHIELD_DURATION)
            )
        elif shield_cool > 0.0:
            shield_label = f"SHIELD COOLDOWN {shield_cool:0.1f}s"
            total_cool = (
                self.config.SHIP_SHIELD_DURATION + self.config.SHIP_SHIELD_COOLDOWN
            )
            shield_ratio = 1.0 - min(1.0, max(0.0, shield_cool / total_cool))
        else:
            shield_label = "SHIELD READY"
            shield_ratio = 1.0

        shield_y = 56 if double_shot_time > 0.0 else 10
        shield_info = self.font.render(shield_label, True, self.config.WHITE)
        self.screen.blit(shield_info, (bar_x, shield_y))

        shield_border = pg.Rect(bar_x, shield_y + 30, bar_w, bar_h)
        shield_fill = pg.Rect(bar_x, shield_y + 30, int(bar_w * shield_ratio), bar_h)
        pg.draw.rect(self.screen, self.config.WHITE, shield_border, width=1)
        if shield_fill.width > 0:
            pg.draw.rect(self.screen, self.config.WHITE, shield_fill, width=0)

        if time_stop_timer > 0.0:
            ts_label = f"TIME STOP {time_stop_timer:.1f}s"
            ts_ratio = min(1.0, time_stop_timer / self.config.TIME_STOP_DURATION)
            ts_color = self.config.WHITE
        elif time_stop_cool > 0.0:
            ts_label = f"TIME STOP CD {time_stop_cool:.1f}s"
            total = self.config.TIME_STOP_DURATION + self.config.TIME_STOP_COOLDOWN
            ts_ratio = 1.0 - min(1.0, time_stop_cool / total)
            ts_color = self.config.WHITE
        else:
            ts_label = "TIME STOP READY"
            ts_ratio = 1.0
            ts_color = self.config.WHITE

        ts_y = shield_y + 56
        self.screen.blit(self.font.render(ts_label, True, ts_color), (bar_x, ts_y))
        ts_border = pg.Rect(bar_x, ts_y + 30, bar_w, bar_h)
        ts_fill = pg.Rect(bar_x, ts_y + 30, int(bar_w * ts_ratio), bar_h)
        pg.draw.rect(self.screen, ts_color, ts_border, width=1)
        if ts_fill.width > 0:
            pg.draw.rect(self.screen, ts_color, ts_fill)

    def draw_menu(self) -> None:
        self._draw_text(
            self.big,
            "ASTEROIDS",
            self.config.WIDTH // 2 - 170,
            130,
        )
        self._draw_text(
            self.font,
            "(Press any key to start)",
            self.config.WIDTH // 2 - 170,
            220,
        )
        self._draw_text(
            self.font,
            "Move: W/UP | Turn: A,D or LEFT,RIGHT | Shoot: SPACE",
            self.config.WIDTH // 2 - 330,
            290,
        )
        self._draw_text(
            self.font,
            "Shield: E | Hyperspace: LSHIFT | Time Stop: Q",
            self.config.WIDTH // 2 - 290,
            325,
        )
        self._draw_text(
            self.font,
            "Double Shot is a pickup (diamond on map)",
            self.config.WIDTH // 2 - 260,
            360,
        )

    def draw_game_over(self) -> None:
        self._draw_text(
            self.big,
            "GAME OVER",
            self.config.WIDTH // 2 - 170,
            260,
        )
        self._draw_text(
            self.font,
            "(Press any key to play again)",
            self.config.WIDTH // 2 - 200,
            340,
        )

    def _draw_text(
        self,
        font: pg.font.Font,
        text: str,
        x: int,
        y: int,
    ) -> None:
        label = font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (x, y))

    def _draw_bullet(self, bullet: Bullet) -> None:
        center = (int(bullet.pos.x), int(bullet.pos.y))
        pg.draw.circle(
            self.screen,
            self.config.WHITE,
            center,
            bullet.r,
            width=1,
        )

    def _draw_asteroid(self, asteroid: Asteroid) -> None:
        points = []
        for point in asteroid.poly:
            px = int(asteroid.pos.x + point.x)
            py = int(asteroid.pos.y + point.y)
            points.append((px, py))
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

    def _draw_ship(self, ship: Ship) -> None:
        p1, p2, p3 = ship.ship_points()
        points = [
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)),
            (int(p3.x), int(p3.y)),
        ]
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

        if ship.has_active_shield():
            center = (int(ship.pos.x), int(ship.pos.y))
            pulse = 8 + int(ship.shield_time * 6) % 3
            pg.draw.circle(
                self.screen,
                self.config.WHITE,
                center,
                ship.r + pulse,
                width=1,
            )

        if ship.invuln > 0.0 and int(ship.invuln * 10) % 2 == 0:
            center = (int(ship.pos.x), int(ship.pos.y))
            pg.draw.circle(
                self.screen,
                self.config.WHITE,
                center,
                ship.r + 6,
                width=1,
            )

    def _draw_ufo(self, ufo: UFO) -> None:
        width = ufo.r * 2
        height = ufo.r

        body = pg.Rect(0, 0, width, height)
        body.center = (int(ufo.pos.x), int(ufo.pos.y))
        pg.draw.ellipse(self.screen, self.config.WHITE, body, width=1)

        cup = pg.Rect(0, 0, int(width * 0.5), int(height * 0.7))
        cup.center = (int(ufo.pos.x), int(ufo.pos.y - height * 0.3))
        pg.draw.ellipse(self.screen, self.config.WHITE, cup, width=1)

    def _draw_black_hole(self, bh: BlackHole):
        # BLACK HOLE AURA
        pg.draw.circle(self.screen, C.DARK_PURPLE, bh.pos, bh.visual_r)
        # BLACK HOLE RING
        pg.draw.circle(self.screen, C.VIOLET, bh.pos, bh.visual_r - 4, 2)
        # BLACK HOLE CENTER
        pg.draw.circle(self.screen, C.BLACK, bh.pos, bh.r)

    def _draw_powerup(self, powerup: PowerUp) -> None:
        center = (int(powerup.pos.x), int(powerup.pos.y))
        r = powerup.r
        if powerup.kind == "repair":
            # círculo + cruz
            pg.draw.circle(self.screen, self.config.GREEN, center, r, 1)
            pg.draw.line(
                self.screen,
                self.config.GREEN,
                (center[0], center[1] - r),
                (center[0], center[1] + r),
                2,
            )
            pg.draw.line(
                self.screen,
                self.config.GREEN,
                (center[0] - r, center[1]),
                (center[0] + r, center[1]),
                2,
            )

        elif powerup.kind == "orb":
            pg.draw.circle(self.screen, self.config.PURPLE, center, r, 1)

        else:
            points = [
                (center[0], center[1] - r),
                (center[0] + r, center[1]),
                (center[0], center[1] + r),
                (center[0] - r, center[1]),
            ]
            pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)
