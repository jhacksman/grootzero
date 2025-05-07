"""
Tests for the GR00T N1 mock interface.
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest
from typing import Dict, Any, List

from grootzero.groot_n1.interface import GR00TN1Interface
from grootzero.groot_n1.mock import MockGR00TN1


class TestMockGR00TN1(unittest.TestCase):
    """Tests for the MockGR00TN1 class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_groot = MockGR00TN1()
    
    def test_initialization(self):
        """Test initialization of MockGR00TN1."""
        self.assertIsInstance(self.mock_groot, GR00TN1Interface)
        self.assertEqual(self.mock_groot.task_selection_mode, "sequential")
        self.assertEqual(self.mock_groot.controller_selection_mode, "sequential")
        self.assertEqual(self.mock_groot.task_counter, 0)
        self.assertEqual(self.mock_groot.controller_counter, 0)
        self.assertEqual(len(self.mock_groot.learning_history), 0)
        
        custom_tasks = [{"task_id": "custom_task", "task_description": "Custom task"}]
        custom_controllers = ["def custom_controller(): pass"]
        
        custom_mock = MockGR00TN1(
            predefined_tasks=custom_tasks,
            predefined_controllers=custom_controllers,
            task_selection_mode="random",
            controller_selection_mode="match_task"
        )
        
        self.assertEqual(custom_mock.predefined_tasks, custom_tasks)
        self.assertEqual(custom_mock.predefined_controllers, custom_controllers)
        self.assertEqual(custom_mock.task_selection_mode, "random")
        self.assertEqual(custom_mock.controller_selection_mode, "match_task")
    
    def test_propose_task_sequential(self):
        """Test propose_task with sequential selection mode."""
        tasks = [
            {"task_id": "task1", "task_description": "Task 1"},
            {"task_id": "task2", "task_description": "Task 2"}
        ]
        mock_groot = MockGR00TN1(predefined_tasks=tasks, task_selection_mode="sequential")
        
        context = {"difficulty_level": "medium"}
        task1 = mock_groot.propose_task(context)
        self.assertEqual(task1["task_description"], "Task 1")
        
        task2 = mock_groot.propose_task(context)
        self.assertEqual(task2["task_description"], "Task 2")
        
        task3 = mock_groot.propose_task(context)
        self.assertEqual(task3["task_description"], "Task 1")
    
    def test_propose_task_random(self):
        """Test propose_task with random selection mode."""
        tasks = [
            {"task_id": "task1", "task_description": "Task 1"},
            {"task_id": "task2", "task_description": "Task 2"},
            {"task_id": "task3", "task_description": "Task 3"}
        ]
        mock_groot = MockGR00TN1(predefined_tasks=tasks, task_selection_mode="random")
        
        for _ in range(10):
            context = {"difficulty_level": "medium"}
            task = mock_groot.propose_task(context)
            self.assertIn(task["task_description"], ["Task 1", "Task 2", "Task 3"])
    
    def test_propose_task_difficulty(self):
        """Test propose_task with difficulty selection mode."""
        tasks = [
            {"task_id": "task1", "task_description": "Easy Task", "difficulty": "easy"},
            {"task_id": "task2", "task_description": "Medium Task", "difficulty": "medium"},
            {"task_id": "task3", "task_description": "Hard Task", "difficulty": "hard"}
        ]
        mock_groot = MockGR00TN1(predefined_tasks=tasks, task_selection_mode="difficulty")
        
        context = {"difficulty_level": "easy"}
        task = mock_groot.propose_task(context)
        self.assertEqual(task["task_description"], "Easy Task")
        
        context = {"difficulty_level": "medium"}
        task = mock_groot.propose_task(context)
        self.assertEqual(task["task_description"], "Medium Task")
        
        context = {"difficulty_level": "hard"}
        task = mock_groot.propose_task(context)
        self.assertEqual(task["task_description"], "Hard Task")
    
    def test_generate_controller_code_sequential(self):
        """Test generate_controller_code with sequential selection mode."""
        controllers = [
            "def controller1(): pass",
            "def controller2(): pass"
        ]
        mock_groot = MockGR00TN1(
            predefined_controllers=controllers, 
            controller_selection_mode="sequential"
        )
        
        task_params = {"task_id": "task1", "task_description": "Task 1"}
        controller1 = mock_groot.generate_controller_code(task_params)
        self.assertEqual(controller1, "def controller1(): pass")
        
        controller2 = mock_groot.generate_controller_code(task_params)
        self.assertEqual(controller2, "def controller2(): pass")
        
        controller3 = mock_groot.generate_controller_code(task_params)
        self.assertEqual(controller3, "def controller1(): pass")
    
    def test_generate_controller_code_random(self):
        """Test generate_controller_code with random selection mode."""
        controllers = [
            "def controller1(): pass",
            "def controller2(): pass",
            "def controller3(): pass"
        ]
        mock_groot = MockGR00TN1(
            predefined_controllers=controllers, 
            controller_selection_mode="random"
        )
        
        for _ in range(10):
            task_params = {"task_id": "task1", "task_description": "Task 1"}
            controller = mock_groot.generate_controller_code(task_params)
            self.assertIn(controller, controllers)
    
    def test_generate_controller_code_match_task(self):
        """Test generate_controller_code with match_task selection mode."""
        controllers = [
            "def pick_and_place_controller(): pass",
            "def navigation_controller(): pass",
            "def manipulation_controller(): pass"
        ]
        mock_groot = MockGR00TN1(
            predefined_controllers=controllers, 
            controller_selection_mode="match_task"
        )
        
        task_params = {"task_id": "task1", "task_description": "Task 1", "task_type": "pick_and_place"}
        controller = mock_groot.generate_controller_code(task_params)
        self.assertEqual(controller, "def pick_and_place_controller(): pass")
        
        task_params = {"task_id": "task2", "task_description": "Task 2", "task_type": "navigation"}
        controller = mock_groot.generate_controller_code(task_params)
        self.assertEqual(controller, "def navigation_controller(): pass")
    
    def test_controller_code_placeholder_replacement(self):
        """Test that placeholders in controller code are replaced with task-specific values."""
        controllers = [
            "def controller():\n    # Task: TASK_DESCRIPTION_PLACEHOLDER\n    target_pos = TARGET_POSITION_PLACEHOLDER"
        ]
        mock_groot = MockGR00TN1(predefined_controllers=controllers)
        
        task_params = {
            "task_id": "task1",
            "task_description": "Move the cube",
            "robot_goal": {
                "target_position": [1.0, 2.0, 3.0]
            }
        }
        
        controller = mock_groot.generate_controller_code(task_params)
        self.assertIn("# Task: Move the cube", controller)
        self.assertIn("target_pos = [1.0, 2.0, 3.0]", controller)
    
    def test_evaluate_controller(self):
        """Test evaluate_controller method."""
        mock_groot = MockGR00TN1()
        
        task_params = {"task_id": "task1", "task_description": "Task 1"}
        controller_code = "def controller(): pass"
        execution_results = {
            "success": True,
            "metrics": {
                "time_to_completion": 5.0,
                "path_efficiency": 0.8
            }
        }
        
        evaluation = mock_groot.evaluate_controller(task_params, controller_code, execution_results)
        
        self.assertTrue(evaluation["success"])
        self.assertGreaterEqual(evaluation["score"], 0.0)
        self.assertLessEqual(evaluation["score"], 1.0)
        self.assertIn("successfully", evaluation["feedback"])
        
        execution_results["success"] = False
        evaluation = mock_groot.evaluate_controller(task_params, controller_code, execution_results)
        
        self.assertFalse(evaluation["success"])
        self.assertGreaterEqual(evaluation["score"], 0.0)
        self.assertLessEqual(evaluation["score"], 1.0)
        self.assertIn("failed", evaluation["feedback"])
        self.assertTrue(len(evaluation["improvement_suggestions"]) > 0)
    
    def test_update_learning(self):
        """Test update_learning method."""
        mock_groot = MockGR00TN1()
        
        self.assertEqual(len(mock_groot.learning_history), 0)
        
        task_params = {"task_id": "task1", "task_description": "Task 1"}
        controller_code = "def controller(): pass"
        evaluation_results = {
            "success": True,
            "score": 0.9,
            "feedback": "Good job!",
            "improvement_suggestions": []
        }
        
        mock_groot.update_learning(task_params, controller_code, evaluation_results)
        
        self.assertEqual(len(mock_groot.learning_history), 1)
        self.assertEqual(mock_groot.learning_history[0]["task_id"], "task1")
        self.assertEqual(mock_groot.learning_history[0]["success"], True)
        self.assertEqual(mock_groot.learning_history[0]["score"], 0.9)
        
        task_params = {"task_id": "task2", "task_description": "Task 2"}
        evaluation_results["success"] = False
        evaluation_results["score"] = 0.2
        
        mock_groot.update_learning(task_params, controller_code, evaluation_results)
        
        self.assertEqual(len(mock_groot.learning_history), 2)
        self.assertEqual(mock_groot.learning_history[1]["task_id"], "task2")
        self.assertEqual(mock_groot.learning_history[1]["success"], False)
        self.assertEqual(mock_groot.learning_history[1]["score"], 0.2)
    
    def test_task_structure(self):
        """Test that proposed tasks have the expected structure."""
        mock_groot = MockGR00TN1()
        
        context = {"difficulty_level": "medium"}
        task = mock_groot.propose_task(context)
        
        self.assertIn("task_id", task)
        self.assertIn("task_description", task)
        self.assertIn("scene_config", task)
        self.assertIn("robot_goal", task)
        self.assertIn("domain_randomization_settings", task)
        self.assertIn("success_criteria_description", task)
        
        self.assertTrue(task["task_id"].startswith("mock_task_"))
        self.assertEqual(len(task["task_id"]), 17)  # "mock_task_" + 8 hex chars
        
        self.assertIn("objects_to_spawn", task["scene_config"])
        self.assertTrue(isinstance(task["scene_config"]["objects_to_spawn"], list))
        
        self.assertIn("target_position", task["robot_goal"])
        self.assertTrue(isinstance(task["robot_goal"]["target_position"], list))
        self.assertEqual(len(task["robot_goal"]["target_position"]), 3)  # x, y, z
    
    def test_controller_code_structure(self):
        """Test that generated controller code has the expected structure."""
        mock_groot = MockGR00TN1()
        
        task_params = {
            "task_id": "task1",
            "task_description": "Move the cube",
            "robot_goal": {
                "target_position": [1.0, 2.0, 3.0]
            }
        }
        
        controller_code = mock_groot.generate_controller_code(task_params)
        
        self.assertTrue(isinstance(controller_code, str))
        self.assertTrue(len(controller_code) > 0)
        
        self.assertIn("def execute_controller", controller_code)
        
        self.assertIn("robot_interface", controller_code)
        self.assertIn("world_state", controller_code)
        
        self.assertIn("return", controller_code)
        self.assertTrue(
            "return \"success\"" in controller_code or 
            "return \"failure\"" in controller_code or 
            "return \"running\"" in controller_code
        )


if __name__ == "__main__":
    unittest.main()
