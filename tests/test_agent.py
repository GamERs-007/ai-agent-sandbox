import os
import sys
import unittest

# Append parent directories to path so Python can resolve imports correctly during testing
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "src"))

from robotics_workbench.agent import SimpleAgent

class TestSimpleAgent(unittest.TestCase):
    def test_heuristic_agent_decisions(self) -> None:
        """
        Verifies that SimpleAgent makes the correct coordinate-reducing decisions
        based on relative target placements.
        """
        agent = SimpleAgent()
        
        # Target is to the right
        obs = {
            "robot_position": (1, 1),
            "target_position": (3, 1),
            "grid_size": (5, 5)
        }
        self.assertEqual(agent.select_action(obs), "RIGHT")
        
        # Target is to the left
        obs = {
            "robot_position": (3, 1),
            "target_position": (1, 1),
            "grid_size": (5, 5)
        }
        self.assertEqual(agent.select_action(obs), "LEFT")
        
        # Target is below (when x aligns)
        obs = {
            "robot_position": (2, 1),
            "target_position": (2, 3),
            "grid_size": (5, 5)
        }
        self.assertEqual(agent.select_action(obs), "DOWN")
        
        # Target is above (when x aligns)
        obs = {
            "robot_position": (2, 3),
            "target_position": (2, 1),
            "grid_size": (5, 5)
        }
        self.assertEqual(agent.select_action(obs), "UP")

if __name__ == "__main__":
    unittest.main()
