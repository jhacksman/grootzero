"""
Unit tests for the reinforcement learning feedback mechanism.

This module contains tests for the RL feedback mechanism implemented in
the MockGR00TN1 class.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grootzero.groot_n1.mock import MockGR00TN1


class TestRLFeedback(unittest.TestCase):
    """Test cases for the reinforcement learning feedback mechanism."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_groot = MockGR00TN1(
            controller_selection_mode="random",
            learning_rate=0.2
        )
    
    def test_apply_reinforcement_feedback_positive(self):
        """Test applying positive reinforcement feedback."""
        task_parameters = {
            "task_id": "test_task_1",
            "task_type": "navigation",
            "task_description": "Test navigation task"
        }
        
        controller_code = "def execute_controller(robot, world_state): return 'success'"
        
        initial_weights = self.mock_groot.controller_selection_weights.copy()
        
        self.mock_groot.generate_controller_code(task_parameters)
        
        self.mock_groot.apply_reinforcement_feedback(
            task_parameters,
            controller_code,
            1.0  # Positive reward
        )
        
        task_id = task_parameters["task_id"]
        controller_index = self.mock_groot._last_selected_controller[task_id]
        
        self.assertGreater(
            self.mock_groot.controller_selection_weights[controller_index],
            initial_weights[controller_index]
        )
        
        self.assertIn("navigation", self.mock_groot.task_type_controller_map)
        self.assertIn(controller_index, self.mock_groot.task_type_controller_map["navigation"])
    
    def test_apply_reinforcement_feedback_negative(self):
        """Test applying negative reinforcement feedback."""
        task_parameters = {
            "task_id": "test_task_2",
            "task_type": "manipulation",
            "task_description": "Test manipulation task"
        }
        
        controller_code = "def execute_controller(robot, world_state): return 'failure'"
        
        initial_weights = self.mock_groot.controller_selection_weights.copy()
        
        self.mock_groot.generate_controller_code(task_parameters)
        
        self.mock_groot.apply_reinforcement_feedback(
            task_parameters,
            controller_code,
            -1.0  # Negative reward
        )
        
        task_id = task_parameters["task_id"]
        controller_index = self.mock_groot._last_selected_controller[task_id]
        
        self.assertLess(
            self.mock_groot.controller_selection_weights[controller_index],
            initial_weights[controller_index]
        )
        
        if "manipulation" in self.mock_groot.task_type_controller_map:
            self.assertNotIn(controller_index, self.mock_groot.task_type_controller_map["manipulation"])
    
    def test_learning_rate_effect(self):
        """Test the effect of different learning rates."""
        task_parameters = {
            "task_id": "test_task_3",
            "task_type": "grasping",
            "task_description": "Test grasping task"
        }
        
        controller_code = "def execute_controller(robot, world_state): return 'success'"
        
        mock_groot_low_lr = MockGR00TN1(
            controller_selection_mode="random",
            learning_rate=0.1
        )
        
        mock_groot_high_lr = MockGR00TN1(
            controller_selection_mode="random",
            learning_rate=0.5
        )
        
        mock_groot_low_lr.generate_controller_code(task_parameters)
        mock_groot_high_lr.generate_controller_code(task_parameters)
        
        mock_groot_low_lr.apply_reinforcement_feedback(
            task_parameters,
            controller_code,
            1.0
        )
        
        mock_groot_high_lr.apply_reinforcement_feedback(
            task_parameters,
            controller_code,
            1.0
        )
        
        task_id = task_parameters["task_id"]
        low_lr_index = mock_groot_low_lr._last_selected_controller[task_id]
        high_lr_index = mock_groot_high_lr._last_selected_controller[task_id]
        
        low_lr_weight_change = mock_groot_low_lr.controller_selection_weights[low_lr_index] - 1.0
        high_lr_weight_change = mock_groot_high_lr.controller_selection_weights[high_lr_index] - 1.0
        
        self.assertGreater(high_lr_weight_change, low_lr_weight_change)
    
    def test_controller_selection_probability(self):
        """Test that controller selection probability changes with feedback."""
        task_parameters = {
            "task_id": "test_task_4",
            "task_type": "navigation",
            "task_description": "Test navigation task"
        }
        
        controller_code = "def execute_controller(robot, world_state): return 'success'"
        
        self.mock_groot.controller_selection_weights = [1.0] * len(self.mock_groot.predefined_controllers)
        
        self.mock_groot.generate_controller_code(task_parameters)
        
        task_id = task_parameters["task_id"]
        controller_index = self.mock_groot._last_selected_controller[task_id]
        
        self.mock_groot.apply_reinforcement_feedback(
            task_parameters,
            controller_code,
            2.0  # Strong positive reward
        )
        
        total_weight = sum(self.mock_groot.controller_selection_weights)
        probabilities = [w / total_weight for w in self.mock_groot.controller_selection_weights]
        
        initial_probability = 1.0 / len(self.mock_groot.predefined_controllers)
        self.assertGreater(probabilities[controller_index], initial_probability)
        
        self.assertAlmostEqual(sum(probabilities), 1.0)


if __name__ == "__main__":
    unittest.main()
