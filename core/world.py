"""Game systems (World, waves, score)."""

import math
from random import uniform
from typing import Dict

import pygame as pg

from core import config as C
from core.collisions import CollisionManager
from core.commands import PlayerCommand
from core.entities import Asteroid, BlackHole, PowerUp, Ship, UFO
from core.utils import Vec, rand_edge_pos

PlayerId = int


class World:
    """World state and game rules.

    Multiplayer-ready:
    - World receives commands indexed by player_id.
    - World generates events (strings) for the client (sounds/effects).
    """

    def __init__(self, player_count: int = 1) -> None:
        self.player_count = max(1, min(C.MAX_PLAYERS, int(player_count)))
        self.ships: Dict[PlayerId, Ship] = {}
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

        self.scores: Dict[PlayerId, int] = {}
        self.lives: Dict[PlayerId, int] = {}
        self.flags_collected: Dict[PlayerId, int] = {}
        self.kills: Dict[PlayerId, int] = {}  # Contador de kills (UFOs + jogadores)
        self.asteroid_destroys: Dict[PlayerId, int] = {}
        self.powerup_pickups: Dict[PlayerId, int] = {}
        self.player_spawn_positions: Dict[PlayerId, Vec] = {}
        self.wave = 0
        self.wave_cool = float(C.WAVE_DELAY)
        self.ufo_timer = float(C.UFO_SPAWN_EVERY)

        # Timer para modo multiplayer (só ativo quando player_count > 1)
        self.multiplayer_timer = float(C.MULTIPLAYER_TIMER_SECONDS) if player_count > 1 else 0.0
        self.is_multiplayer = player_count > 1

        self.black_hole = None
        # blackhole spawn period
        self.bh_timer = uniform(C.BH_TIMER_MIN, C.BH_TIMER_MAX)
        self.bh_duration = 0

        self.events: list[str] = []
        self._collision_mgr = CollisionManager(is_multiplayer=player_count > 1)

        self.game_over = False
        self.winner_id: PlayerId | None = None
        self.ended_by_time = False
        self.victory_reason: str = ""

        for pid in range(1, self.player_count + 1):
            self.spawn_player(pid)

    def begin_frame(self) -> None:
        self.events.clear()

    def reset(self, player_count: int | None = None) -> None:
        """Recomeça o mundo; opcionalmente altera o número de jogadores."""
        n = self.player_count if player_count is None else player_count
        self.__init__(n)

    def _spawn_screen_pad(self) -> float:
        """Distância mínima à borda para a nave inteira ficar visível no ecrã."""
        return float(C.SHIP_RADIUS) * 2.5 + 48.0

    def _clamp_pos_to_screen(self, pos: Vec) -> Vec:
        pad = self._spawn_screen_pad()
        w, h = float(C.WIDTH), float(C.HEIGHT)
        return Vec(max(pad, min(w - pad, pos.x)), max(pad, min(h - pad, pos.y)))

    def _spawn_pos_for_player(self, player_id: PlayerId) -> Vec:
        w, h = float(C.WIDTH), float(C.HEIGHT)
        cx, cy = w / 2, h / 2
        if self.player_count <= 1:
            return self._clamp_pos_to_screen(Vec(cx, cy))

        # Posições no interior (quadrantes / metades), não coladas ao canto físico.
        if self.player_count == 2:
            raw = {
                1: Vec(w * 0.28, cy),
                2: Vec(w * 0.72, cy),
            }
        elif self.player_count == 3:
            raw = {
                1: Vec(w * 0.28, h * 0.32),
                2: Vec(cx, h * 0.62),
                3: Vec(w * 0.72, h * 0.32),
            }
        else:
            raw = {
                1: Vec(w * 0.28, h * 0.28),
                2: Vec(w * 0.72, h * 0.28),
                3: Vec(w * 0.28, h * 0.72),
                4: Vec(w * 0.72, h * 0.72),
            }

        pos = raw.get(player_id, Vec(cx, cy))
        return self._clamp_pos_to_screen(pos)

    def spawn_player(self, player_id: PlayerId) -> None:
        pos = self._spawn_pos_for_player(player_id)
        self.player_spawn_positions[player_id] = Vec(pos)
        ship = Ship(player_id, pos)
        ship.invuln = float(C.SAFE_SPAWN_TIME)

        self.ships[player_id] = ship
        self.scores[player_id] = 0
        self.lives[player_id] = C.START_LIVES
        self.flags_collected[player_id] = 0
        self.kills[player_id] = 0
        self.asteroid_destroys[player_id] = 0
        self.powerup_pickups[player_id] = 0
        self.all_sprites.add(ship)

    def get_ship(self, player_id: PlayerId) -> Ship | None:
        return self.ships.get(player_id)

    def start_wave(self) -> None:
        self.wave += 1
        count = C.WAVE_BASE_COUNT + self.wave

        ship_positions = [s.pos for s in self.ships.values()]

        for _ in range(count):
            pos = rand_edge_pos()
            while any(
                (pos - sp).length() < C.AST_MIN_SPAWN_DIST for sp in ship_positions
            ):
                pos = rand_edge_pos()

            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str) -> None:
        ast = Asteroid(pos, vel, size)
        self.asteroids.add(ast)
        self.all_sprites.add(ast)

    def spawn_ufo(self) -> None:
        small = uniform(0, 1) < 0.5
        pos = rand_edge_pos()
        target = self._get_nearest_ship_pos(pos)
        ufo = UFO(pos, small, target_pos=target)
        self.ufos.add(ufo)

        self.all_sprites.add(ufo)

    def spawn_powerup(self, pos: Vec, kind: str) -> None:
        powerup = PowerUp(pos, kind)
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)

    def spawn_black_hole(self) -> None:
        """Cria buraco negro longe de todas as naves."""
        pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        while any((pos - s.pos).length() < 200 for s in self.ships.values()):
            pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))

        bh = BlackHole(pos)
        self.black_hole = bh
        self.all_sprites.add(bh)
        self.bh_duration = uniform(C.BH_DURATION_MIN, C.BH_DURATION_MAX)

    def _update_blackhole(self, dt: float) -> None:
        """Um passo global de temporizador + gravidade em todas as naves."""
        if self.black_hole:
            self.bh_duration -= dt
            if self.bh_duration <= 0:
                self.black_hole.kill()
                self.black_hole = None
                self.bh_timer = uniform(10, 20)
        else:
            self.bh_timer -= dt
            if self.bh_timer <= 0:
                self.spawn_black_hole()

        if not self.black_hole:
            return

        for ship in self.ships.values():
            dir_vec = self.black_hole.pos - ship.pos
            dist = dir_vec.length()
            if dist <= 0:
                continue
            dir_vec = dir_vec.normalize()
            force = self.black_hole.strength / (dist + 1)
            ship.vel += dir_vec * force * dt * 50

    def update(
        self,
        dt: float,
        commands_by_player_id: Dict[PlayerId, PlayerCommand],
    ) -> None:
        self.begin_frame()

        if self.game_over:
            return

        enemy_dt = dt

        self._apply_commands(dt, commands_by_player_id)

        for ship in self.ships.values():
            created = ship.update(dt)
            if created:
                self.bullets.add(*created)
                self.all_sprites.add(*created)

        self._update_blackhole(dt)
        for bullet in self.bullets:
            bullet.update(dt)
        for ast in self.asteroids:
            ast.update(enemy_dt)
        for powerup in self.powerups:
            powerup.update(dt)

        if self.player_count == 1:
            self._update_ufos(enemy_dt)
            self._update_timers(dt)

        self._handle_collisions()
        self._collect_powerups()
        
        if self.is_multiplayer:
            self._update_multiplayer_mode(dt)
        else:
            self._maybe_start_next_wave(dt)

    def _apply_commands(
        self,
        dt: float,
        commands_by_player_id: Dict[PlayerId, PlayerCommand],
    ) -> None:
        for player_id, cmd in commands_by_player_id.items():
            ship = self.get_ship(player_id)
            if ship is None:
                continue

            if cmd.shield and ship.try_activate_shield():
                self.events.append("shield_on")

            if cmd.hyperspace:
                ship.hyperspace()
                self.scores[player_id] = max(
                    0, self.scores[player_id] - C.HYPERSPACE_COST
                )
                self.events.append("hyperspace")

            created_bullets = ship.apply_command(cmd, dt, self.bullets)
            if created_bullets:
                self.bullets.add(*created_bullets)
                self.all_sprites.add(*created_bullets)
                self.events.append("player_shoot")

            if cmd.special:
                created = ship.try_activate_special(self.bullets)
                if created:
                    self.bullets.add(*created)
                    self.all_sprites.add(*created)
                    self.events.append("player_shoot")

    def _update_ufos(self, dt: float) -> None:
        for ufo in list(self.ufos):
            ufo.target_pos = self._get_nearest_ship_pos(ufo.pos)
            ufo.update(dt)
            if not ufo.alive():
                continue

            ufo.target_pos = self._get_nearest_ship_pos(ufo.pos)
            bullet = ufo.try_fire()
            if bullet is not None:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.events.append("ufo_shoot")

            if not ufo.alive():
                self.ufos.remove(ufo)

    def _get_nearest_ship_pos(self, from_pos: Vec) -> Vec | None:
        """Return position of the nearest living ship to from_pos."""
        nearest = None
        min_dist = float("inf")
        for ship in self.ships.values():
            d = (ship.pos - from_pos).length()
            if d < min_dist:
                min_dist = d
                nearest = ship
        return nearest.pos if nearest else None

    def _update_timers(self, dt: float) -> None:
        self.ufo_timer -= dt
        if self.ufo_timer <= 0.0:
            self.spawn_ufo()
            self.ufo_timer = float(C.UFO_SPAWN_EVERY)

    def _maybe_start_next_wave(self, dt: float) -> None:
        if self.asteroids:
            return

        self.wave_cool -= dt
        if self.wave_cool <= 0.0:
            self.start_wave()
            self.wave_cool = float(C.WAVE_DELAY)

    def _update_multiplayer_mode(self, dt: float) -> None:
        """Gerencia timer e spawning contínuo em modo multiplayer."""
        # Decrementar timer
        if self.multiplayer_timer > 0.0:
            self.multiplayer_timer -= dt
            
            # Timer acabou - determinar vencedor
            if self.multiplayer_timer <= 0.0:
                self.multiplayer_timer = 0.0
                self._end_multiplayer_by_timer()
                return
        
        # Spawnar asteroides continuamente (não por waves)
        # Manter sempre entre 4-8 asteroides no campo
        asteroid_count = len(self.asteroids)
        target_asteroids = 6
        
        if asteroid_count < target_asteroids:
            # Spawnar novos asteroides
            ship_positions = [s.pos for s in self.ships.values()]
            
            for _ in range(target_asteroids - asteroid_count):
                pos = rand_edge_pos()
                # Garantir que não spawne muito perto de nenhum jogador
                attempts = 0
                while attempts < 20 and any(
                    (pos - sp).length() < C.AST_MIN_SPAWN_DIST for sp in ship_positions
                ):
                    pos = rand_edge_pos()
                    attempts += 1
                
                ang = uniform(0, math.tau)
                speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
                vel = Vec(math.cos(ang), math.sin(ang)) * speed
                
                # 60% Large, 30% Medium, 10% Small
                r = uniform(0, 1)
                if r < 0.6:
                    size = "L"
                elif r < 0.9:
                    size = "M"
                else:
                    size = "S"
                    
                self.spawn_asteroid(pos, vel, size)

    def _end_multiplayer_by_timer(self) -> None:
        """Fim do tempo: vence quem tem mais kills; empate → bandeiras → pontos."""
        self.game_over = True
        self.ended_by_time = True

        pids = sorted(self.ships.keys())
        if not pids:
            self.winner_id = None
            self.victory_reason = "timer_tie"
            return

        def ranking(pid: PlayerId) -> tuple[int, int, int]:
            return (
                int(self.kills.get(pid, 0)),
                int(self.flags_collected.get(pid, 0)),
                int(self.scores.get(pid, 0)),
            )

        best = max(ranking(pid) for pid in pids)
        winners = [pid for pid in pids if ranking(pid) == best]

        if len(winners) == 1:
            self.winner_id = winners[0]
            self.victory_reason = "timer_most_kills"
        else:
            self.winner_id = None
            self.victory_reason = "timer_tie"

    def _handle_collisions(self) -> None:
        result = self._collision_mgr.resolve(
            self.ships, self.bullets, self.asteroids, self.ufos, self.black_hole
        )

        self.events.extend(result.events)

        for player_id, delta in result.score_deltas.items():
            if player_id in self.scores:
                self.scores[player_id] += delta

        for player_id, delta in result.asteroid_destroy_deltas.items():
            if player_id in self.asteroid_destroys:
                self.asteroid_destroys[player_id] += delta

        for player_id, delta in result.kill_deltas.items():
            if player_id in self.kills:
                self.kills[player_id] += delta

        for pos, vel, size in result.asteroids_to_spawn:
            self.spawn_asteroid(pos, vel, size)

        for pos, kind in result.powerups_to_spawn:
            self.spawn_powerup(pos, kind)

        for death in result.ship_deaths:
            for player_id, is_instakill in death.items():
                ship = self.get_ship(player_id)
                if ship is not None:
                    self._ship_die(ship, is_instakill)

    def _collect_powerups(self) -> None:
        for ship in self.ships.values():
            for powerup in list(self.powerups):
                if (ship.pos - powerup.pos).length() >= (ship.r + powerup.r):
                    continue

                if powerup.kind == "double_shot":
                    ship.activate_double_shot()
                    self.events.append("powerup_pick")

                elif powerup.kind == "repair":
                    self.lives[ship.player_id] = min(
                        C.MAX_LIVES, self.lives[ship.player_id] + 1
                    )
                    self.events.append("powerup_pick")

                elif powerup.kind == "orb":
                    ship.special_energy = min(
                        C.SPECIAL_MAX, ship.special_energy + C.SPECIAL_PER_ORB
                    )
                    self.events.append("powerup_pick")

                elif powerup.kind == "flag":
                    self.flags_collected[ship.player_id] += 1
                    self.events.append("powerup_pick")
                    
                    # Verificar se o jogador ganhou
                    if self.flags_collected[ship.player_id] >= C.FLAGS_TO_WIN:
                        self.game_over = True
                        self.winner_id = ship.player_id
                        self.victory_reason = "flags_10"
                        self.events.append("flag_victory")

                pid = ship.player_id
                self.powerup_pickups[pid] = self.powerup_pickups.get(pid, 0) + 1
                powerup.kill()

    def _ship_die(self, ship: Ship, is_instakill: bool) -> None:
        pid = ship.player_id
        self.lives[pid] -= 1

        if self.is_multiplayer:
            # Respawn imediato no multiplayer
            base = self.player_spawn_positions.get(pid, Vec(C.WIDTH / 2, C.HEIGHT / 2))
            safe = self._clamp_pos_to_screen(Vec(base))
            ship.pos.xy = (safe.x, safe.y)
            ship.vel.xy = (0, 0)
            ship.angle = -90.0
            ship.invuln = float(C.SAFE_SPAWN_TIME)
            self.events.append("ship_explosion")
            return

        # Modo single player - lógica original
        if self.lives[pid] <= 0 or is_instakill:
            # Eliminar o jogador permanentemente
            self.lives[pid] = 0
            ship.kill()
            del self.ships[pid]
            self.events.append("ship_explosion")

            alive = [p for p, v in self.lives.items() if v > 0]
            if len(alive) == 0:
                self.game_over = True
            return

        # Ainda tem vidas — respawn no lugar
        base = self.player_spawn_positions.get(pid, Vec(C.WIDTH / 2, C.HEIGHT / 2))
        safe = self._clamp_pos_to_screen(Vec(base))
        ship.pos.xy = (safe.x, safe.y)
        ship.vel.xy = (0, 0)
        ship.angle = -90.0
        ship.invuln = float(C.SAFE_SPAWN_TIME)
        self.events.append("ship_explosion")
