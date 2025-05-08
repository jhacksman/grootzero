"""
Unit tests for the AZR learning loop orchestrator.

This module contains tests for the AZRLearningLoop class and related functionality.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grootzero.azr.orchestrator import AZRLearningLoop, RobotInterface
from grootzero.groot_n1.interface import GR00TN1Interface
from grootzero.simulation.environment import SimulationEnvironment


class MockGR00TN1(GR00TN1Interface):
    """Mock implementation of GR00TN1Interface for testing."""
    
    def propose_task(self, current_context):
        return {
            "task_id": "test_task_1",
            "task_description": "Test task",
            "scene_config": {"environment": "test_env"},
            "robot_config": {
                "name": "test_robot",
                "type": "test_type",
                "position": [0, 0, 0]
            },
            "robot_goal": "Reach the target",
            "domain_randomization_settings": {"enabled": True},
            "success_criteria_description": "Robot reaches the target"
        }
    
    def generate_controller_code(self, task_parameters):
        return """
def execute_controller(robot, world_state):
    robot.apply_action({"joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]})
    
    if world_state["step_count"] > 10:
        return "success"
    
    return "continue"
"""
    
    def evaluate_controller(self, task_parameters, controller_code, execution_results):
        return {
            "success": execution_results.get("success", False),
            "score": 0.8 if execution_results.get("success", False) else 0.2,
            "feedback": "Good job!" if execution_results.get("success", False) else "Try again",
            "improvement_suggestions": []
        }
    
    def update_learning(self, task_parameters, controller_code, evaluation_results):
        pass


class TestAZRLearningLoop(unittest.TestCase):
    """Test cases for the AZRLearningLoop class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_gr00t_n1 = MockGR00TN1()
        self.mock_sim_env = MagicMock(spec=SimulationEnvironment)
        self.mock_sim_env.initialize.return_value = True
        self.mock_sim_env.load_environment.return_value = True
        self.mock_sim_env.create_robot.return_value = "test_robot_id"
        self.mock_sim_env.apply_domain_randomization.return_value = True
        self.mock_sim_env.reset.return_value = {"test_robot_id": {"position": [0, 0, 0]}}
        self.mock_sim_env.step.return_value = (
            {"test_robot_id": {"position": [1, 1, 1]}},
            {"test_robot_id": 0.5},
            {"test_robot_id": False},
            {"step": 1}
        )
        self.mock_sim_env.get_observations.return_value = {
            "test_robot_id": {
                "position": [1, 1, 1],
                "end_effector_position": [2, 2, 2],
                "joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
            }
        }
        
        self.config = {
            "azr": {
                "max_episodes": 5,
                "max_steps_per_episode": 20,
                "initial_difficulty": "easy"
            }
        }
        
        with patch('grootzero.config.load_config', return_value=self.config):
            self.learning_loop = AZRLearningLoop(
                gr00t_n1=self.mock_gr00t_n1,
                sim_env=self.mock_sim_env
            )
    
    def test_init(self):
        """Test initialization of AZRLearningLoop."""
        self.assertEqual(self.learning_loop.gr00t_n1, self.mock_gr00t_n1)
        self.assertEqual(self.learning_loop.sim_env, self.mock_sim_env)
        self.assertEqual(self.learning_loop.max_episodes, 5)
        self.assertEqual(self.learning_loop.episode_count, 0)
        self.assertEqual(self.learning_loop.current_context["difficulty_level"], "easy")
    
    def test_initialize(self):
        """Test initialization of the learning loop."""
        result = self.learning_loop.initialize()
        self.assertTrue(result)
        self.mock_sim_env.initialize.assert_called_once()
    
    def test_run_episode(self):
        """Test running a single episode."""
        with patch('grootzero.azr.orchestrator.importlib.util') as mock_importlib_util:
            mock_spec = MagicMock()
            mock_module = MagicMock()
            mock_importlib_util.spec_from_file_location.return_value = mock_spec
            mock_importlib_util.module_from_spec.return_value = mock_module
            
            def mock_execute_controller(robot, world_state):
                if world_state["step_count"] > 5:
                    return "success"
                return "continue"
            
            mock_module.execute_controller = mock_execute_controller
            
            result = self.learning_loop.run_episode()
            
            self.assertIn("task_parameters", result)
            self.assertIn("controller_code", result)
            self.assertIn("execution_results", result)
            self.assertIn("evaluation_results", result)
            
            self.mock_sim_env.load_environment.assert_called()
            self.mock_sim_env.create_robot.assert_called()
            self.mock_sim_env.apply_domain_randomization.assert_called()
            self.mock_sim_env.reset.assert_called()
            self.mock_sim_env.step.assert_called()
            
            self.assertEqual(self.learning_loop.episode_count, 1)
    
    def test_run(self):
        """Test running multiple episodes."""
        with patch.object(self.learning_loop, 'run_episode') as mock_run_episode:
            mock_run_episode.return_value = {"success": True}
            
            results = self.learning_loop.run(3)
            
            self.assertEqual(mock_run_episode.call_count, 3)
            
            self.assertEqual(len(results), 3)
    
    def test_close(self):
        """Test closing the learning loop."""
        self.learning_loop.close()
        self.mock_sim_env.close.assert_called_once()


class TestRobotInterface(unittest.TestCase):
    """Test cases for the RobotInterface class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_sim_env = MagicMock(spec=SimulationEnvironment)
        self.mock_sim_env.get_observations.return_value = {
            "test_robot_id": {
                "position": [1, 1, 1],
                "end_effector_position": [2, 2, 2],
                "joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
            }
        }
        
        self.robot_interface = RobotInterface(self.mock_sim_env, "test_robot_id")
    
    def test_get_end_effector_position(self):
        """Test getting the end effector position."""
        position = self.robot_interface.get_end_effector_position()
        self.assertEqual(position, [2, 2, 2])
    
    def test_get_joint_positions(self):
        """Test getting the joint positions."""
        positions = self.robot_interface.get_joint_positions()
        self.assertEqual(positions, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    
    def test_apply_action(self):
        """Test applying an action."""
        action = {"joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]}
        self.robot_interface.apply_action(action)
        self.assertEqual(self.robot_interface.actions, action)
        self.assertEqual(len(self.robot_interface.trajectory), 2)  # Initial position + new position
    
    def test_get_actions(self):
        """Test getting the current actions."""
        action = {"joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]}
        self.robot_interface.apply_action(action)
        actions = self.robot_interface.get_actions()
        self.assertEqual(actions, action)


if __name__ == "__main__":
    unittest.main()
