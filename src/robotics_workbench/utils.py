import os
from typing import Dict, Any, Optional

def clear_terminal() -> None:
    """
    Clears the terminal screen using ANSI escape sequences.
    This works across Windows, macOS, and Linux without starting shell subprocesses.
    """
    # ANSI escape code: \033[H moves cursor to top-left, \033[2J clears the screen
    print("\033[H\033[2J", end="", flush=True)


def print_grid_with_info(
    grid_str: str, 
    step: int, 
    total_reward: float, 
    obs: Dict[str, Any],
    last_action: Optional[str] = None,
    last_reward: Optional[float] = None
) -> None:
    """
    Prints the simulation dashboard in the terminal.
    Includes current coordinates, steps, cumulative reward, last action, and the grid.
    """
    rx, ry = obs["robot_position"]
    tx, ty = obs["target_position"]
    w, h = obs["grid_size"]
    
    print("=" * 40)
    print("      ROBOTICS SIMULATION WORKBENCH      ")
    print("=" * 40)
    print(f"Grid Size      : {w}x{h}")
    print(f"Robot Position : ({rx}, {ry})")
    print(f"Target Position: ({tx}, {ty})")
    print(f"Steps Taken    : {step}")
    print(f"Total Reward   : {total_reward:.2f}")
    
    if last_action is not None:
        print(f"Last Action    : {last_action} (Reward: {last_reward})")
    else:
        print("Last Action    : N/A")
        
    print("-" * 40)
    print(grid_str)
    print("=" * 40)
