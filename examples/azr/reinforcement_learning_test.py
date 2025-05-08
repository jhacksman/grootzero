"""
Test script for the AZR learning loop with reinforcement learning feedback.

This script demonstrates the basic usage of the AZRLearningLoop class
with the reinforcement learning feedback mechanism for controller selection.
"""

import os
import sys
import argparse
import time
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grootzero.azr.orchestrator import AZRLearningLoop
from grootzero.groot_n1.mock import MockGR00TN1
from grootzero.simulation.environment import SimulationEnvironment
from grootzero.logging import setup_logging, get_logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test for AZR learning loop with RL feedback")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--config-path", type=str, default=None, help="Path to configuration file")
    parser.add_argument("--mock-simulation", action="store_true", help="Use mock simulation environment")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--num-episodes", type=int, default=10, help="Number of episodes to run")
    parser.add_argument("--controller-selection", type=str, default="random", 
                       choices=["sequential", "random", "match_task"],
                       help="Controller selection mode for MockGR00TN1")
    parser.add_argument("--learning-rate", type=float, default=0.1,
                       help="Learning rate for RL feedback (0.0 to 1.0)")
    return parser.parse_args()


def main():
    """Main function for the RL feedback test."""
    args = parse_args()
    
    setup_logging(log_level=args.log_level)
    logger = get_logger("reinforcement_learning_test")
    
    logger.info("Starting AZR learning loop test with RL feedback")
    logger.info(f"Mock simulation: {args.mock_simulation}")
    logger.info(f"Number of episodes: {args.num_episodes}")
    logger.info(f"Controller selection mode: {args.controller_selection}")
    logger.info(f"Learning rate: {args.learning_rate}")
    
    logger.info("Creating MockGR00TN1 instance")
    mock_groot = MockGR00TN1(
        controller_selection_mode=args.controller_selection,
        learning_rate=args.learning_rate
    )
    
    logger.info("Creating SimulationEnvironment instance")
    sim_env = SimulationEnvironment(
        config_path=args.config_path,
        mock_mode=args.mock_simulation
    )
    
    logger.info("Creating AZRLearningLoop instance")
    learning_loop = AZRLearningLoop(
        gr00t_n1=mock_groot,
        sim_env=sim_env,
        config_path=args.config_path,
        mock_simulation=args.mock_simulation,
        headless=args.headless
    )
    
    try:
        logger.info(f"Running learning loop for {args.num_episodes} episodes")
        start_time = time.time()
        
        episode_results = learning_loop.run(args.num_episodes)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        logger.info(f"Learning loop completed in {elapsed_time:.2f} seconds")
        logger.info(f"Completed {len(episode_results)} episodes")
        
        success_count = sum(1 for result in episode_results 
                          if result["evaluation_results"].get("success", False))
        success_rate = success_count / len(episode_results) if episode_results else 0
        
        logger.info(f"Success rate: {success_rate:.2f} ({success_count}/{len(episode_results)})")
        
        logger.info("Controller selection weights after learning:")
        for i, weight in enumerate(mock_groot.controller_selection_weights):
            logger.info(f"  Controller {i}: {weight:.2f}")
        
        logger.info("Task type to controller mapping after learning:")
        for task_type, controllers in mock_groot.task_type_controller_map.items():
            logger.info(f"  Task type '{task_type}': {controllers}")
        
        logger.info("\nDetailed episode results:")
        for i, result in enumerate(episode_results):
            task_id = result["task_parameters"]["task_id"]
            task_desc = result["task_parameters"]["task_description"]
            success = result["evaluation_results"].get("success", False)
            score = result["evaluation_results"].get("score", 0.0)
            reward = result.get("reward", 0.0)
            
            logger.info(f"Episode {i+1}: Task {task_id} - {task_desc}")
            logger.info(f"  Success: {success}, Score: {score:.2f}, Reward: {reward:.2f}")
            
            if "metrics" in result["execution_results"]:
                metrics = result["execution_results"]["metrics"]
                logger.info(f"  Time: {metrics.get('time_to_completion', 0.0):.2f}s, "
                           f"Steps: {metrics.get('steps_to_completion', 0)}")
        
    finally:
        logger.info("Closing learning loop")
        learning_loop.close()
    
    logger.info("AZR learning loop test with RL feedback completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
