"""
Orchestrator for the AZR learning loop.

This module provides the main orchestration logic for the AZR-inspired
self-play learning loop, connecting the GR00T N1 foundation model with
the Isaac Sim simulation environment.
"""

import os
import time
import importlib
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Callable

from grootzero.config import load_config
from grootzero.logging import get_logger
from grootzero.simulation.environment import SimulationEnvironment
from grootzero.groot_n1.interface import GR00TN1Interface
from grootzero.azr.rewards import calculate_reward, calculate_normalized_reward


class AZRLearningLoop:
    """
    Orchestrator for the AZR learning loop.
    
    This class manages the overall process of the AZR learning loop,
    connecting the GR00T N1 foundation model with the Isaac Sim
    simulation environment.
    
    Attributes:
        config: Configuration dictionary for the learning loop
        logger: Logger instance for the learning loop
        gr00t_n1: GR00T N1 interface instance
        sim_env: Simulation environment instance
        learning_history: List of learning events
        episode_count: Number of episodes run so far
        max_episodes: Maximum number of episodes to run
        current_context: Current context for task proposal
    """
    
    def __init__(
        self,
        gr00t_n1: GR00TN1Interface,
        sim_env: Optional[SimulationEnvironment] = None,
        config_path: Optional[str] = None,
        mock_simulation: bool = False,
        headless: bool = False
    ):
        """
        Initialize the AZR learning loop.
        
        Args:
            gr00t_n1: GR00T N1 interface instance
            sim_env: Optional simulation environment instance. If not provided,
                a new instance will be created based on the configuration.
            config_path: Path to the configuration file. If not provided,
                the default configuration will be used.
            mock_simulation: Whether to use mock mode for the simulation environment.
                Only used if sim_env is not provided.
            headless: Whether to run the simulation in headless mode.
                Only used if sim_env is not provided.
        """
        self.config = load_config(config_path)
        self.logger = get_logger("azr_learning_loop")
        
        self.gr00t_n1 = gr00t_n1
        
        if sim_env is None:
            self.logger.info("Creating simulation environment")
            self.sim_env = SimulationEnvironment(
                config_path=config_path,
                mock_mode=mock_simulation
            )
        else:
            self.sim_env = sim_env
        
        self.learning_history = []
        self.episode_count = 0
        self.max_episodes = self.config.get("azr", {}).get("max_episodes", 100)
        
        self.current_context = {
            "difficulty_level": self.config.get("azr", {}).get("initial_difficulty", "easy"),
            "previous_task_ids": [],
            "learning_history": []
        }
        
        self.logger.info("AZR learning loop initialized")
        self.logger.info(f"Max episodes: {self.max_episodes}")
        self.logger.info(f"Initial difficulty: {self.current_context['difficulty_level']}")
    
    def initialize(self) -> bool:
        """
        Initialize the learning loop.
        
        This method initializes the simulation environment and
        prepares the learning loop for execution.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        self.logger.info("Initializing AZR learning loop")
        
        if not self.sim_env.initialize():
            self.logger.error("Failed to initialize simulation environment")
            return False
        
        self.logger.info("AZR learning loop initialized successfully")
        return True
    
    def run_episode(self) -> Dict[str, Any]:
        """
        Run a single episode of the learning loop.
        
        This method runs a single episode of the learning loop, including:
        1. Task proposal
        2. Controller generation
        3. Simulation execution
        4. Result collection
        5. Result processing
        6. Reinforcement learning feedback
        
        Returns:
            Dictionary containing the episode results:
                - task_parameters: Task parameters for the episode
                - controller_code: Controller code for the episode
                - execution_results: Results from executing the controller
                - evaluation_results: Results from evaluating the controller
                - reward: Calculated reward value for reinforcement learning
        """
        self.logger.info(f"Running episode {self.episode_count + 1}/{self.max_episodes}")
        
        self.logger.info("Proposing task")
        task_parameters = self.gr00t_n1.propose_task(self.current_context)
        self.logger.info(f"Task proposed: {task_parameters['task_id']}")
        self.logger.info(f"Task description: {task_parameters['task_description']}")
        
        self.logger.info("Generating controller code")
        controller_code = self.gr00t_n1.generate_controller_code(task_parameters)
        self.logger.debug(f"Controller code length: {len(controller_code)}")
        
        self.logger.info("Executing controller in simulation")
        execution_results = self._execute_controller_in_simulation(task_parameters, controller_code)
        self.logger.info(f"Execution results: success={execution_results.get('success', False)}")
        
        self.logger.info("Evaluating controller")
        evaluation_results = self.gr00t_n1.evaluate_controller(
            task_parameters, controller_code, execution_results
        )
        self.logger.info(f"Evaluation results: score={evaluation_results.get('score', 0.0)}")
        
        # Calculate reward for reinforcement learning feedback
        self.logger.info("Calculating reward for reinforcement learning")
        reward = calculate_reward(execution_results, task_parameters)
        self.logger.info(f"Calculated reward: {reward:.2f}")
        
        self.logger.info("Applying reinforcement learning feedback")
        self.gr00t_n1.apply_reinforcement_feedback(
            task_parameters, 
            controller_code, 
            reward,
            context=self.current_context
        )
        
        self.logger.info("Updating learning state")
        self.gr00t_n1.update_learning(task_parameters, controller_code, evaluation_results)
        
        self._update_learning_history(task_parameters, evaluation_results, reward)
        self.episode_count += 1
        
        return {
            "task_parameters": task_parameters,
            "controller_code": controller_code,
            "execution_results": execution_results,
            "evaluation_results": evaluation_results,
            "reward": reward
        }
    
    def run(self, num_episodes: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Run the learning loop for a specified number of episodes.
        
        Args:
            num_episodes: Number of episodes to run. If not provided,
                the maximum number of episodes from the configuration will be used.
        
        Returns:
            List of episode results.
        """
        if num_episodes is None:
            num_episodes = self.max_episodes
        
        self.logger.info(f"Running AZR learning loop for {num_episodes} episodes")
        
        if not self.initialize():
            self.logger.error("Failed to initialize AZR learning loop")
            return []
        
        episode_results = []
        
        for _ in range(num_episodes):
            if self.episode_count >= self.max_episodes:
                self.logger.info("Reached maximum number of episodes")
                break
            
            try:
                episode_result = self.run_episode()
                episode_results.append(episode_result)
            except Exception as e:
                self.logger.error(f"Error running episode: {e}")
                break
        
        self.logger.info(f"AZR learning loop completed {len(episode_results)} episodes")
        
        return episode_results
    
    def close(self) -> None:
        """
        Close the learning loop.
        
        This method closes the simulation environment and
        releases any resources used by the learning loop.
        """
        self.logger.info("Closing AZR learning loop")
        
        if self.sim_env is not None:
            self.sim_env.close()
        
        self.logger.info("AZR learning loop closed")
    
    def _execute_controller_in_simulation(
        self,
        task_parameters: Dict[str, Any],
        controller_code: str
    ) -> Dict[str, Any]:
        """
        Execute a controller in the simulation environment.
        
        This method loads the task parameters into the simulation environment,
        compiles and executes the controller code, and returns the execution results.
        
        Args:
            task_parameters: Task parameters for the episode
            controller_code: Controller code for the episode
        
        Returns:
            Dictionary containing the execution results:
                - success: Whether the controller succeeded
                - metrics: Dictionary of metrics collected during execution
        """
        self.logger.info("Loading environment for task")
        if not self.sim_env.load_environment():
            self.logger.error("Failed to load environment")
            return {"success": False, "metrics": {}}
        
        robot_id = self._create_robot_from_task(task_parameters)
        if not robot_id:
            self.logger.error("Failed to create robot")
            return {"success": False, "metrics": {}}
        
        if not self._apply_domain_randomization(task_parameters):
            self.logger.error("Failed to apply domain randomization")
            return {"success": False, "metrics": {}}
        
        observations = self.sim_env.reset()
        
        controller_func = self._compile_controller_code(controller_code)
        if controller_func is None:
            self.logger.error("Failed to compile controller code")
            return {"success": False, "metrics": {}}
        
        return self._run_controller(controller_func, robot_id, task_parameters)
    
    def _create_robot_from_task(self, task_parameters: Dict[str, Any]) -> str:
        """
        Create a robot in the simulation environment based on task parameters.
        
        Args:
            task_parameters: Task parameters for the episode
        
        Returns:
            Robot ID if successful, empty string otherwise.
        """
        robot_config = task_parameters.get("robot_config", {})
        robot_name = robot_config.get("name", "default_robot")
        robot_type = robot_config.get("type", "ur10")
        position = robot_config.get("position", [0.0, 0.0, 0.0])
        
        self.logger.info(f"Creating robot: {robot_name} ({robot_type})")
        
        return self.sim_env.create_robot(
            robot_name=robot_name,
            robot_type=robot_type,
            position=position
        )
    
    def _apply_domain_randomization(self, task_parameters: Dict[str, Any]) -> bool:
        """
        Apply domain randomization to the simulation environment based on task parameters.
        
        Args:
            task_parameters: Task parameters for the episode
        
        Returns:
            True if successful, False otherwise.
        """
        domain_randomization = task_parameters.get("domain_randomization_settings", {})
        
        self.logger.info("Applying domain randomization")
        self.logger.debug(f"Domain randomization settings: {domain_randomization}")
        
        return self.sim_env.apply_domain_randomization(domain_randomization)
    
    def _compile_controller_code(self, controller_code: str) -> Optional[Callable]:
        """
        Compile controller code into a callable function.
        
        Args:
            controller_code: Controller code string
        
        Returns:
            Callable controller function if successful, None otherwise.
        """
        self.logger.info("Compiling controller code")
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
                temp_file.write(controller_code.encode())
                temp_file_path = temp_file.name
            
            module_name = os.path.basename(temp_file_path)[:-3]  # Remove .py extension
            spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            os.unlink(temp_file_path)
            
            if hasattr(module, "execute_controller"):
                return module.execute_controller
            else:
                self.logger.error("Controller code does not define execute_controller function")
                return None
        
        except Exception as e:
            self.logger.error(f"Error compiling controller code: {e}")
            return None
    
    def _run_controller(
        self,
        controller_func: Callable,
        robot_id: str,
        task_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a controller in the simulation environment.
        
        Args:
            controller_func: Callable controller function
            robot_id: ID of the robot to control
            task_parameters: Task parameters for the episode
        
        Returns:
            Dictionary containing the execution results:
                - success: Whether the controller succeeded
                - metrics: Dictionary of metrics collected during execution
        """
        self.logger.info("Running controller")
        
        max_steps = self.config.get("azr", {}).get("max_steps_per_episode", 1000)
        step_count = 0
        success = False
        metrics = {
            "time_to_completion": 0.0,
            "path_efficiency": 0.0,
            "energy_efficiency": 0.0
        }
        
        start_time = time.time()
        
        robot_interface = RobotInterface(self.sim_env, robot_id)
        
        while step_count < max_steps:
            observations = self.sim_env.get_observations()
            
            world_state = {
                "observations": observations,
                "task_parameters": task_parameters,
                "step_count": step_count
            }
            
            try:
                status = controller_func(robot_interface, world_state)
            except Exception as e:
                self.logger.error(f"Error in controller function: {e}")
                break
            
            if status == "success":
                success = True
                self.logger.info(f"Controller succeeded at step {step_count}")
                break
            elif status == "failure":
                success = False
                self.logger.info(f"Controller failed at step {step_count}")
                break
            
            actions = {robot_id: robot_interface.get_actions()}
            _, rewards, dones, info = self.sim_env.step(actions)
            
            if dones.get(robot_id, False):
                success = rewards.get(robot_id, 0.0) > 0.0
                self.logger.info(f"Episode done at step {step_count}, success={success}")
                break
            
            step_count += 1
        
        end_time = time.time()
        metrics["time_to_completion"] = end_time - start_time
        metrics["steps_to_completion"] = step_count
        
        if hasattr(robot_interface, "get_path_efficiency"):
            metrics["path_efficiency"] = robot_interface.get_path_efficiency()
        
        if hasattr(robot_interface, "get_energy_efficiency"):
            metrics["energy_efficiency"] = robot_interface.get_energy_efficiency()
        
        self.logger.info(f"Controller execution completed: success={success}, steps={step_count}")
        self.logger.debug(f"Metrics: {metrics}")
        
        return {
            "success": success,
            "metrics": metrics
        }
    
    def _update_learning_history(
        self,
        task_parameters: Dict[str, Any],
        evaluation_results: Dict[str, Any],
        reward: Optional[float] = None
    ) -> None:
        """
        Update the learning history with the results of an episode.
        
        Args:
            task_parameters: Task parameters for the episode
            evaluation_results: Results from evaluating the controller
            reward: Optional reward value from reinforcement learning
        """
        learning_event = {
            "task_id": task_parameters["task_id"],
            "task_description": task_parameters["task_description"],
            "success": evaluation_results.get("success", False),
            "score": evaluation_results.get("score", 0.0),
            "timestamp": str(int(time.time()))
        }
        
        if reward is not None:
            learning_event["reward"] = reward
        
        self.learning_history.append(learning_event)
        
        self.current_context["previous_task_ids"].append(task_parameters["task_id"])
        self.current_context["learning_history"] = self.learning_history
        
        self._adjust_difficulty_based_on_performance()
    
    def _adjust_difficulty_based_on_performance(self) -> None:
        """
        Adjust the difficulty level based on recent performance.
        
        This method adjusts the difficulty level in the current context
        based on the success rate of recent episodes.
        """
        if len(self.learning_history) < 5:
            return
        
        recent_history = self.learning_history[-5:]
        success_count = sum(1 for event in recent_history if event["success"])
        success_rate = success_count / len(recent_history)
        
        current_difficulty = self.current_context["difficulty_level"]
        
        if success_rate > 0.8 and current_difficulty == "easy":
            self.current_context["difficulty_level"] = "medium"
            self.logger.info("Increasing difficulty to medium")
        elif success_rate > 0.8 and current_difficulty == "medium":
            self.current_context["difficulty_level"] = "hard"
            self.logger.info("Increasing difficulty to hard")
        elif success_rate < 0.2 and current_difficulty == "hard":
            self.current_context["difficulty_level"] = "medium"
            self.logger.info("Decreasing difficulty to medium")
        elif success_rate < 0.2 and current_difficulty == "medium":
            self.current_context["difficulty_level"] = "easy"
            self.logger.info("Decreasing difficulty to easy")


class RobotInterface:
    """
    Interface for controlling a robot in the simulation environment.
    
    This class provides a simplified interface for controllers to
    interact with a robot in the simulation environment.
    
    Attributes:
        sim_env: Simulation environment instance
        robot_id: ID of the robot to control
        actions: Current actions to apply to the robot
        trajectory: List of positions visited by the robot
    """
    
    def __init__(self, sim_env: SimulationEnvironment, robot_id: str):
        """
        Initialize the robot interface.
        
        Args:
            sim_env: Simulation environment instance
            robot_id: ID of the robot to control
        """
        self.sim_env = sim_env
        self.robot_id = robot_id
        self.actions = {}
        self.trajectory = []
        
        initial_pos = self.get_end_effector_position()
        if initial_pos:
            self.trajectory.append(initial_pos)
    
    def get_end_effector_position(self) -> List[float]:
        """
        Get the current position of the robot's end effector.
        
        Returns:
            List of 3 floats representing the x, y, z position.
        """
        observations = self.sim_env.get_observations()
        if self.robot_id in observations:
            return observations[self.robot_id].get("end_effector_position", [0.0, 0.0, 0.0])
        return [0.0, 0.0, 0.0]
    
    def get_joint_positions(self) -> List[float]:
        """
        Get the current positions of the robot's joints.
        
        Returns:
            List of floats representing the joint positions.
        """
        observations = self.sim_env.get_observations()
        if self.robot_id in observations:
            return observations[self.robot_id].get("joint_positions", [])
        return []
    
    def apply_action(self, action: Dict[str, Any]) -> None:
        """
        Apply an action to the robot.
        
        Args:
            action: Dictionary containing the action to apply.
                This can include:
                - joint_positions: List of joint positions
                - joint_velocities: List of joint velocities
                - end_effector_position: Target end effector position
                - gripper_position: Target gripper position
        """
        self.actions = action
        
        current_pos = self.get_end_effector_position()
        if current_pos:
            self.trajectory.append(current_pos)
    
    def get_actions(self) -> Dict[str, Any]:
        """
        Get the current actions to apply to the robot.
        
        Returns:
            Dictionary containing the actions to apply.
        """
        return self.actions
    
    def get_path_efficiency(self) -> float:
        """
        Calculate the path efficiency of the robot's trajectory.
        
        Path efficiency is defined as the ratio of the direct distance
        between the start and end points to the total distance traveled.
        
        Returns:
            Path efficiency as a float between 0.0 and 1.0.
        """
        if len(self.trajectory) < 2:
            return 1.0
        
        start_point = self.trajectory[0]
        end_point = self.trajectory[-1]
        direct_distance = sum((e - s) ** 2 for s, e in zip(start_point, end_point)) ** 0.5
        
        total_distance = 0.0
        for i in range(1, len(self.trajectory)):
            prev_point = self.trajectory[i - 1]
            curr_point = self.trajectory[i]
            segment_distance = sum((c - p) ** 2 for p, c in zip(prev_point, curr_point)) ** 0.5
            total_distance += segment_distance
        
        if total_distance > 0.0:
            return direct_distance / total_distance
        return 1.0
    
    def get_energy_efficiency(self) -> float:
        """
        Calculate the energy efficiency of the robot's actions.
        
        Energy efficiency is a simplified metric based on the
        magnitude of joint velocities and accelerations.
        
        Returns:
            Energy efficiency as a float between 0.0 and 1.0.
        """
        return 0.8  # Placeholder value
