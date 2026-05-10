"""Game loop and scenes (menu, escolha de jogadores, play, game over).

- InputMapper converte teclado em PlayerCommand por jogador.
- World recebe comandos indexados por player_id.
"""

import sys

import pygame as pg

from core import config as C
from core.scene import SceneState
from core.world import World
from client.audio import load_sounds
from client.audio_manager import AudioManager
from client.controls import InputMapper
from client.renderer import Renderer


class Game:
    """Orchestrates input -> update -> draw."""

    def __init__(self) -> None:
        pg.mixer.pre_init(
            C.AUDIO_FREQUENCY, C.AUDIO_SIZE, C.AUDIO_CHANNELS, C.AUDIO_BUFFER
        )
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroids")

        self.clock = pg.time.Clock()
        self.running = True

        self.font = pg.font.SysFont(C.FONT_NAME, C.FONT_SIZE_SMALL)
        self.big = pg.font.SysFont(C.FONT_NAME, C.FONT_SIZE_LARGE)
        self.renderer = Renderer(
            self.screen,
            config=C,
            fonts={"font": self.font, "big": self.big},
        )

        self.scene = SceneState.MENU
        self.selected_player_count = 2
        self.player_select_highlight = self.selected_player_count
        self.world: World | None = None
        self.input_mapper = InputMapper(self.selected_player_count)

        self.sounds = load_sounds(C.SOUND_PATH)
        self.audio = AudioManager(self.sounds)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

        pg.quit()

    def _start_session(self, player_count: int) -> None:
        n = max(1, min(C.MAX_PLAYERS, int(player_count)))
        self.selected_player_count = n
        self.input_mapper.set_player_count(n)
        self.world = World(n)
        self.scene = SceneState.PLAY

    def _handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.scene == SceneState.PLAYER_SELECT:
                    self.scene = SceneState.MENU
                    continue
                self._quit()

            if self.scene == SceneState.MENU:
                if event.type == pg.KEYDOWN:
                    self.scene = SceneState.PLAYER_SELECT
                    self.player_select_highlight = self.selected_player_count
                continue

            if self.scene == SceneState.PLAYER_SELECT:
                if event.type != pg.KEYDOWN:
                    continue
                k = event.key
                if k in (pg.K_1, pg.K_KP1):
                    self._start_session(1)
                elif k in (pg.K_2, pg.K_KP2):
                    self._start_session(2)
                elif k in (pg.K_3, pg.K_KP3):
                    self._start_session(3)
                elif k in (pg.K_4, pg.K_KP4):
                    self._start_session(4)
                elif k == pg.K_UP:
                    self.player_select_highlight = max(
                        1, self.player_select_highlight - 1
                    )
                elif k == pg.K_DOWN:
                    self.player_select_highlight = min(
                        C.MAX_PLAYERS, self.player_select_highlight + 1
                    )
                elif k in (pg.K_RETURN, pg.K_KP_ENTER):
                    self._start_session(self.player_select_highlight)
                continue

            if self.scene == SceneState.GAME_OVER:
                if event.type == pg.KEYDOWN:
                    self.world = None
                    self.scene = SceneState.PLAYER_SELECT
                    self.player_select_highlight = self.selected_player_count
                continue

            if self.scene == SceneState.PLAY:
                self.input_mapper.handle_event(event)

    def _update(self, dt: float) -> None:
        if self.scene != SceneState.PLAY or self.world is None:
            return

        keys = pg.key.get_pressed()
        commands = self.input_mapper.build_commands(keys)

        self.world.update(dt, commands)

        if self.world.game_over:
            self.audio.stop_all()
            self.scene = SceneState.GAME_OVER
            return

        self.audio.update_thrust(any(c.thrust for c in commands.values()))
        self.audio.update_ufo_siren(list(self.world.ufos))
        self.audio.update_blackhole_audio(self.world.black_hole)
        self.audio.play_events(self.world.events)

    def _draw(self) -> None:
        self.renderer.clear()

        if self.scene == SceneState.MENU:
            self.renderer.draw_menu()
            pg.display.flip()
            return

        if self.scene == SceneState.PLAYER_SELECT:
            self.renderer.draw_player_select(self.player_select_highlight)
            pg.display.flip()
            return

        if self.scene == SceneState.GAME_OVER:
            self.renderer.draw_game_over()
            pg.display.flip()
            return

        if self.world is None:
            pg.display.flip()
            return

        self.renderer.draw_world(self.world)
        self.renderer.draw_hud(self.world, self.scene)
        pg.display.flip()

    def _quit(self) -> None:
        self.running = False
        pg.quit()
        sys.exit(0)
