import os
import sys
import unittest

# Append parent directories to path so Python can resolve imports correctly during testing
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "src"))

from robotics_workbench.environment import GridEnvironment

class TestGridEnvironment(unittest.TestCase):
    def test_environment_initialization(self) -> None:
        """Verifies that the GridEnvironment initializes with correct default states and bounds."""
        env = GridEnvironment(width=5, height=7)
        self.assertEqual(env.width, 5)
        self.assertEqual(env.height, 7)
        self.assertEqual(env.robot_pos, (0, 0))
        self.assertEqual(env.steps_taken, 0)
        # The target should not spawn directly on top of the robot
        self.assertNotEqual(env.target_pos, (0, 0))
        self.assertTrue(0 <= env.target_pos[0] < 5)
        self.assertTrue(0 <= env.target_pos[1] < 7)

    def test_environment_reset(self) -> None:
        """Verifies reset returns correct initial state observations."""
        env = GridEnvironment(width=10, height=10)
        obs = env.reset()
        self.assertEqual(obs["robot_position"], (0, 0))
        self.assertEqual(obs["grid_size"], (10, 10))
        self.assertIn("target_position", obs)
        self.assertEqual(env.steps_taken, 0)

    def test_environment_movement_transitions(self) -> None:
        """Verifies that legal step actions properly transition the robot's coordinates."""
        env = GridEnvironment(width=5, height=5)
        env.robot_pos = (2, 2)
        env.target_pos = (4, 4)  # Place target away to avoid immediate goal trigger
        
        obs, reward, done, info = env.step("RIGHT")
        self.assertEqual(env.robot_pos, (3, 2))
        self.assertEqual(reward, -0.1)  # Standard step penalty
        self.assertFalse(done)
        self.assertFalse(info["collision"])
        
        obs, reward, done, info = env.step("DOWN")
        self.assertEqual(env.robot_pos, (3, 3))
        self.assertEqual(reward, -0.1)
        self.assertFalse(done)
        self.assertFalse(info["collision"])

    def test_environment_boundary_collisions(self) -> None:
        """Verifies that moving out of bounds does not change robot position and inflicts penalty."""
        env = GridEnvironment(width=5, height=5)
        env.robot_pos = (0, 0)
        env.target_pos = (2, 2)
        
        # Try moving UP from (0,0) - out of bounds
        obs, reward, done, info = env.step("UP")
        self.assertEqual(env.robot_pos, (0, 0))
        self.assertEqual(reward, -1.0)  # Collision penalty
        self.assertFalse(done)
        self.assertTrue(info["collision"])

    def test_environment_goal_reaching(self) -> None:
        """Verifies that hitting the target coordinates finishes the episode with a positive reward."""
        env = GridEnvironment(width=5, height=5)
        env.robot_pos = (3, 3)
        env.target_pos = (3, 4)
        
        obs, reward, done, info = env.step("DOWN")
        self.assertEqual(env.robot_pos, (3, 4))
        self.assertEqual(reward, 10.0)  # Success reward
        self.assertTrue(done)
        self.assertTrue(info["reached_goal"])

if __name__ == "__main__":
    unittest.main()
