"""Teclado e comando (PS4 / DualSense) → `PlayerCommand` por jogador.

- Teclado: igual ao layout 1–4 local.
- Comando: 1.º USB ligado → P1, 2.º → P2, … até ao número de jogadores da sessão.
"""

from typing import Dict

import pygame as pg

from core import config as C
from core.commands import PlayerCommand

PlayerId = int

# KEYDOWN: (player_id, ação)
_KEYDOWN_ACTIONS: dict[int, tuple[PlayerId, str]] = {
    pg.K_SPACE: (1, "shoot"),
    pg.K_e: (1, "shield"),
    pg.K_LSHIFT: (1, "hyper"),
    pg.K_LCTRL: (1, "special"),
    pg.K_o: (2, "shoot"),
    pg.K_u: (2, "shield"),
    pg.K_p: (2, "hyper"),
    pg.K_RIGHTBRACKET: (2, "special"),
    pg.K_g: (3, "shoot"),
    pg.K_r: (3, "shield"),
    pg.K_v: (3, "hyper"),
    pg.K_m: (3, "special"),
    pg.K_RCTRL: (4, "shoot"),
    pg.K_RSHIFT: (4, "shield"),
    pg.K_END: (4, "hyper"),
    pg.K_PAGEDOWN: (4, "special"),
}

_MOVEMENT_KEYS: list[tuple[PlayerId, int, int, int]] = [
    (1, pg.K_a, pg.K_d, pg.K_w),
    (2, pg.K_j, pg.K_l, pg.K_i),
    (3, pg.K_f, pg.K_h, pg.K_t),
    (4, pg.K_LEFT, pg.K_RIGHT, pg.K_UP),
]

_JOY_BTN_ACTION: tuple[tuple[str, int], ...] = (
    ("shoot", int(C.JOY_BTN_SHOOT)),
    ("shield", int(C.JOY_BTN_SHIELD)),
    ("hyper", int(C.JOY_BTN_HYPER)),
    ("special", int(C.JOY_BTN_SPECIAL)),
)


class InputMapper:
    """Converte teclado + joysticks em `PlayerCommand` por `player_id`."""

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
        self._joy_for_player: Dict[PlayerId, pg.joystick.Joystick] = {}
        self._joy_btn_prev: dict[int, tuple[bool, ...]] = {}
        pg.joystick.init()
        self._scan_existing_joysticks()

    def set_player_count(self, player_count: int) -> None:
        self.player_count = max(1, min(C.MAX_PLAYERS, int(player_count)))
        for pid in list(self._joy_for_player.keys()):
            if pid > self.player_count:
                j = self._joy_for_player.pop(pid)
                self._joy_btn_prev.pop(j.get_instance_id(), None)
        self._scan_existing_joysticks()

    def _scan_existing_joysticks(self) -> None:
        for i in range(pg.joystick.get_count()):
            j = pg.joystick.Joystick(i)
            j.init()
            self._try_assign_joy(j)

    def _try_assign_joy(self, joy: pg.joystick.Joystick) -> None:
        iid = joy.get_instance_id()
        for j in self._joy_for_player.values():
            if j.get_instance_id() == iid:
                return
        for pid in range(1, self.player_count + 1):
            if pid not in self._joy_for_player:
                self._joy_for_player[pid] = joy
                n = joy.get_numbuttons()
                self._joy_btn_prev[iid] = tuple(False for _ in range(n))
                return

    def _remove_joy(self, instance_id: int) -> None:
        for pid, j in list(self._joy_for_player.items()):
            if j.get_instance_id() == instance_id:
                del self._joy_for_player[pid]
                self._joy_btn_prev.pop(instance_id, None)
                return

    def handle_joystick_connection(self, event: pg.event.Event) -> None:
        if event.type == pg.JOYDEVICEADDED:
            j = pg.joystick.Joystick(event.device_index)
            j.init()
            self._try_assign_joy(j)
            return
        if event.type == pg.JOYDEVICEREMOVED:
            self._remove_joy(event.instance_id)

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

    def _joy_motion(self, joy: pg.joystick.Joystick) -> tuple[bool, bool, bool]:
        dz = float(C.JOY_DEADZONE)
        ax = int(C.JOY_AXIS_ROTATE)
        ay = int(C.JOY_AXIS_THRUST)
        a0 = joy.get_axis(ax) if joy.get_numaxes() > ax else 0.0
        a1 = joy.get_axis(ay) if joy.get_numaxes() > ay else 0.0
        rl = a0 < -dz
        rr = a0 > dz
        th = a1 < -dz
        if joy.get_numhats() > 0:
            hx, hy = joy.get_hat(0)
            if hx < 0:
                rl = True
            elif hx > 0:
                rr = True
            if hy < 0:
                th = True
        return rl, rr, th

    def _joy_button_edges(self) -> Dict[PlayerId, dict[str, bool]]:
        actions = ("shoot", "shield", "hyper", "special")
        out: Dict[PlayerId, dict[str, bool]] = {
            pid: {a: False for a in actions} for pid in range(1, C.MAX_PLAYERS + 1)
        }
        new_prev: dict[int, tuple[bool, ...]] = {}
        for pid, joy in self._joy_for_player.items():
            if pid > self.player_count:
                continue
            if not joy.get_init():
                continue
            n = joy.get_numbuttons()
            curr = tuple(joy.get_button(i) for i in range(n))
            iid = joy.get_instance_id()
            prev = self._joy_btn_prev.get(iid)
            if prev is None or len(prev) != n:
                prev = tuple(False for _ in range(n))
            for act, bi in _JOY_BTN_ACTION:
                if 0 <= bi < n and curr[bi] and not prev[bi]:
                    out[pid][act] = True
            new_prev[iid] = curr
        self._joy_btn_prev.update(new_prev)
        return out

    def build_commands(self, keys: pg.key.ScancodeWrapper) -> Dict[PlayerId, PlayerCommand]:
        joy_edge = self._joy_button_edges()
        out: Dict[PlayerId, PlayerCommand] = {}
        for pid, left_k, right_k, thrust_k in _MOVEMENT_KEYS:
            if pid > self.player_count:
                break
            rl = bool(keys[left_k])
            rr = bool(keys[right_k])
            th = bool(keys[thrust_k])
            joy = self._joy_for_player.get(pid)
            if joy is not None and joy.get_init():
                jrl, jrr, jth = self._joy_motion(joy)
                rl = rl or jrl
                rr = rr or jrr
                th = th or jth
            ed = self._edges[pid]
            je = joy_edge[pid]
            cmd = PlayerCommand(
                rotate_left=rl,
                rotate_right=rr,
                thrust=th,
                shoot=ed["shoot"] or je["shoot"],
                shield=ed["shield"] or je["shield"],
                hyperspace=ed["hyper"] or je["hyper"],
                special=ed["special"] or je["special"],
            )
            for k in ed:
                ed[k] = False
            out[pid] = cmd
        return out

    @staticmethod
    def is_menu_confirm(event: pg.event.Event) -> bool:
        if event.type != pg.JOYBUTTONDOWN:
            return False
        return event.button in tuple(C.JOY_MENU_CONFIRM_BUTTONS)
