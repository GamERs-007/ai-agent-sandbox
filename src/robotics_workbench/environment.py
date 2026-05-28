import random
from typing import Tuple, Dict, Any

class GridEnvironment:
    """
    A simple 2D Grid Environment for a robot simulation.
    The coordinate system starts at (0, 0) in the top-left corner.
    x-axis goes right (columns), y-axis goes down (rows).
    
    This class follows the standard OpenAI Gym API design:
    - reset(): returns initial observation.
    - step(action): executes an action, updates state, returns (obs, reward, done, info).
    """
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.robot_pos = (0, 0)
        self.target_pos = (0, 0)
        self.steps_taken = 0
        self.reset()

    def reset(self) -> Dict[str, Any]:
        """
        Resets the environment. Places the robot at (0, 0)
        and the target at a random location (excluding the robot position).
        
        Returns:
            Dict[str, Any]: The initial observation of the environment state.
        """
        self.robot_pos = (0, 0)
        self.steps_taken = 0
        
        # Place target randomly, making sure it doesn't overlap with the robot
        while True:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            if (tx, ty) != self.robot_pos:
                self.target_pos = (tx, ty)
                break
        
        return self._get_observation()

    def _get_observation(self) -> Dict[str, Any]:
        """
        Returns the current state representation as an observation.
        This structured data is what agents (heuristic or LLM-based) will read.
        """
        return {
            "robot_position": self.robot_pos,
            "target_position": self.target_pos,
            "grid_size": (self.width, self.height),
        }

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Executes one step in the environment by applying the given movement action.
        
        Args:
            action (str): Direction to move. Valid values are 'UP', 'DOWN', 'LEFT', 'RIGHT'.
              
        Returns:
            Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
                - observation (Dict): Current positions of robot/target and grid dimensions.
                - reward (float): Reward obtained from this transition.
                - done (bool): True if target is reached or simulation finishes.
                - info (Dict): Diagnostic fields (e.g. if collision occurred).
        """
        self.steps_taken += 1
        action_upper = action.upper()
        
        # Determine displacement vector based on grid coordinates
        dx, dy = 0, 0
        if action_upper == "UP":
            dy = -1
        elif action_upper == "DOWN":
            dy = 1
        elif action_upper == "LEFT":
            dx = -1
        elif action_upper == "RIGHT":
            dx = 1
        else:
            raise ValueError(f"Invalid action: {action}. Expected UP, DOWN, LEFT, or RIGHT.")
            
        new_x = self.robot_pos[0] + dx
        new_y = self.robot_pos[1] + dy
        
        # Boundary checking: keep robot within grid dimensions
        collision = False
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.robot_pos = (new_x, new_y)
        else:
            collision = True  # Robot tried to walk off the grid, remains at current pos
            
        # Check goal condition
        reached_goal = (self.robot_pos == self.target_pos)
        
        # Calculate step reward
        # - Success (reaching target): +10.0
        # - Collision (stepping out of bounds): -1.0
        # - Standard step penalty (to promote efficient pathfinding): -0.1
        if reached_goal:
            reward = 10.0
            done = True
        elif collision:
            reward = -1.0
            done = False
        else:
            reward = -0.1
            done = False
            
        obs = self._get_observation()
        info = {
            "collision": collision,
            "reached_goal": reached_goal,
            "steps": self.steps_taken
        }
        
        return obs, reward, done, info

    def render_ascii(self) -> str:
        """
        Generates an ASCII text representation of the grid.
        'R' = Robot, 'T' = Target, '.' = Empty space
        
        Returns:
            str: Plottable string of the grid.
        """
        grid_str = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                pos = (x, y)
                if pos == self.robot_pos:
                    row.append("R")
                elif pos == self.target_pos:
                    row.append("T")
                else:
                    row.append(".")
            grid_str.append(" ".join(row))
        return "\n".join(grid_str)
