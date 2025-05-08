"""
Basic test script for the AZR learning loop.

This script demonstrates the basic usage of the AZRLearningLoop class
for orchestrating the interaction between the GR00T N1 foundation model
and the Isaac Sim simulation environment.
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
    parser = argparse.ArgumentParser(description="Basic test for AZR learning loop")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--config-path", type=str, default=None, help="Path to configuration file")
    parser.add_argument("--mock-simulation", action="store_true", help="Use mock simulation environment")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--num-episodes", type=int, default=3, help="Number of episodes to run")
    parser.add_argument("--task-selection", type=str, default="sequential", 
                       choices=["sequential", "random", "difficulty"],
                       help="Task selection mode for MockGR00TN1")
    parser.add_argument("--controller-selection", type=str, default="sequential", 
                       choices=["sequential", "random", "match_task"],
                       help="Controller selection mode for MockGR00TN1")
    parser.add_argument("--difficulty", type=str, default="medium", 
                       choices=["easy", "medium", "hard"],
                       help="Initial difficulty level")
    return parser.parse_args()


def main():
    """Main function for the basic AZR learning loop test."""
    args = parse_args()
    
    setup_logging(log_level=args.log_level)
    logger = get_logger("basic_learning_loop_test")
    
    logger.info("Starting basic AZR learning loop test")
    logger.info(f"Mock simulation: {args.mock_simulation}")
    logger.info(f"Number of episodes: {args.num_episodes}")
    
    logger.info("Creating MockGR00TN1 instance")
    mock_groot = MockGR00TN1(
        task_selection_mode=args.task_selection,
        controller_selection_mode=args.controller_selection
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
    
    learning_loop.current_context["difficulty_level"] = args.difficulty
    
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
        
        for i, result in enumerate(episode_results):
            task_id = result["task_parameters"]["task_id"]
            task_desc = result["task_parameters"]["task_description"]
            success = result["evaluation_results"].get("success", False)
            score = result["evaluation_results"].get("score", 0.0)
            
            logger.info(f"Episode {i+1}: Task {task_id} - {task_desc}")
            logger.info(f"  Success: {success}, Score: {score:.2f}")
            
            if "metrics" in result["execution_results"]:
                metrics = result["execution_results"]["metrics"]
                logger.info(f"  Time: {metrics.get('time_to_completion', 0.0):.2f}s, "
                           f"Steps: {metrics.get('steps_to_completion', 0)}")
        
    finally:
        logger.info("Closing learning loop")
        learning_loop.close()
    
    logger.info("Basic AZR learning loop test completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
