"""
Unit tests for the AZR reward functions.

This module contains tests for the reward calculation functions used in the
reinforcement learning feedback mechanism.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grootzero.azr.rewards import calculate_reward, calculate_normalized_reward


class TestRewardFunctions(unittest.TestCase):
    """Test cases for the reward calculation functions."""
    
    def test_calculate_reward_success(self):
        """Test reward calculation for successful execution."""
        execution_results = {
            "success": True,
            "metrics": {
                "time_to_completion": 2.5,
                "path_efficiency": 0.8,
                "energy_efficiency": 0.7
            }
        }
        
        reward = calculate_reward(execution_results)
        
        self.assertAlmostEqual(reward, 1.88, places=2)
    
    def test_calculate_reward_failure(self):
        """Test reward calculation for failed execution."""
        execution_results = {
            "success": False,
            "metrics": {}
        }
        
        reward = calculate_reward(execution_results)
        
        self.assertEqual(reward, -1.0)
    
    def test_calculate_reward_with_difficulty(self):
        """Test reward calculation with difficulty adjustment."""
        execution_results = {
            "success": True,
            "metrics": {
                "time_to_completion": 2.0,
                "path_efficiency": 0.5,
                "energy_efficiency": 0.5
            }
        }
        
        task_parameters = {"difficulty": "easy"}
        reward_easy = calculate_reward(execution_results, task_parameters)
        
        task_parameters = {"difficulty": "medium"}
        reward_medium = calculate_reward(execution_results, task_parameters)
        
        task_parameters = {"difficulty": "hard"}
        reward_hard = calculate_reward(execution_results, task_parameters)
        
        self.assertLess(reward_easy, reward_medium)
        self.assertLess(reward_medium, reward_hard)
    
    def test_calculate_normalized_reward(self):
        """Test normalized reward calculation."""
        execution_results = {
            "success": True,
            "metrics": {
                "time_to_completion": 1.0,
                "path_efficiency": 1.0,
                "energy_efficiency": 1.0
            }
        }
        
        reward = calculate_normalized_reward(execution_results)
        
        self.assertGreaterEqual(reward, -1.0)
        self.assertLessEqual(reward, 1.0)
        
        self.assertGreater(reward, 0.9)
        
        execution_results = {"success": False, "metrics": {}}
        reward = calculate_normalized_reward(execution_results)
        
        self.assertLess(reward, 0.0)


if __name__ == "__main__":
    unittest.main()
