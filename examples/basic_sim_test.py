"""
Basic test script for NVIDIA Isaac Sim integration.

This script demonstrates the basic usage of the SimulationEnvironment class
for initializing Isaac Sim, loading an environment, creating a robot,
applying domain randomization, and running a simple simulation loop.
"""

import os
import sys
import time
import argparse
from typing import Dict, Any

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from grootzero.simulation.environment import SimulationEnvironment
from grootzero.config import load_config
from grootzero.logging import setup_logging, get_logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Basic test for Isaac Sim integration")
    parser.add_argument("--mock", action="store_true", help="Use mock mode instead of real Isaac Sim")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no rendering)")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps to run")
    return parser.parse_args()


def main():
    """Main function for the basic simulation test."""
    args = parse_args()
    
    setup_logging(log_level=args.log_level)
    logger = get_logger("basic_sim_test")
    
    logger.info("Starting basic simulation test")
    logger.info(f"Mock mode: {args.mock}")
    logger.info(f"Headless mode: {args.headless}")
    
    try:
        logger.info("Creating simulation environment")
        env = SimulationEnvironment(config_path=args.config, mock_mode=args.mock)
        
        logger.info("Initializing simulation")
        if not env.initialize():
            logger.error("Failed to initialize simulation")
            return 1
        
        logger.info("Loading environment")
        if not env.load_environment():
            logger.error("Failed to load environment")
            return 1
        
        logger.info("Creating robot")
        robot_id = env.create_robot(
            robot_name="test_robot",
            robot_type="ur10",
            position=[0.0, 0.0, 0.0]
        )
        if not robot_id:
            logger.error("Failed to create robot")
            return 1
        
        logger.info("Applying domain randomization")
        if not env.apply_domain_randomization():
            logger.error("Failed to apply domain randomization")
            return 1
        
        logger.info("Resetting simulation")
        observations = env.reset()
        logger.info(f"Initial observations: {observations}")
        
        logger.info(f"Running simulation for {args.steps} steps")
        for i in range(args.steps):
            actions = {
                robot_id: {
                    "joint_positions": np.random.rand(6).tolist()
                }
            }
            
            observations, rewards, dones, info = env.step(actions)
            
            if i % 10 == 0:
                logger.info(f"Step {i}: Reward = {rewards.get(robot_id, 0.0)}")
            
            if dones.get(robot_id, False):
                logger.info(f"Simulation done at step {i}")
                break
        
        logger.info("Closing simulation")
        env.close()
        
        logger.info("Basic simulation test completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in basic simulation test: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
