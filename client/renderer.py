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

    def draw_hud(self, world: object, state: SceneState) -> None:
        if state != SceneState.PLAY:
            return
        ships = getattr(world, "ships", {})
        if len(ships) <= 1:
            self._draw_hud_single(world)
        else:
            self._draw_hud_multi(world)

    def _draw_hud_single(self, world: object) -> None:
        ships = getattr(world, "ships", {})
        scores = getattr(world, "scores", {})
        lives = getattr(world, "lives", {})
        flags = getattr(world, "flags_collected", {})
        pid = min(ships.keys()) if ships else 1
        ship = ships.get(pid)
        score = int(scores.get(pid, 0))
        lives_n = int(lives.get(pid, 0))
        flags_n = int(flags.get(pid, 0))
        wave = int(getattr(world, "wave", 0))
        double_shot_time = ship.double_shot_time if ship else 0.0
        shield_time = ship.shield_time if ship else 0.0
        shield_cool = ship.shield_cool if ship else 0.0
        time_stop_timer = float(getattr(world, "time_stop_timer", 0.0))
        time_stop_cool = float(getattr(world, "time_stop_cool", 0.0))

        text = f"SCORE {score:06d}   LIVES {lives_n}   WAVE {wave}   BANDEIRAS {flags_n}/{self.config.FLAGS_TO_WIN}"
        self.screen.blit(self.font.render(text, True, self.config.WHITE), (10, 10))

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
            x, y, w = 10, 60, 150
            special_label = "FULL SPECIAL" if ratio >= 1.0 else "SPECIAL"
            self.screen.blit(
                self.font.render(special_label, True, self.config.WHITE),
                (x, y - 20),
            )
            border = pg.Rect(x, y, w, 8)
            fill = pg.Rect(x, y, int(w * ratio), 8)
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
        self.screen.blit(
            self.font.render(shield_label, True, self.config.WHITE),
            (bar_x, shield_y),
        )
        shield_border = pg.Rect(bar_x, shield_y + 30, bar_w, bar_h)
        shield_fill = pg.Rect(bar_x, shield_y + 30, int(bar_w * shield_ratio), bar_h)
        pg.draw.rect(self.screen, self.config.WHITE, shield_border, width=1)
        if shield_fill.width > 0:
            pg.draw.rect(self.screen, self.config.WHITE, shield_fill, width=0)

        if time_stop_timer > 0.0:
            ts_label = f"PARAR TEMPO {time_stop_timer:.1f}s"
            ts_ratio = min(1.0, time_stop_timer / self.config.TIME_STOP_DURATION)
        elif time_stop_cool > 0.0:
            ts_label = f"PARAR TEMPO CD {time_stop_cool:.1f}s"
            total = self.config.TIME_STOP_DURATION + self.config.TIME_STOP_COOLDOWN
            ts_ratio = 1.0 - min(1.0, time_stop_cool / total)
        else:
            ts_label = "PARAR TEMPO PRONTO"
            ts_ratio = 1.0

        ts_y = shield_y + 56
        self.screen.blit(
            self.font.render(ts_label, True, self.config.WHITE), (bar_x, ts_y)
        )
        ts_border = pg.Rect(bar_x, ts_y + 30, bar_w, bar_h)
        ts_fill = pg.Rect(bar_x, ts_y + 30, int(bar_w * ts_ratio), bar_h)
        pg.draw.rect(self.screen, self.config.WHITE, ts_border, width=1)
        if ts_fill.width > 0:
            pg.draw.rect(self.screen, self.config.WHITE, ts_fill)

    def _draw_hud_multi(self, world: object) -> None:
        # Mostrar timer ao invés de wave
        timer = float(getattr(world, "multiplayer_timer", 0.0))
        minutes = int(timer // 60)
        seconds = int(timer % 60)
        timer_text = f"TEMPO: {minutes}:{seconds:02d}"
        tw = self.font.render(timer_text, True, self.config.WHITE)
        cx = self.config.WIDTH // 2 - tw.get_width() // 2
        self.screen.blit(tw, (cx, 8))

        time_stop_timer = float(getattr(world, "time_stop_timer", 0.0))
        time_stop_cool = float(getattr(world, "time_stop_cool", 0.0))
        bar_w, bar_h = 200, 8
        bar_x = self.config.WIDTH // 2 - bar_w // 2
        if time_stop_timer > 0.0:
            ts_label = f"PARAR TEMPO {time_stop_timer:.1f}s"
            ts_ratio = min(1.0, time_stop_timer / self.config.TIME_STOP_DURATION)
        elif time_stop_cool > 0.0:
            ts_label = f"PARAR TEMPO CD {time_stop_cool:.1f}s"
            total = self.config.TIME_STOP_DURATION + self.config.TIME_STOP_COOLDOWN
            ts_ratio = 1.0 - min(1.0, time_stop_cool / total)
        else:
            ts_label = "PARAR TEMPO PRONTO"
            ts_ratio = 1.0

        ts_y = 36
        self.screen.blit(self.font.render(ts_label, True, self.config.WHITE), (bar_x, ts_y))
        ts_border = pg.Rect(bar_x, ts_y + 22, bar_w, bar_h)
        ts_fill = pg.Rect(bar_x, ts_y + 22, int(bar_w * ts_ratio), bar_h)
        pg.draw.rect(self.screen, self.config.WHITE, ts_border, width=1)
        if ts_fill.width > 0:
            pg.draw.rect(self.screen, self.config.WHITE, ts_fill)

        ships = getattr(world, "ships", {})
        scores = getattr(world, "scores", {})
        lives = getattr(world, "lives", {})
        flags = getattr(world, "flags_collected", {})
        kills = getattr(world, "kills", {})
        corners = [
            (12, 72),
            (self.config.WIDTH - 248, 72),
            (12, self.config.HEIGHT - 88),
            (self.config.WIDTH - 248, self.config.HEIGHT - 88),
        ]
        bar_mini_w = 130
        bar_mini_h = 5
        for idx, pid in enumerate(sorted(ships.keys())):
            ship = ships[pid]
            col = getattr(ship, "color", self.config.WHITE)
            x, y = corners[idx] if idx < len(corners) else (12, 72)
            sc = int(scores.get(pid, 0))
            lv = int(lives.get(pid, 0))
            fl = int(flags.get(pid, 0))
            kl = int(kills.get(pid, 0))
            # No multiplayer, vidas são infinitas, então mostramos só score, bandeiras e kills
            line = self.font.render(f"P{pid}  {sc:06d}  🚩{fl}  ☠{kl}", True, col)
            self.screen.blit(line, (x, y))
            ratio = min(1.0, max(0.0, ship.special_energy / self.config.SPECIAL_MAX))
            by = y + 26
            border = pg.Rect(x, by, bar_mini_w, bar_mini_h)
            fill = pg.Rect(x, by, int(bar_mini_w * ratio), bar_mini_h)
            pg.draw.rect(self.screen, col, border, width=1)
            if fill.width > 0:
                pg.draw.rect(self.screen, col, fill)

    def draw_menu(self) -> None:
        self._draw_text(
            self.big,
            "ASTEROIDS",
            self.config.WIDTH // 2 - 170,
            120,
        )
        self._draw_text(
            self.font,
            "ENTER — escolher quantos jogadores (teclado)",
            self.config.WIDTH // 2 - 320,
            210,
        )
        self._draw_text(
            self.font,
            "Mandos (ex.: PlayStation) serão suportados numa atualização futura.",
            self.config.WIDTH // 2 - 420,
            250,
        )
        self._draw_text(
            self.font,
            "Qualquer outra tecla também abre o menu de jogadores",
            self.config.WIDTH // 2 - 360,
            290,
        )
        self._draw_text(
            self.font,
            "ESC — sair",
            self.config.WIDTH // 2 - 80,
            330,
        )

    def draw_player_select(self, highlight: int) -> None:
        self._draw_text(
            self.big,
            "JOGADORES",
            self.config.WIDTH // 2 - 160,
            100,
        )
        h = max(1, min(4, int(highlight)))
        y0 = 220
        for n in range(1, 5):
            prefix = ">" if n == h else " "
            col = self.config.PLAYER_COLORS.get(n, self.config.WHITE)
            line = f"{prefix}  {n} jogador{'es' if n != 1 else ''}"
            surf = self.font.render(line, True, col if n == h else self.config.GRAY)
            self.screen.blit(surf, (self.config.WIDTH // 2 - 120, y0 + (n - 1) * 40))

        self._draw_text(
            self.font,
            "Tecla 1, 2, 3 ou 4 — começar já   |   SETAS + ENTER — confirmar",
            self.config.WIDTH // 2 - 380,
            420,
        )
        self._draw_text(
            self.font,
            "ESC — voltar ao menu inicial",
            self.config.WIDTH // 2 - 180,
            460,
        )

    def draw_game_over(self, world: object = None) -> None:
        winner_id = getattr(world, "winner_id", None) if world else None
        is_multiplayer = getattr(world, "is_multiplayer", False) if world else False
        flags = getattr(world, "flags_collected", {}) if world else {}
        kills = getattr(world, "kills", {}) if world else {}
        
        if winner_id is not None:
            player_color = self.config.PLAYER_COLORS.get(winner_id, self.config.WHITE)
            title = f"JOGADOR {winner_id} VENCEU!"
            title_surf = self.big.render(title, True, player_color)
            self._draw_text(
                self.big,
                title,
                self.config.WIDTH // 2 - title_surf.get_width() // 2,
                200,
            )
            
            # Verificar se foi por bandeiras ou por kills
            winner_flags = flags.get(winner_id, 0)
            winner_kills = kills.get(winner_id, 0)
            
            if winner_flags >= self.config.FLAGS_TO_WIN:
                reason = f"Coletou {self.config.FLAGS_TO_WIN} bandeiras! 🚩"
            else:
                reason = f"Mais kills: {winner_kills} ☠"
            
            self._draw_text(
                self.font,
                reason,
                self.config.WIDTH // 2 - 150,
                280,
            )
            
        elif is_multiplayer and winner_id is None:
            # Empate no multiplayer
            self._draw_text(
                self.big,
                "EMPATE!",
                self.config.WIDTH // 2 - 120,
                220,
            )
            
            # Mostrar estatísticas dos jogadores
            if kills:
                y_offset = 290
                for pid in sorted(kills.keys()):
                    col = self.config.PLAYER_COLORS.get(pid, self.config.WHITE)
                    kl = kills.get(pid, 0)
                    stat_line = f"P{pid}: {kl} kills"
                    self._draw_text(
                        self.font,
                        stat_line,
                        self.config.WIDTH // 2 - 80,
                        y_offset,
                    )
                    y_offset += 30
        else:
            # Game over normal (single player)
            self._draw_text(
                self.big,
                "GAME OVER",
                self.config.WIDTH // 2 - 170,
                260,
            )
        
        self._draw_text(
            self.font,
            "(Qualquer tecla — voltar ao menu de jogadores)",
            self.config.WIDTH // 2 - 320,
            self.config.HEIGHT - 80,
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
        col = getattr(ship, "color", self.config.WHITE)
        pg.draw.polygon(self.screen, col, points, width=1)

        if ship.has_active_shield():
            center = (int(ship.pos.x), int(ship.pos.y))
            pulse = 8 + int(ship.shield_time * 6) % 3
            pg.draw.circle(
                self.screen,
                col,
                center,
                ship.r + pulse,
                width=1,
            )

        if ship.invuln > 0.0 and int(ship.invuln * 10) % 2 == 0:
            center = (int(ship.pos.x), int(ship.pos.y))
            pg.draw.circle(
                self.screen,
                col,
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

        elif powerup.kind == "flag":
            # Bandeira: haste + bandeira triangular
            pole_bottom = (center[0] - r, center[1] + r)
            pole_top = (center[0] - r, center[1] - r)
            # Haste
            pg.draw.line(self.screen, self.config.YELLOW, pole_bottom, pole_top, 2)
            # Bandeira triangular
            flag_points = [
                pole_top,
                (center[0] + r, center[1] - r // 2),
                (center[0] - r, center[1]),
            ]
            pg.draw.polygon(self.screen, self.config.ORANGE, flag_points, width=1)

        else:
            points = [
                (center[0], center[1] - r),
                (center[0] + r, center[1]),
                (center[0], center[1] + r),
                (center[0] - r, center[1]),
            ]
            pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)