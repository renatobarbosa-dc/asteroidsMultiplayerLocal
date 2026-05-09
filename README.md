# Ajustes no jogo Asteroids

Clone clássico de **Asteroids** em **Python 3** com **Pygame**: nave, asteroides, UFOs, power-ups, ondas e efeitos de som. O código separa **simulação** (`core/`) de **apresentação e entrada** (`client/`).

## Requisitos

- Python 3.10+ (recomendado)
- [uv](https://docs.astral.sh/uv/) (opcional, para criar o ambiente virtual e instalar dependências)

## Instalação e execução

Clone o repositório:

```bash
git clone https://github.com/PedroYutaroUEA/asteroids_single-player.git
cd asteroids_single-player
```

Crie o ambiente virtual e instale as dependências:

```bash
uv venv
```

Ative o ambiente (o comando varia conforme o shell; no PowerShell no Windows):

```powershell
.\.venv\Scripts\Activate.ps1
```

Confirme que está a usar o Python do projeto e instale os pacotes:

```bash
uv pip install -r requirements.txt
```

Execute o jogo:

```bash
python main.py
```

## Estrutura do repositório

| Pasta / ficheiro | Função |
|------------------|--------|
| `main.py` | Ponto de entrada: inicia `Game().run()` |
| `client/` | Loop do jogo, Pygame (janela, eventos), renderização, input, áudio |
| `core/` | Mundo de jogo, entidades, colisões, comandos e configuração |
| `assets/sounds/` | Ficheiros de áudio usados pelo cliente |
| `docs/` | Documentação e diagramas de arquitetura |

## Documentação

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — descrição detalhada da arquitetura e dos módulos  
- **[docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)** — fluxo de desenvolvimento (se aplicável à equipa)

## Diagramas C4 (arquitetura)

Os diagramas abaixo estão em `docs/` e seguem o **modelo C4** (contexto, contêineres e componentes).

### Nível 1 — Contexto

![Diagrama C4 — Contexto](docs/Arquitetura%20Asteroids%20-%20C4%20Model%20-%20Context%20-%20Asteroids%202.png)

*Ficheiro:* [`docs/Arquitetura Asteroids - C4 Model - Context - Asteroids 2.png`](docs/Arquitetura%20Asteroids%20-%20C4%20Model%20-%20Context%20-%20Asteroids%202.png)

### Nível 2 — Contêineres

![Diagrama C4 — Contêineres](docs/Arquitetura%20Asteroids%20-%20C4%20Model%20-%20Container%20-%20Asteriods%202.png)

*Ficheiro:* [`docs/Arquitetura Asteroids - C4 Model - Container - Asteriods 2.png`](docs/Arquitetura%20Asteroids%20-%20C4%20Model%20-%20Container%20-%20Asteriods%202.png)

### Nível 3 — Componentes

![Diagrama C4 — Componentes](docs/Arquitetura%20Asteroids%20-%20C4%20Model%20-%20Components%20-%20Asteroids%202.png)

*Ficheiro:* [`docs/Arquitetura Asteroids - C4 Model - Components - Asteroids 2.png`](docs/Arquitetura%20Asteroids%20-%20C4%20Model%20-%20Components%20-%20Asteroids%202.png)

## Equipe

- Pedro Yutaro Mont Morency Nakamura (pymmn.snf23@uea.edu.br)
- Renato Barbosa de Carvalho (rbdc.snf23@uea.edu.br)
- Ryan Da Silva Marinho (rdsm.snf23@uea.edu.br)
- Eduarda Souza Da Silva (esds.snf23@uea.edu.br)
- Aglison Balieiro Da Silva (abds.snf23@uea.edu.br)
