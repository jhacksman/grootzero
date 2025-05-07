"""
Basic test script for GR00T N1 mock interface.

This script demonstrates the basic usage of the MockGR00TN1 class
for task proposal and controller generation.
"""

import os
import sys
import argparse
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grootzero.groot_n1.mock import MockGR00TN1
from grootzero.logging import setup_logging, get_logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Basic test for GR00T N1 mock interface")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--task-selection", type=str, default="sequential", 
                       choices=["sequential", "random", "difficulty"],
                       help="Task selection mode")
    parser.add_argument("--controller-selection", type=str, default="sequential", 
                       choices=["sequential", "random", "match_task"],
                       help="Controller selection mode")
    parser.add_argument("--difficulty", type=str, default="medium", 
                       choices=["easy", "medium", "hard"],
                       help="Difficulty level for tasks")
    parser.add_argument("--num-tasks", type=int, default=3, 
                       help="Number of tasks to generate")
    return parser.parse_args()


def main():
    """Main function for the basic GR00T N1 mock test."""
    args = parse_args()
    
    setup_logging(log_level=args.log_level)
    logger = get_logger("basic_mock_test")
    
    logger.info("Starting basic GR00T N1 mock test")
    logger.info(f"Task selection mode: {args.task_selection}")
    logger.info(f"Controller selection mode: {args.controller_selection}")
    logger.info(f"Difficulty level: {args.difficulty}")
    
    mock_groot = MockGR00TN1(
        task_selection_mode=args.task_selection,
        controller_selection_mode=args.controller_selection
    )
    
    for i in range(args.num_tasks):
        logger.info(f"\n--- Task {i+1}/{args.num_tasks} ---")
        
        context = {
            "difficulty_level": args.difficulty,
            "previous_task_ids": [f"mock_task_{j}" for j in range(i)],
            "learning_history": []
        }
        
        logger.info("Proposing task...")
        task_params = mock_groot.propose_task(context)
        
        logger.info(f"Task ID: {task_params['task_id']}")
        logger.info(f"Task Description: {task_params['task_description']}")
        logger.info(f"Robot Goal: {task_params['robot_goal']}")
        
        logger.info("\nGenerating controller code...")
        controller_code = mock_groot.generate_controller_code(task_params)
        
        code_snippet = "\n".join(controller_code.split("\n")[:10]) + "\n..."
        logger.info(f"Controller Code Snippet:\n{code_snippet}")
        
        execution_results = {
            "success": i % 2 == 0,  # Alternate success/failure for demonstration
            "metrics": {
                "time_to_completion": 5.0 + i * 2.0,
                "path_efficiency": 0.7 - (i * 0.1)
            }
        }
        
        logger.info("\nEvaluating controller...")
        evaluation = mock_groot.evaluate_controller(
            task_params, controller_code, execution_results
        )
        
        logger.info(f"Success: {evaluation['success']}")
        logger.info(f"Score: {evaluation['score']:.2f}")
        logger.info(f"Feedback: {evaluation['feedback']}")
        logger.info(f"Improvement Suggestions: {evaluation['improvement_suggestions']}")
        
        logger.info("\nUpdating learning state...")
        mock_groot.update_learning(task_params, controller_code, evaluation)
        
        logger.info(f"Learning history size: {len(mock_groot.learning_history)}")
    
    logger.info("\nBasic GR00T N1 mock test completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
