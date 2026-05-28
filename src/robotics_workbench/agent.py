from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract Base Class representing a robotics agent.
    All agents (heuristic, RL, or LLM-based) must inherit from this
    and implement the select_action method.
    """
    
    @abstractmethod
    def select_action(self, observation: Dict[str, Any]) -> str:
        """
        Determines the next action to take based on the environment observation.
        
        Args:
            observation (Dict[str, Any]): The current state dictionary from the environment.
            
        Returns:
            str: The chosen action, e.g., 'UP', 'DOWN', 'LEFT', or 'RIGHT'.
        """
        pass


class SimpleAgent(BaseAgent):
    """
    A rule-based heuristic agent that solves the grid navigation task.
    It calculates the difference in coordinates between the robot and target
    and chooses actions to reduce Manhattan distance.
    """
    def __init__(self, name: str = "SimpleHeuristicAgent"):
        self.name = name

    def select_action(self, observation: Dict[str, Any]) -> str:
        """
        Selects an action to move closer to the target position.
        
        Args:
            observation (Dict[str, Any]): Dictionary containing robot_position (x, y) 
                                           and target_position (x, y).
        Returns:
            str: Action to execute.
        """
        rx, ry = observation["robot_position"]
        tx, ty = observation["target_position"]
        
        # Navigate horizontally first, then vertically
        if rx < tx:
            return "RIGHT"
        elif rx > tx:
            return "LEFT"
        elif ry < ty:
            return "DOWN"
        elif ry > ty:
            return "UP"
            
        # If already at the target (this should theoretically terminate the episode),
        # return a default move.
        return "UP"
