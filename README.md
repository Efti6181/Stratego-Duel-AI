<div align="center">

<img src="https://capsule-render.vercel.app/api?type=venom&height=220&text=STRATEGO%20DUEL%20AI&fontSize=44&color=0:0f172a,50:4338ca,100:7c3aed&fontColor=ffffff&desc=Plan%20Your%20Moves.%20Protect%20Your%20Flag.&descAlignY=75&descSize=18" width="100%" alt="Stratego Duel AI banner" />

<br>

**A tactical battlefield powered by informed and adversarial search.**

A Python strategy game where you command an army, defend your flag, and challenge an AI opponent combining **A\* Search**, **Minimax**, and **Alpha-Beta Pruning**.

<br>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Pygame-2D%20Game%20Engine-22C55E?style=for-the-badge" alt="Pygame" />
<img src="https://img.shields.io/badge/A%2A-Informed%20Search-8B5CF6?style=for-the-badge" alt="A Star Search" />
<img src="https://img.shields.io/badge/Minimax-Adversarial%20Search-F59E0B?style=for-the-badge" alt="Minimax" />

<br><br>

[Explore Features](#-features) · [AI Architecture](#-how-the-ai-works) · [Run the Game](#-getting-started) · [Controls](#-controls)

</div>

---

## 🎮 Overview

**Stratego Duel AI** is a turn-based **Human vs. AI** strategy game built with Python and Pygame. Each player commands **40 pieces on a 10 × 10 board**, with the goal of capturing the opposing flag.

The project demonstrates how route planning and competitive decision-making can work together in a playable game.

> **Your mission:** Protect your flag, use your army’s special abilities, and outmaneuver the AI.

## ✨ Features

- 🧠 **Hybrid AI** combining A* route planning and Minimax search.
- ⚡ **Alpha-Beta pruning** to reduce unnecessary search.
- 🛡️ **Tactical responses** for flag defense, escape, and immediate winning moves.
- ♟️ **40-piece armies** with ranked combat and special abilities.
- 🎯 **Legal-move highlights** for movement and attacks.
- 🎲 **Randomized AI formations** and optional human Auto Fill.
- 📜 **Battle log** with combat outcomes and capture counters.
- 🏁 **Victory detection** through flag capture or opponent immobility.
- 🔄 **Restart controls** for replaying matches.

## 🧠 How the AI Works

| Component | Responsibility |
|---|---|
| **Tactical Rules** | Handle immediate flag captures, urgent escapes, and flag defense. |
| **A* Search** | Plan routes around blockers and account for threats from revealed enemies. |
| **Minimax** | Evaluate candidate moves against possible opponent responses. |
| **Alpha-Beta Pruning** | Skip search branches that cannot improve the current decision. |
| **Heuristic Evaluation** | Score material, advancement, flag pressure, and tactical opportunities. |

### Decision Process

1. Generate legal moves and check for an immediate win.
2. Evaluate urgent escape and defensive actions.
3. Use **A*** to identify useful routes and reward their first steps.
4. Rank candidate moves using tactical scores and route bonuses.
5. Apply **Minimax with Alpha-Beta pruning** to evaluate continuations.
6. Select and execute the highest-valued candidate.

A* uses **f(n) = g(n) + h(n)**, combining accumulated route cost with estimated remaining movement. Scouts use a separate heuristic to account for their long-range movement.

The AI considers up to **10 root candidates** and **8 moves per recursive node**. Search covers **3 plies including the root move**, increasing to **4 plies** when 14 or fewer pieces remain.

## ⚔️ Game Rules

- Players alternate turns; the **human moves first**.
- Most pieces move **one square horizontally or vertically**.
- **Scouts** can travel multiple clear squares in a straight line.
- Pieces cannot jump over other pieces.
- A higher-ranked piece wins ordinary combat.
- Equal-ranked pieces eliminate each other.
- **Flags and Bombs cannot move**.

| Special Piece | Ability |
|---|---|
| 🚩 **Flag** | Capture the opponent’s flag to win. |
| 💣 **Bomb** | Defeats attackers except Miners. |
| ⛏️ **Miner** | Defuses Bombs when attacking. |
| 🔭 **Scout** | Moves any clear distance along a row or column. |
| 🗡️ **Spy** | Defeats a Marshal when the Spy initiates the attack. |

**Alternative victory:** Win when the opponent has no legal moves.

### Game Variant

Both flag positions are available during battle, and the colored bridge squares are passable. Most enemy identities remain hidden in the interface until combat.

The AI’s internal board contains actual piece ranks, which its search and evaluation can access. This implementation is therefore not a fully information-restricted Stratego agent.

## 🚀 Getting Started

### Requirements

- Python 3
- Pygame
- A desktop environment

### 1. Clone the Repository

```bash
git clone https://github.com/Efti6181/Stratego-Duel-AI.git
cd Stratego-Duel-AI
```

### 2. Install Pygame

```bash
python -m pip install pygame
```

### 3. Launch the Game

```bash
python Stratego_Duel_AStar.py
```

> If you renamed the game file, use its current filename in the launch command.

## 🕹️ Controls

| Input | Action |
|---|---|
| **Left Click** | Select and place pieces during setup; select and move during battle. |
| **Right Click** | Remove a placed human piece during setup. |
| **F1** | Automatically fill remaining setup positions. |
| **Enter** | Start the battle after completing placement. |
| **Space** | Clear the current selection. |
| **R** | Restart the game. |
| **Esc** | Quit. |

## 🏗️ Code Structure

| Component | Purpose |
|---|---|
| `Piece` | Piece attributes and combat resolution. |
| `Board` | Board state, legal moves, move execution, and state copying. |
| `AI` | Tactical rules, A* planning, evaluation, and Minimax search. |
| `Game` | Game phases, player interaction, turns, and results. |
| `draw()` | Board, pieces, highlights, and interface rendering. |
| `main()` | Event handling and the main game loop. |

## 🔮 Future Development

- Configurable difficulty levels.
- Iterative deepening and transposition tables.
- Probability-based reasoning about hidden enemy pieces.
- Match recording and replay.
- AI-versus-AI benchmarking.
- Multiplayer support.

## 👨‍💻 Developer

**Najmul Alam Efti**  
Computer Science and Engineering · Premier University, Chattogram

[![GitHub](https://img.shields.io/badge/GitHub-Efti6181-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Efti6181)

---

<div align="center">

**Built with Python, Pygame, and a passion for Artificial Intelligence.**

⭐ If you find this project useful, consider starring the repository.

</div>
