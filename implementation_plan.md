# Implementation Plan - Minimal Robotics Simulation Workbench

This plan outlines the design and files for building a modular, expandable 2D grid simulation environment and robot agent. The codebase is organized to resemble standard AI research repositories, making it easy to scale up to complex simulations and LLM integrations.

## User Review Required

> [!NOTE]
> We are using standard library Python to minimize external dependencies. The environment interface is inspired by the **OpenAI Gym/Gymnasium API** (`reset`, `step` returning `obs, reward, done, info`). This is a standard in reinforcement learning and robotics simulation, which will make it natural to integrate LLM-based decision-making.

> [!IMPORTANT]
> The project uses a source-package layout (`src/robotics_workbench`) to keep code modular and importable, while testing is placed in a separate `tests/` directory.

Please let me know if you would like any modifications to this architecture or directory layout before we begin writing the starter code.

## Open Questions

No blocker questions for starting, but:
1. Do you have a preferred grid size or default positions for the robot and target? (Currently proposing a default 10x10 grid with random or configurable starting positions).
2. Would you like to introduce obstacles in the grid right away, or keep it strictly empty for the first step to test the simple navigation logic? (Proposing empty for step 1, with obstacle support prepared as a modular addition).

---

## Proposed Changes

We will create a clean modular Python package:

```
llm-robotics-workbench/
├── src/
│   └── robotics_workbench/
│       ├── __init__.py
│       ├── environment.py     # 2D Grid Environment logic (Gym-like interface)
│       ├── agent.py           # Base Agent interface and a simple heuristic agent
│       ├── simulation.py      # Simulation runner and loop logic
│       └── utils.py           # Helper visualizers and loggers
├── tests/
│   ├── __init__.py
│   ├── test_environment.py    # Unit tests for the environment step/reset logic
│   └── test_agent.py          # Unit tests for agent navigation decisions
├── run_simulation.py          # Script to run the simulation and display console animation
├── requirements.txt           # Python dependency file (pytest for testing)
└── README.md                  # Comprehensive user and developer guide
```

### Core Package

#### [NEW] [__init__.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/src/robotics_workbench/__init__.py)
Exposes key classes (`GridEnvironment`, `SimpleAgent`, `SimulationRunner`) at the package root level.

#### [NEW] [environment.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/src/robotics_workbench/environment.py)
Implements the 2D grid environment:
- State representation: Grid dimensions, robot position $(x, y)$, target position $(x, y)$.
- Action space: `UP`, `DOWN`, `LEFT`, `RIGHT` (we can define these as an `Enum`).
- `reset()`: Re-initializes robot and target positions.
- `step(action)`: Applies movement logic, checks boundaries, calculates step reward / collision penalty, checks if target reached. Returns standard `(observation, reward, done, info)`.
- `render()`: Returns a text representation of the grid (e.g. `.` for empty cells, `R` for robot, `T` for target) or prints it directly.

#### [NEW] [agent.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/src/robotics_workbench/agent.py)
Implements the agents:
- `BaseAgent`: Abstract base class enforcing a `.select_action(observation)` interface.
- `SimpleAgent`: A rule-based agent that computes the Manhattan distance vector to the target and moves in the direction that minimizes it. This serves as a baseline/heuristic.

#### [NEW] [simulation.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/src/robotics_workbench/simulation.py)
Manages the main loop:
- Plugs an instance of `GridEnvironment` and `BaseAgent` together.
- Controls the maximum step count per episode.
- Controls timing/pauses (using `time.sleep`) to create a smooth console animation.
- Collects and logs metrics (number of steps, total reward, success/failure).

#### [NEW] [utils.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/src/robotics_workbench/utils.py)
Utility functions like color coding terminal output, clearing the screen for animation, or formatting state information.

---

### Executables and Metadata

#### [MODIFY] [README.md](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/README.md)
Update the README with:
- Project Overview and architectural diagram (Mermaid).
- Installation guide (using `requirements.txt`).
- Quickstart running instructions.
- Section on how the codebase is ready for LLM agent integration.
- List of suggested Git commits to make as the user builds their repository.

#### [NEW] [run_simulation.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/run_simulation.py)
A lightweight run script that parses command-line arguments (like grid size, max steps, render delay) and starts the simulation.

#### [NEW] [requirements.txt](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/requirements.txt)
Specifies dependencies:
- `pytest` (for unit testing)
- `numpy` (optional: we can write it using pure Python lists/tuples to keep installation instantaneous, but NumPy is a standard tool in robotics. We can list it for completeness or keep it purely standard-lib first. We'll suggest standard library first for simplicity).

---

### Tests

#### [NEW] [__init__.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/tests/__init__.py)
Enables importing code from the sibling package in test scripts.

#### [NEW] [test_environment.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/tests/test_environment.py)
Tests:
- Boundary conditions (cannot walk off the grid).
- Moving transitions.
- Goal reaching conditions and rewards.

#### [NEW] [test_agent.py](file:///C:/Users/15165/.gemini/antigravity/worktrees/ai-agent-sandbox/init-robotics-simulation-workbench/tests/test_agent.py)
Tests:
- Heuristic logic behaves correctly in different quadrants relative to the target.

---

## Verification Plan

### Automated Tests
We can run our suite with `pytest`:
```bash
python -m pytest tests/
```

### Manual Verification
We will execute `python run_simulation.py` to watch the agent navigate to the target in real time. We will verify:
- The screen updates cleanly.
- The path is optimal (moves directly to target).
- The final step displays a success message.
