"""Teclado → comandos por jogador (1–4, sem teclado numérico).

Futuro: mapear o mesmo `PlayerCommand` a partir de `pygame.joystick`.
"""

from typing import Dict

import pygame as pg

from core import config as C
from core.commands import PlayerCommand

PlayerId = int

# KEYDOWN: (player_id, ação)
_KEYDOWN_ACTIONS: dict[int, tuple[PlayerId, str]] = {
    # P1 — WASD + linha de ações à esquerda
    pg.K_SPACE: (1, "shoot"),
    pg.K_e: (1, "shield"),
    pg.K_LSHIFT: (1, "hyper"),
    pg.K_LCTRL: (1, "special"),
    # P2 — IJKL + teclas à direita do bloco
    pg.K_o: (2, "shoot"),
    pg.K_u: (2, "shield"),
    pg.K_p: (2, "hyper"),
    pg.K_RIGHTBRACKET: (2, "special"),
    # P3 — TFGH (estilo WASD no meio do teclado)
    pg.K_g: (3, "shoot"),
    pg.K_r: (3, "shield"),
    pg.K_v: (3, "hyper"),
    pg.K_m: (3, "special"),
    # P4 — setas + bloco acima das setas
    pg.K_RCTRL: (4, "shoot"),
    pg.K_RSHIFT: (4, "shield"),
    pg.K_END: (4, "hyper"),
    pg.K_PAGEDOWN: (4, "special"),
}

# Movimento contínuo: (pid, esquerda, direita, impulso)
_MOVEMENT_KEYS: list[tuple[PlayerId, int, int, int]] = [
    (1, pg.K_a, pg.K_d, pg.K_w),
    (2, pg.K_j, pg.K_l, pg.K_i),
    (3, pg.K_f, pg.K_h, pg.K_t),
    (4, pg.K_LEFT, pg.K_RIGHT, pg.K_UP),
]


class InputMapper:
    """Converte teclado em `PlayerCommand` por `player_id`."""

    def __init__(self, player_count: int = 1) -> None:
        self.player_count = max(1, min(C.MAX_PLAYERS, int(player_count)))
        self._edges: Dict[PlayerId, dict[str, bool]] = {
            pid: {
                "shoot": False,
                "shield": False,
                "hyper": False,
                "special": False,
            }
            for pid in range(1, C.MAX_PLAYERS + 1)
        }

    def set_player_count(self, player_count: int) -> None:
        self.player_count = max(1, min(C.MAX_PLAYERS, int(player_count)))

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type != pg.KEYDOWN:
            return
        mapped = _KEYDOWN_ACTIONS.get(event.key)
        if mapped is None:
            return
        player_id, action = mapped
        if player_id > self.player_count:
            return
        self._edges[player_id][action] = True

    def build_commands(self, keys: pg.key.ScancodeWrapper) -> Dict[PlayerId, PlayerCommand]:
        out: Dict[PlayerId, PlayerCommand] = {}
        for pid, left_k, right_k, thrust_k in _MOVEMENT_KEYS:
            if pid > self.player_count:
                break
            ed = self._edges[pid]
            cmd = PlayerCommand(
                rotate_left=bool(keys[left_k]),
                rotate_right=bool(keys[right_k]),
                thrust=bool(keys[thrust_k]),
                shoot=ed["shoot"],
                shield=ed["shield"],
                hyperspace=ed["hyper"],
                special=ed["special"],
            )
            for k in ed:
                ed[k] = False
            out[pid] = cmd
        return out
