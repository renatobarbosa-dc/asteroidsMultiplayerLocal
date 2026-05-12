"""Game configuration constants."""

import os

WIDTH = 1920
HEIGHT = 1080
FPS = 120

# True = jogo em tela cheia em WIDTH x HEIGHT (útil em monitor 1920).
FULLSCREEN = True

MAX_PLAYERS = 4
LOCAL_PLAYER_ID = 1

PLAYER_COLORS: dict[int, tuple[int, int, int]] = {
    1: (255, 120, 120),
    2: (120, 200, 255),
    3: (160, 255, 140),
    4: (255, 220, 100),
}

START_LIVES = 3
SAFE_SPAWN_TIME = 2.0
WAVE_DELAY = 2.0
WAVE_BASE_COUNT = 3

SHIP_RADIUS = 15
SHIP_NOSE_ANGLE = 140.0
SHIP_NOSE_SCALE = 0.9

SHIP_TURN_SPEED = 220.0
SHIP_THRUST = 220.0
SHIP_FRICTION = 0.995
SHIP_FIRE_RATE = 0.2

SHIP_BULLET_SPEED = 420.0
SHIP_BASE_SHOT_COUNT = 1

SHIP_SHIELD_DURATION = 2.0
SHIP_SHIELD_COOLDOWN = 6.0
SHIP_SHIELD_HIT_INVULN = 0.6

SHIP_SPREAD_ANGLE_DEG = 8.0
SHIP_DOUBLE_SHOT_COUNT = 2
DOUBLE_SHOT_DURATION = 8.0

HYPERSPACE_COST = 250

BULLET_SPAWN_OFFSET = 6

# SPECIAL (MINIGUN)
SPECIAL_MAX = 30.0
SPECIAL_PER_ORB = 3.0
SPECIAL_DRAIN = 10.0
SPECIAL_FIRE_RATE = 0.05

# REPAIR
MAX_LIVES = 3
REPAIR_DROP_CHANCE = 0.18
ORB_DROP_CHANCE = 0.12

POWERUP_RADIUS = 10
POWERUP_TTL = 10.0
POWERUP_DROP_CHANCE = 0.12

# PIQUE-BANDEIRA
FLAG_DROP_CHANCE = 0.15
FLAGS_TO_WIN = 10

# MULTIPLAYER
MULTIPLAYER_TIMER_SECONDS = 30.0  # multijogador: tempo até o fim da partida (ajusta para testar)

# PARAR TEMPO (HUD / futuro gameplay)
TIME_STOP_DURATION = 5.0
TIME_STOP_COOLDOWN = 12.0

BH_RADIUS = 18
BH_VISUAL_RADIUS = 28
BH_STRENGTH = 800
BH_TIMER_MIN = 40
BH_TIMER_MAX = 120
BH_DURATION_MIN = 5
BH_DURATION_MAX = 11

AST_VEL_MIN = 30.0
AST_VEL_MAX = 90.0
AST_POLY_STEPS = {"L": 24, "M": 15, "S": 12}
AST_POLY_JITTER_MIN = 0.75
AST_POLY_JITTER_MAX = 1.2
AST_MIN_SPAWN_DIST = 150
AST_SPLIT_SPEED_MULT = 1.2
AST_SIZES = {
    "L": {"r": 46, "score": 20, "split": ["M", "M"]},
    "M": {"r": 24, "score": 50, "split": ["S", "S"]},
    "S": {"r": 12, "score": 100, "split": []},
}

BULLET_RADIUS = 2
BULLET_TTL = 1.0
MAX_BULLETS_PER_PLAYER = 4

UFO_SPAWN_EVERY = 12.0
UFO_SPEED_BIG = 95.0
UFO_SPEED_SMALL = 120.0
UFO_BIG = {"r": 18, "score": 200}
UFO_SMALL = {"r": 12, "score": 1000}

UFO_FIRE_RATE_BIG = 0.8
UFO_FIRE_RATE_SMALL = 0.55
UFO_BULLET_SPEED = 360.0
UFO_BULLET_TTL = 1.3

# Aim: small UFO is precise, big UFO is inaccurate.
UFO_AIM_JITTER_DEG_BIG = 28.0
UFO_AIM_JITTER_DEG_SMALL = 6.0
UFO_BIG_MISS_CHANCE = 0.35

WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)

DARK_PURPLE = (40, 0, 80)
VIOLET = (120, 120, 255)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Audio mixer settings
AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512

# UI layout
FONT_SIZE_SMALL = 22
FONT_SIZE_LARGE = 64
FONT_NAME = "consolas"

# Comando / PS4 (SDL): primeiro comando USB = jogador 1, segundo = jogador 2, …
# Se os botões não baterem com o teu comando, altera os índices (testa com um print).
JOY_DEADZONE = 0.22
JOY_AXIS_ROTATE = 0
JOY_AXIS_THRUST = 1
# Botões típicos no Windows com DualShock 4: 0 Cross, 1 Circle, 2 Square, 3 Triangle, 4 L1, 5 R1
JOY_BTN_SHOOT = 0
JOY_BTN_SPECIAL = 1
JOY_BTN_SHIELD = 2
JOY_BTN_HYPER = 3
JOY_MENU_CONFIRM_BUTTONS = (0, 9)  # Cross, Options (confirmar em menus / fim de jogo)

RANDOM_SEED = None

# Paths (work from any execution directory).
# config.py lives in core/, so we go one level up to the project root.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_PATH = os.path.join(BASE_DIR, "assets", "sounds")

# Sounds
PLAYER_SHOOT = "player_shoot.wav"
UFO_SHOOT = "ufo_shoot.wav"
ASTEROID_EXPLOSION = "asteroid_explosion.wav"
SHIP_EXPLOSION = "ship_explosion.wav"
THRUST_LOOP = "thrust_loop.wav"
UFO_SIREN_BIG = "ufo_siren_big.wav"
UFO_SIREN_SMALL = "ufo_siren_small.wav"
HYPERSPACE = "hyperspace.wav"
BLACKHOLE = "blackhole.wav"
