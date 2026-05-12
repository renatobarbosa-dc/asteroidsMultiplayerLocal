# Asteroids multijogador local

Clone de *Asteroids* em **Python** com **Pygame**, pensado para **vários jogadores no mesmo teclado** e **comandos USB (PS4 / DualSense)**. A lógica de jogo (`core`) está separada do cliente (`client`).

## Requisitos e execução

- Python 3.10+ (testado com 3.11)
- Dependências: `pip install -r requirements.txt`
- Arranque: `python main.py`

Resolução e janela vêm de `core/config.py` (`WIDTH`, `HEIGHT`, `FULLSCREEN`).

---

## Estrutura do fluxo do jogo

1. **Menu** — avança com tecla ou qualquer botão do comando.
2. **Escolha de jogadores** — 1 a 4 jogadores (teclas 1–4, setas + Enter, ou D-pad + Cross/Options no comando).
3. **Partida** — loop: input → `World.update` → desenho + áudio.
4. **Fim de jogo** — duas telas: resumo (vencedor / empate / motivo) e **estatísticas** (Enter ou Cross/Options para avançar).

---

## Controlos

### Teclado (até 4 jogadores)

| Jogador | Rodar esq. | Rodar dir. | Impulso | Tiro | Escudo | Hiperespaço | Especial |
|--------|--------------|-------------|---------|------|--------|-------------|----------|
| **P1** | A | D | W | Espaço | E | Shift esq. | Ctrl esq. |
| **P2** | J | L | I | O | U | P | `]` |
| **P3** | F | H | T | G | R | V | M |
| **P4** | ← | → | ↑ | Ctrl dir. | Shift dir. | End | Page Down |

Ações de tiro / escudo / hiper / especial são **à pressão** (um toque por evento de tecla).

### Comando (PS4 / DualSense via SDL)

- O **1.º** comando USB fica no **P1**, o **2.º** no **P2**, etc., até ao número de jogadores da sessão.
- **Stick esquerdo**: horizontal roda a nave; vertical **para cima** dá impulso (com *dead zone*).
- **D-pad**: esquerda/direita rodam; **cima** dá impulso (útil alinhado com o SDL).
- **Botões** (valores por defeito no Windows; ajustáveis em `core/config.py`):

| Ação | Botão típico (PS4) |
|------|---------------------|
| Tiro | Cross (0) |
| Especial | Circle (1) |
| Escudo | Square (2) |
| Hiperespaço | Triangle (3) |

Confirmar em menus / fim de jogo: **Cross** ou **Options** (9).

Se usares **DS4Windows** em modo Xbox, os índices podem mudar — edita `JOY_BTN_*`, `JOY_AXIS_*` e `JOY_DEADZONE` em `config.py`.

---

## Modo **1 jogador**

- **Ondas**: quando não há asteroides, após um breve atraso começa a **próxima onda** (mais asteroides).
- **UFOs**: aparecem periodicamente, atiram e dão pontos ao serem destruídos.
- **Vidas**: começas com várias vidas; colisão com asteróide (sem escudo ativo) ou outros perigos podem consumir vidas. **Game over** quando não restam vidas.
- **Pontuação**: destruir asteroides, UFOs, etc., conforme `AST_SIZES` e regras em `core/collisions.py`.
- **Hiperespaço**: custa pontos (`HYPERSPACE_COST`); se não tiveres pontos suficientes, o custo é limitado ao que tens.

---

## Modo **multijogador** (2–4 jogadores)

- **Sem UFOs** — só asteroides, power-ups, buraco negro e **PvP** (tiros entre naves contam como *kills*).
- **Sem fim por vidas** — ao morreres, **respawn** imediato no ponto de spawn do jogador.
- **Timer global** (`MULTIPLAYER_TIMER_SECONDS` em `config.py`) — quando chega a zero, a partida termina.
- **Vitória imediata por bandeiras**: o primeiro a recolher **10 bandeiras** (`FLAGS_TO_WIN`) ganha (pique-bandeira).
- **Fim por tempo**: se ninguém chegou às 10 bandeiras, vence quem tiver **mais kills**; em empate de kills, **mais bandeiras**; depois **pontuação**.
- **Asteróides**: spawn contínuo para manter pressão no campo (não é o mesmo sistema de ondas do 1 jogador).

---

## Mecânicas comuns

### Nave

- Rotação contínua enquanto a tecla / stick estiver ativo.
- Impulso com atrito.
- **Tiro** com cadência máxima e limite de balas por jogador (`MAX_BULLETS_PER_PLAYER`).
- **Escudo**: duração e cooldown configuráveis; pode bloquear um impacto.
- **Especial** (“minigun”): barra de energia (`SPECIAL_*`); orbes aumentam energia.
- **Double shot** e outros power-ups alteram o comportamento temporariamente.

### Asteróides

- Tamanhos **L → M → S**; ao serem atingidos por **tiros de jogador** partem-se e dão **pontos**.
- Colisão nave–asteróide: pode partir o asteróide se o escudo absorver o golpe; caso contrário conta como dano / morte conforme o modo.

### Power-ups (quedas ao destruir asteroides)

- **Repair** — vida extra (até `MAX_LIVES`).
- **Orb** — energia do especial.
- **Double shot** — tiros duplos temporários.
- **Bandeira** — incrementa o contador de **pique-bandeira** (vitória imediata no MP ao atingir a meta).

Probabilidades e TTL em `config.py` (`*_DROP_CHANCE`, `POWERUP_TTL`).

### Buraco negro

- Aparece após intervalos aleatórios; exerce **atração** nas naves; colisão com o centro pode ser **morte instantânea** (instakill).

### Colisões e eventos

- `core/collisions.py` resolve impactos e devolve deltas de pontuação, *kills*, asteroides a criar e power-ups a largar.
- `core/world.py` aplica regras de vitória, timer multijogador, recolha de power-ups e respawn.

---

## HUD e estatísticas

- **1 jogador**: score, vidas, onda, bandeiras em progresso, barras de especial / escudo / “parar tempo” (quando ativo ou em cooldown — o estado “pronto” não ocupa a HUD).
- **Multijogador**: tempo restante, painéis por jogador (score, bandeiras, kills), barra de especial.
- **Fim de jogo — estatísticas**: líderes e tabela por jogador (bandeiras, kills, asteróides destruídos com tiro pontuado, power-ups apanhados).

---

## Configuração (`core/config.py`)

Entre outros: resolução, FPS, vidas iniciais, física da nave, pontuação dos asteroides, meta de bandeiras, duração do timer multijogador, áudio e mapeamento do comando. Comentários no ficheiro indicam o propósito de cada grupo de constantes.

---

## Pastas do repositório

| Pasta / ficheiro | Função |
|------------------|--------|
| `main.py` | Ponto de entrada. |
| `client/game.py` | Ciclo principal, cenas e áudio. |
| `client/renderer.py` | Desenho (menu, HUD, entidades, fim de jogo). |
| `client/controls.py` | Teclado + joystick → `PlayerCommand`. |
| `client/audio*.py` | Sons. |
| `core/world.py` | Estado do jogo e regras. |
| `core/entities.py` | Nave, asteróide, bala, UFO, power-up, buraco negro. |
| `core/collisions.py` | Deteção e resolução de colisões. |
| `core/config.py` | Constantes globais. |
| `assets/sounds/` | Ficheiros `.wav`. |

Para mais detalhe de arquitetura, vê `docs/ARCHITECTURE.md` (se existir no teu clone).
