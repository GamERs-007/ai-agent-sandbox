#!/usr/bin/env python3
"""
Entrypoint script for running the 2D Grid Robotics Simulation.
Allows customizing the grid size, animation speeds, and step limits via command-line arguments.
"""
import os
import sys
import argparse

# Add 'src' directory to Python path to resolve local packages easily
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "src"))

# pyrefly: ignore [missing-import]
from robotics_workbench.environment import GridEnvironment
# pyrefly: ignore [missing-import]
from robotics_workbench.agent import SimpleAgent
# pyrefly: ignore [missing-import]
from robotics_workbench.simulation import SimulationRunner
# pyrefly: ignore [missing-import]
from robotics_workbench.gui import GUIRunner

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Robotics Simulation Workbench: 2D Grid & Heuristic Agent Demonstration"
    )
    parser.add_argument(
        "--width", 
        type=int, 
        default=10, 
        help="Width of the grid environment (columns). Default: 10"
    )
    parser.add_argument(
        "--height", 
        type=int, 
        default=10, 
        help="Height of the grid environment (rows). Default: 10"
    )
    parser.add_argument(
        "--delay", 
        type=float, 
        default=0.2, 
        help="Frame delay in seconds for terminal animation. Default: 0.2"
    )
    parser.add_argument(
        "--max-steps", 
        type=int, 
        default=50, 
        help="Maximum step budget allowed to reach target. Default: 50"
    )
    parser.add_argument(
        "--no-render", 
        action="store_true", 
        help="Run simulation headlessly (no console visualization prints)."
    )
    parser.add_argument(
        "--terminal", 
        action="store_true", 
        help="Run simulation in the terminal (ASCII visualization) instead of GUI."
    )
    
    args = parser.parse_args()
    
    # Initialize component structures
    env = GridEnvironment(width=args.width, height=args.height)
    agent = SimpleAgent()
    
    if args.no_render:
        runner = SimulationRunner(env, agent)
        metrics = runner.run_episode(
            max_steps=args.max_steps,
            render_delay=args.delay,
            render=False
        )
        print("--- Headless Simulation Summary ---")
        print(f"Goal Reached : {metrics['success']}")
        print(f"Steps Taken  : {metrics['steps']}")
        print(f"Total Reward : {metrics['total_reward']:.2f}")
    elif args.terminal:
        runner = SimulationRunner(env, agent)
        runner.run_episode(
            max_steps=args.max_steps,
            render_delay=args.delay,
            render=True
        )
    else:
        # Run in GUI mode (external window) by default
        gui_runner = GUIRunner(
            env=env,
            agent=agent,
            max_steps=args.max_steps,
            initial_delay=args.delay
        )
        gui_runner.start()

if __name__ == "__main__":
    main()

