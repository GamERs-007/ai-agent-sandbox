import time
from typing import Dict, Any
from robotics_workbench.environment import GridEnvironment
from robotics_workbench.agent import BaseAgent
from robotics_workbench.utils import clear_terminal, print_grid_with_info

class SimulationRunner:
    """
    Manages the simulation loop connecting the environment and the agent.
    Collects run statistics and handles terminal-based animation frames.
    """
    def __init__(self, env: GridEnvironment, agent: BaseAgent):
        """
        Initializes the runner with an environment and an agent.
        
        Args:
            env (GridEnvironment): The environment instance.
            agent (BaseAgent): The agent instance.
        """
        self.env = env
        self.agent = agent

    def run_episode(self, max_steps: int = 50, render_delay: float = 0.2, render: bool = True) -> Dict[str, Any]:
        """
        Runs a single simulation episode from reset to termination or step limit.
        
        Args:
            max_steps (int): Maximum steps allowed before forced termination.
            render_delay (float): Time (in seconds) to pause between steps for visualization.
            render (bool): Whether to clear and print the console dashboard on each step.
            
        Returns:
            Dict[str, Any]: Episode summary statistics (success, steps, total_reward, trajectory).
        """
        obs = self.env.reset()
        done = False
        step_count = 0
        total_reward = 0.0
        trajectory = []
        
        if render:
            clear_terminal()
            print("Initializing Simulation Environment...")
            print_grid_with_info(self.env.render_ascii(), step_count, total_reward, obs)
            time.sleep(render_delay)
            
        while not done and step_count < max_steps:
            # Query agent for next action
            action = self.agent.select_action(obs)
            
            # Apply action in environment
            next_obs, reward, done, info = self.env.step(action)
            
            step_count += 1
            total_reward += reward
            
            # Record transition for research analysis / prompt engineering history
            trajectory.append({
                "step": step_count,
                "action": action,
                "reward": reward,
                "robot_position": next_obs["robot_position"]
            })
            
            obs = next_obs
            
            if render:
                clear_terminal()
                print_grid_with_info(
                    self.env.render_ascii(), 
                    step_count, 
                    total_reward, 
                    obs, 
                    last_action=action, 
                    last_reward=reward
                )
                time.sleep(render_delay)
                
        success = obs["robot_position"] == obs["target_position"]
        
        if render:
            if success:
                print(f"\n[SUCCESS] The robot reached the target in {step_count} steps.")
            else:
                print(f"\n[FAIL] Episode Finished. Failed to reach the target within {max_steps} steps.")
            print(f"Final Cumulative Reward: {total_reward:.2f}\n")
            
        return {
            "success": success,
            "steps": step_count,
            "total_reward": total_reward,
            "trajectory": trajectory
        }
