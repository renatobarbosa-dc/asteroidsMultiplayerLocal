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

    def __init__(self) -> None:
        self.ships: Dict[PlayerId, Ship] = {}
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

        self.scores: Dict[PlayerId, int] = {}
        self.lives: Dict[PlayerId, int] = {}
        self.wave = 0
        self.wave_cool = float(C.WAVE_DELAY)
        self.ufo_timer = float(C.UFO_SPAWN_EVERY)

        self.black_hole = None
        # blackhole spawn period
        self.bh_timer = uniform(C.BH_TIMER_MIN, C.BH_TIMER_MAX)
        self.bh_duration = 0

        self.events: list[str] = []
        self._collision_mgr = CollisionManager()

        self.game_over = False
        self.time_stop_timer = 0.0
        self.time_stop_cool = 0.0

        self.spawn_player(C.LOCAL_PLAYER_ID)

    def begin_frame(self) -> None:
        self.events.clear()

    def reset(self) -> None:
        """Reset the world (used on Game Over)."""
        self.__init__()

    def spawn_player(self, player_id: PlayerId) -> None:
        pos = Vec(C.WIDTH / 2, C.HEIGHT / 2)
        ship = Ship(player_id, pos)
        ship.invuln = float(C.SAFE_SPAWN_TIME)

        self.ships[player_id] = ship
        self.scores[player_id] = 0
        self.lives[player_id] = C.START_LIVES
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

    def spawn_black_hole(self, ship: Ship):
        """Handles blackhole spawwning based on player pos"""
        pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        while (pos - ship.pos).length() < 200:
            pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))

        bh = BlackHole(pos)
        self.black_hole = bh
        self.all_sprites.add(bh)
        self.bh_duration = uniform(C.BH_DURATION_MIN, C.BH_DURATION_MAX)

    def _update_blackhole(self, dt: float, ship: Ship):
        """Handles blackhole timers and effects"""
        # Handle blackhole spawn time
        if self.black_hole:
            self.bh_duration -= dt
            if self.bh_duration <= 0:
                self.black_hole.kill()
                self.black_hole = None
                self.bh_timer = uniform(10, 20)
        else:
            self.bh_timer -= dt
            if self.bh_timer <= 0:
                self.spawn_black_hole(ship)

        # Blackhole Gravity effect
        if self.black_hole:
            dir_vec = self.black_hole.pos - ship.pos
            dist = dir_vec.length()

            if dist > 0:
                dir_vec = dir_vec.normalize()
                # reduces based on distance
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
        # Handle time stop timer
        if self.time_stop_timer > 0.0:
            self.time_stop_timer -= dt
            if self.time_stop_timer < 0.0:
                self.time_stop_timer = 0.0
            enemy_dt = 0.0
        else:
            enemy_dt = dt

        # Handle time stop cooldown
        if self.time_stop_cool > 0.0:
            self.time_stop_cool -= dt
            if self.time_stop_cool < 0.0:
                self.time_stop_cool = 0.0

        self._apply_commands(dt, commands_by_player_id)

        for ship in self.ships.values():
            created = ship.update(dt)
            if created:
                self.bullets.add(*created)
                self.all_sprites.add(*created)

            self._update_blackhole(dt, ship)
        for bullet in self.bullets:
            bullet.update(dt)
        for ast in self.asteroids:
            ast.update(enemy_dt)
        for powerup in self.powerups:
            powerup.update(dt)

        self._update_ufos(enemy_dt)
        self._update_timers(dt)
        self._handle_collisions()
        self._collect_powerups()
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

            if (
                cmd.time_stop
                and self.time_stop_timer <= 0.0
                and self.time_stop_cool <= 0.0
            ):
                self.time_stop_timer = float(C.TIME_STOP_DURATION)
                self.time_stop_cool = float(C.TIME_STOP_DURATION + C.TIME_STOP_COOLDOWN)
                self.events.append("time_stop")

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

    def _handle_collisions(self) -> None:
        result = self._collision_mgr.resolve(
            self.ships, self.bullets, self.asteroids, self.ufos, self.black_hole
        )

        self.events.extend(result.events)

        for player_id, delta in result.score_deltas.items():
            if player_id in self.scores:
                self.scores[player_id] += delta

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

                powerup.kill()

    def _ship_die(self, ship: Ship, is_instakill: bool) -> None:
        pid = ship.player_id
        self.lives[pid] = self.lives[pid] - 1
        ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
        ship.vel.xy = (0, 0)
        ship.angle = -90.0
        ship.invuln = float(C.SAFE_SPAWN_TIME)

        self.events.append("ship_explosion")
        if all(v <= 0 for v in self.lives.values()) or is_instakill:
            self.game_over = True
