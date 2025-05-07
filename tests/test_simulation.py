"""
Tests for the simulation environment module.
"""

import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from grootzero.simulation.environment import SimulationEnvironment
from grootzero.simulation.utils import (
    initialize_simulation,
    load_environment,
    create_robot,
    apply_domain_randomization,
    get_observation,
    apply_action
)


class TestSimulationEnvironment:
    """Tests for the SimulationEnvironment class."""
    
    def test_init(self):
        """Test initialization of SimulationEnvironment."""
        env = SimulationEnvironment(mock_mode=True)
        assert env is not None
        assert env.mock_mode is True
        assert env.is_initialized is False
        assert env.current_step == 0
    
    def test_initialize(self):
        """Test initialization of the simulation."""
        env = SimulationEnvironment(mock_mode=True)
        result = env.initialize()
        assert result is True
        assert env.is_initialized is True
        assert env.simulation_app is not None
        assert env.scene is not None
    
    def test_load_environment(self):
        """Test loading an environment."""
        env = SimulationEnvironment(mock_mode=True)
        env.initialize()
        result = env.load_environment("test_environment")
        assert result is True
        assert env.scene.environment_path == "test_environment"
    
    def test_create_robot(self):
        """Test creating a robot."""
        env = SimulationEnvironment(mock_mode=True)
        env.initialize()
        robot_id = env.create_robot("test_robot", "ur10", [0.0, 0.0, 0.0])
        assert robot_id != ""
        assert robot_id in env.robots
        assert env.robots[robot_id]["name"] == "test_robot"
        assert env.robots[robot_id]["type"] == "ur10"
    
    def test_apply_domain_randomization(self):
        """Test applying domain randomization."""
        env = SimulationEnvironment(mock_mode=True)
        env.initialize()
        env.domain_rand_enabled = True
        result = env.apply_domain_randomization()
        assert result is True
    
    def test_step(self):
        """Test stepping the simulation."""
        env = SimulationEnvironment(mock_mode=True)
        env.initialize()
        robot_id = env.create_robot("test_robot", "ur10", [0.0, 0.0, 0.0])
        actions = {robot_id: {"joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]}}
        observations, rewards, dones, info = env.step(actions)
        assert robot_id in observations
        assert robot_id in rewards
        assert robot_id in dones
        assert "step" in info
        assert env.current_step == 1
    
    def test_reset(self):
        """Test resetting the simulation."""
        env = SimulationEnvironment(mock_mode=True)
        env.initialize()
        robot_id = env.create_robot("test_robot", "ur10", [0.0, 0.0, 0.0])
        env.step({})  # Step once to increment current_step
        observations = env.reset()
        assert robot_id in observations
        assert env.current_step == 0
    
    def test_close(self):
        """Test closing the simulation."""
        env = SimulationEnvironment(mock_mode=True)
        env.initialize()
        env.close()
        assert env.is_initialized is False
        assert env.simulation_app is None
        assert env.scene is None


class TestSimulationUtils:
    """Tests for the simulation utility functions."""
    
    def test_initialize_simulation(self):
        """Test initializing the simulation."""
        sim_app = initialize_simulation(mock_mode=True)
        assert sim_app is not None
    
    def test_load_environment(self):
        """Test loading an environment."""
        sim_app = initialize_simulation(mock_mode=True)
        scene = load_environment(sim_app, "test_environment", mock_mode=True)
        assert scene is not None
        assert scene.environment_path == "test_environment"
    
    def test_create_robot(self):
        """Test creating a robot."""
        sim_app = initialize_simulation(mock_mode=True)
        scene = load_environment(sim_app, "test_environment", mock_mode=True)
        robot_id = create_robot(scene, "test_robot", "ur10", [0.0, 0.0, 0.0], mock_mode=True)
        assert robot_id != ""
        assert "ur10" in robot_id
        assert "test_robot" in robot_id
    
    def test_apply_domain_randomization(self):
        """Test applying domain randomization."""
        sim_app = initialize_simulation(mock_mode=True)
        scene = load_environment(sim_app, "test_environment", mock_mode=True)
        config = {
            "enabled": True,
            "gravity_range": [-10.0, -9.8],
            "friction_range": [0.5, 1.0],
            "mass_range_factor": [0.8, 1.2]
        }
        result = apply_domain_randomization(scene, config, mock_mode=True)
        assert result is True
    
    def test_get_observation(self):
        """Test getting an observation."""
        sim_app = initialize_simulation(mock_mode=True)
        scene = load_environment(sim_app, "test_environment", mock_mode=True)
        robot_id = create_robot(scene, "test_robot", "ur10", [0.0, 0.0, 0.0], mock_mode=True)
        observation = get_observation(scene, robot_id, mock_mode=True)
        assert "position" in observation
        assert "velocity" in observation
        assert "joint_positions" in observation
        assert "joint_velocities" in observation
        assert "camera" in observation
    
    def test_apply_action(self):
        """Test applying an action."""
        sim_app = initialize_simulation(mock_mode=True)
        scene = load_environment(sim_app, "test_environment", mock_mode=True)
        robot_id = create_robot(scene, "test_robot", "ur10", [0.0, 0.0, 0.0], mock_mode=True)
        action = {"joint_positions": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]}
        result = apply_action(scene, robot_id, action, mock_mode=True)
        assert result is True
