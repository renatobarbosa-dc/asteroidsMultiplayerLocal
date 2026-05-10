"""Audio playback manager for the game client."""

import pygame as pg

from client.audio import SoundPack


class AudioManager:
    """Manages audio channels and event-driven sound playback."""

    def __init__(self, sounds: SoundPack) -> None:
        self.sounds = sounds
        self._thrust_ch = pg.mixer.Channel(1)
        self._sfx_ch = pg.mixer.Channel(2)
        self._ufo_ch = pg.mixer.Channel(3)
        self._blackhole_ch = pg.mixer.Channel(4)
        self._ufo_siren_kind: str | None = None

    def play_events(self, events: list[str]) -> None:
        for ev in events:
            if ev == "player_shoot":
                self._sfx_ch.play(self.sounds.player_shoot)
            elif ev == "ufo_shoot":
                self._sfx_ch.play(self.sounds.ufo_shoot)
            elif ev == "asteroid_explosion":
                self._sfx_ch.play(self.sounds.asteroid_explosion)
            elif ev == "ship_explosion":
                self._sfx_ch.play(self.sounds.ship_explosion)
            elif ev == "powerup_pick":
                self._sfx_ch.play(self.sounds.player_shoot)
            elif ev == "hyperspace":
                self._sfx_ch.play(self.sounds.hyperspace)

    def update_thrust(self, active: bool) -> None:
        if active:
            if not self._thrust_ch.get_busy():
                self._thrust_ch.play(self.sounds.thrust_loop, loops=-1)
        else:
            if self._thrust_ch.get_busy():
                self._thrust_ch.stop()

    def update_blackhole_audio(self, black_hole) -> None:
        if black_hole is None:
            if self._blackhole_ch.get_busy():
                self._blackhole_ch.stop()
            return

        if not self._blackhole_ch.get_busy():
            self._blackhole_ch.play(self.sounds.blackhole, loops=-1)

    def update_ufo_siren(self, ufos: list) -> None:
        kind = self._choose_ufo_siren(ufos)
        if kind is None:
            if self._ufo_ch.get_busy():
                self._ufo_ch.stop()
            self._ufo_siren_kind = None
            return

        if self._ufo_siren_kind == kind:
            return

        self._ufo_ch.stop()
        if kind == "small":
            snd = self.sounds.ufo_siren_small
        else:
            snd = self.sounds.ufo_siren_big

        self._ufo_ch.play(snd, loops=-1)
        self._ufo_siren_kind = kind

    def stop_all(self) -> None:
        if self._thrust_ch.get_busy():
            self._thrust_ch.stop()
        if self._ufo_ch.get_busy():
            self._ufo_ch.stop()
        if self._blackhole_ch.get_busy():
            self._blackhole_ch.stop()
        self._ufo_siren_kind = None

    def _choose_ufo_siren(self, ufos: list) -> str | None:
        if not ufos:
            return None
        has_small = any(getattr(u, "small", False) for u in ufos)
        return "small" if has_small else "big"
