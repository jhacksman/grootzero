"""
Reward functions for the AZR learning loop.

This module provides functions for calculating rewards based on
simulation execution results, to be used in reinforcement learning
feedback mechanisms.
"""

from typing import Dict, Any, Union, List, Optional
import math

from grootzero.logging import get_logger


def calculate_reward(execution_results: Dict[str, Any], 
                    task_parameters: Optional[Dict[str, Any]] = None) -> float:
    """
    Calculate a reward based on simulation execution results.
    
    This function implements a simple reward calculation that considers:
    1. Binary success/failure (+1 for success, -1 for failure)
    2. Time efficiency (bonus for completing tasks quickly)
    3. Path efficiency (bonus for efficient movement)
    4. Energy efficiency (bonus for energy-efficient solutions)
    
    Args:
        execution_results: Dictionary containing results from executing a controller
            - success: Boolean indicating whether the controller succeeded
            - metrics: Dictionary of metrics collected during execution
                - time_to_completion: Time taken to complete the task
                - steps_to_completion: Number of steps taken to complete the task
                - path_efficiency: Efficiency of the path taken (0.0 to 1.0)
                - energy_efficiency: Energy efficiency of the solution (0.0 to 1.0)
        task_parameters: Optional dictionary containing task parameters,
            which can be used to adjust rewards based on task difficulty
    
    Returns:
        Calculated reward value as a float
    """
    logger = get_logger("reward_function")
    
    success = execution_results.get("success", False)
    base_reward = 1.0 if success else -1.0
    
    total_reward = base_reward
    
    metrics = execution_results.get("metrics", {})
    
    if success and "time_to_completion" in metrics:
        time_taken = metrics["time_to_completion"]
        time_bonus = min(0.5, 5.0 / max(1.0, time_taken))
        total_reward += time_bonus
        logger.debug(f"Time efficiency bonus: {time_bonus:.2f}")
    
    if success and "path_efficiency" in metrics:
        path_efficiency = metrics["path_efficiency"]
        path_bonus = path_efficiency * 0.3
        total_reward += path_bonus
        logger.debug(f"Path efficiency bonus: {path_bonus:.2f}")
    
    if success and "energy_efficiency" in metrics:
        energy_efficiency = metrics["energy_efficiency"]
        energy_bonus = energy_efficiency * 0.2
        total_reward += energy_bonus
        logger.debug(f"Energy efficiency bonus: {energy_bonus:.2f}")
    
    if task_parameters and "difficulty" in task_parameters:
        difficulty = task_parameters["difficulty"]
        difficulty_multiplier = 1.0
        
        if difficulty == "easy":
            difficulty_multiplier = 0.8  # Reduce reward for easy tasks
        elif difficulty == "medium":
            difficulty_multiplier = 1.0  # No change for medium tasks
        elif difficulty == "hard":
            difficulty_multiplier = 1.2  # Increase reward for hard tasks
        
        total_reward *= difficulty_multiplier
        logger.debug(f"Difficulty adjustment: {difficulty} (x{difficulty_multiplier:.1f})")
    
    logger.info(f"Calculated reward: {total_reward:.2f} (base: {base_reward:.1f})")
    return total_reward


def calculate_normalized_reward(execution_results: Dict[str, Any],
                               task_parameters: Optional[Dict[str, Any]] = None) -> float:
    """
    Calculate a normalized reward (between -1 and +1) based on simulation execution results.
    
    This is a wrapper around calculate_reward that ensures the reward is normalized
    to a range of -1 to +1, which can be useful for some RL algorithms.
    
    Args:
        execution_results: Dictionary containing results from executing a controller
        task_parameters: Optional dictionary containing task parameters
    
    Returns:
        Normalized reward value as a float between -1 and +1
    """
    raw_reward = calculate_reward(execution_results, task_parameters)
    
    normalized_reward = math.tanh(raw_reward)
    
    logger = get_logger("reward_function")
    logger.debug(f"Normalized reward: {normalized_reward:.2f} (from raw: {raw_reward:.2f})")
    
    return normalized_reward
