"""
Mock implementation of the GR00T N1 foundation model interface.

This module provides a mock implementation of the GR00T N1 interface for
development and testing purposes.
"""

import random
import uuid
import math
from typing import Dict, Any, List, Optional, Tuple

from grootzero.groot_n1.interface import GR00TN1Interface
from grootzero.logging import get_logger


class MockGR00TN1(GR00TN1Interface):
    """
    Mock implementation of the GR00T N1 foundation model interface.
    
    This class provides a configurable mock implementation of the GR00T N1 interface
    for development and testing purposes. It can be configured to return different
    predefined tasks and controller code based on the input parameters.
    """
    
    def __init__(self, 
                config: Optional[Dict[str, Any]] = None,
                predefined_tasks: Optional[List[Dict[str, Any]]] = None,
                predefined_controllers: Optional[List[str]] = None,
                task_selection_mode: str = "sequential",
                controller_selection_mode: str = "sequential",
                learning_rate: float = 0.1):
        """
        Initialize the MockGR00TN1 instance.
        
        Args:
            config: Configuration dictionary for the mock
            predefined_tasks: List of predefined task parameter dictionaries
            predefined_controllers: List of predefined controller code strings
            task_selection_mode: Mode for selecting tasks ('sequential', 'random', or 'difficulty')
            controller_selection_mode: Mode for selecting controllers ('sequential', 'random', or 'match_task')
            learning_rate: Rate at which to adjust probabilities based on rewards (0.0 to 1.0)
        """
        self.logger = get_logger("MockGR00TN1")
        self.config = config or {}
        self.task_selection_mode = task_selection_mode
        self.controller_selection_mode = controller_selection_mode
        self.learning_rate = learning_rate
        
        self.predefined_tasks = predefined_tasks or self._get_default_tasks()
        
        self.predefined_controllers = predefined_controllers or self._get_default_controllers()
        
        self.task_counter = 0
        self.controller_counter = 0
        
        self.learning_history = []
        
        # Initialize data structures for RL feedback
        self.controller_performance = {}  # Maps controller index to performance metrics
        self.controller_selection_weights = [1.0] * len(self.predefined_controllers)  # Equal weights initially
        self.task_type_controller_map = {}  # Maps task types to successful controllers
        
        self.logger.info(f"Initialized MockGR00TN1 with {len(self.predefined_tasks)} tasks and "
                        f"{len(self.predefined_controllers)} controllers")
    
    def propose_task(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a task proposal based on the current context.
        
        Args:
            current_context: Dictionary containing context information for task generation.
                This may include:
                - difficulty_level: Difficulty level for the task (e.g., 'easy', 'medium', 'hard')
                - previous_task_ids: List of IDs of previously generated tasks
                - learning_history: Information about past learning performance
                - constraints: Any constraints on the task generation
        
        Returns:
            Dictionary containing task parameters:
                - task_id: Unique identifier for the task
                - task_description: Human-readable description of the task
                - scene_config: Configuration for the simulation scene
                - robot_goal: Goal for the robot to achieve
                - domain_randomization_settings: Settings for domain randomization
                - success_criteria_description: Description of success criteria
        """
        self.logger.info(f"Proposing task with context: {current_context}")
        
        task = self._select_task(current_context)
        
        task_id = f"mock_task_{uuid.uuid4().hex[:8]}"
        task["task_id"] = task_id
        
        self._apply_context_to_task(task, current_context)
        
        self.logger.info(f"Proposed task: {task['task_id']} - {task['task_description']}")
        return task
    
    def generate_controller_code(self, task_parameters: Dict[str, Any]) -> str:
        """
        Generate controller code for a given task.
        
        Args:
            task_parameters: Dictionary containing task parameters (output from propose_task)
        
        Returns:
            String containing Python code for the controller
        """
        self.logger.info(f"Generating controller code for task: {task_parameters['task_id']}")
        
        controller_code = self._select_controller(task_parameters)
        
        controller_code = self._apply_task_to_controller(controller_code, task_parameters)
        
        self.logger.info(f"Generated controller code of length {len(controller_code)}")
        return controller_code
    
    def evaluate_controller(self, 
                           task_parameters: Dict[str, Any], 
                           controller_code: str, 
                           execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the performance of a controller on a task.
        
        Args:
            task_parameters: Dictionary containing task parameters
            controller_code: String containing the controller code
            execution_results: Dictionary containing results from executing the controller
        
        Returns:
            Dictionary containing evaluation results:
                - success: Boolean indicating whether the controller succeeded
                - score: Numerical score for the controller's performance
                - feedback: Textual feedback on the controller's performance
                - improvement_suggestions: Suggestions for improving the controller
        """
        self.logger.info(f"Evaluating controller for task: {task_parameters['task_id']}")
        
        success = execution_results.get("success", False)
        
        score = 1.0 if success else 0.0
        if "metrics" in execution_results:
            if "time_to_completion" in execution_results["metrics"]:
                time_factor = min(1.0, 10.0 / max(1.0, execution_results["metrics"]["time_to_completion"]))
                score = score * 0.7 + time_factor * 0.3
            
            if "path_efficiency" in execution_results["metrics"]:
                score = score * 0.8 + execution_results["metrics"]["path_efficiency"] * 0.2
        
        feedback = "The controller successfully completed the task." if success else "The controller failed to complete the task."
        
        improvement_suggestions = []
        if not success:
            improvement_suggestions.append("Consider implementing error recovery strategies.")
            improvement_suggestions.append("Try using a more robust control algorithm.")
        elif score < 0.8:
            improvement_suggestions.append("The controller could be optimized for better efficiency.")
            improvement_suggestions.append("Consider adding smoothing to the trajectory.")
        
        evaluation_results = {
            "success": success,
            "score": score,
            "feedback": feedback,
            "improvement_suggestions": improvement_suggestions
        }
        
        self.logger.info(f"Evaluation results: success={success}, score={score:.2f}")
        return evaluation_results
    
    def update_learning(self, 
                       task_parameters: Dict[str, Any], 
                       controller_code: str, 
                       evaluation_results: Dict[str, Any]) -> None:
        """
        Update the learning state based on task execution results.
        
        Args:
            task_parameters: Dictionary containing task parameters
            controller_code: String containing the controller code
            evaluation_results: Dictionary containing evaluation results
        """
        self.logger.info(f"Updating learning state for task: {task_parameters['task_id']}")
        
        learning_event = {
            "task_id": task_parameters["task_id"],
            "task_description": task_parameters["task_description"],
            "success": evaluation_results["success"],
            "score": evaluation_results["score"],
            "timestamp": uuid.uuid1().hex  # Use timestamp as a simple proxy for time
        }
        
        self.learning_history.append(learning_event)
        
        self.logger.info(f"Learning history updated, now contains {len(self.learning_history)} entries")
    
    def _select_task(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select a task based on the selection mode and current context.
        
        Args:
            current_context: Dictionary containing context information
        
        Returns:
            Dictionary containing task parameters
        """
        if not self.predefined_tasks:
            raise ValueError("No predefined tasks available")
        
        if self.task_selection_mode == "sequential":
            task = self.predefined_tasks[self.task_counter % len(self.predefined_tasks)]
            self.task_counter += 1
        
        elif self.task_selection_mode == "random":
            task = random.choice(self.predefined_tasks)
        
        elif self.task_selection_mode == "difficulty":
            difficulty = current_context.get("difficulty_level", "medium")
            matching_tasks = [t for t in self.predefined_tasks 
                             if t.get("difficulty", "medium") == difficulty]
            
            if not matching_tasks:
                matching_tasks = self.predefined_tasks
            
            task = random.choice(matching_tasks)
        
        else:
            raise ValueError(f"Unknown task selection mode: {self.task_selection_mode}")
        
        return dict(task)
    
    def _select_controller(self, task_parameters: Dict[str, Any]) -> str:
        """
        Select a controller based on the selection mode and task parameters.
        
        Args:
            task_parameters: Dictionary containing task parameters
        
        Returns:
            String containing controller code
        """
        if not self.predefined_controllers:
            raise ValueError("No predefined controllers available")
        
        controller_index, controller = self._get_controller_by_selection_mode(task_parameters)
        
        task_id = task_parameters.get("task_id", "unknown_task")
        if not hasattr(self, "_last_selected_controller"):
            self._last_selected_controller = {}
        self._last_selected_controller[task_id] = controller_index
        
        return controller
    
    def _get_controller_by_selection_mode(self, task_parameters: Dict[str, Any]) -> Tuple[int, str]:
        """
        Get a controller based on the selection mode and task parameters.
        
        Args:
            task_parameters: Dictionary containing task parameters
        
        Returns:
            Tuple of (controller_index, controller_code)
        """
        if self.controller_selection_mode == "sequential":
            controller_index = self.controller_counter % len(self.predefined_controllers)
            controller = self.predefined_controllers[controller_index]
            self.controller_counter += 1
        
        elif self.controller_selection_mode == "random":
            # Use weighted random selection based on controller performance
            if sum(self.controller_selection_weights) > 0:
                probabilities = [w / sum(self.controller_selection_weights) for w in self.controller_selection_weights]
                controller_index = random.choices(
                    range(len(self.predefined_controllers)), 
                    weights=probabilities, 
                    k=1
                )[0]
            else:
                controller_index = random.randint(0, len(self.predefined_controllers) - 1)
            
            controller = self.predefined_controllers[controller_index]
        
        elif self.controller_selection_mode == "match_task":
            task_type = task_parameters.get("task_type", "")
            
            if task_type in self.task_type_controller_map and random.random() < 0.7:  # 70% chance to use learned mapping
                successful_controllers = self.task_type_controller_map[task_type]
                if successful_controllers:
                    controller_index = random.choice(successful_controllers)
                    controller = self.predefined_controllers[controller_index]
                    return controller_index, controller
            
            matching_indices = []
            for i, controller_code in enumerate(self.predefined_controllers):
                if task_type.lower() in controller_code.lower():
                    matching_indices.append(i)
            
            if matching_indices:
                controller_index = random.choice(matching_indices)
            else:
                controller_index = random.randint(0, len(self.predefined_controllers) - 1)
            
            controller = self.predefined_controllers[controller_index]
        
        else:
            raise ValueError(f"Unknown controller selection mode: {self.controller_selection_mode}")
        
        return controller_index, controller
    
    def _apply_context_to_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Apply context-specific modifications to a task.
        
        Args:
            task: Dictionary containing task parameters to be modified
            context: Dictionary containing context information
        """
        if "difficulty_level" in context:
            difficulty = context["difficulty_level"]
            
            if "domain_randomization_settings" in task:
                if difficulty == "easy":
                    for key in task["domain_randomization_settings"]:
                        if isinstance(task["domain_randomization_settings"][key], list) and len(task["domain_randomization_settings"][key]) == 2:
                            min_val, max_val = task["domain_randomization_settings"][key]
                            mid_val = (min_val + max_val) / 2
                            range_factor = 0.5  # Reduce range by half for easy tasks
                            new_min = mid_val - (mid_val - min_val) * range_factor
                            new_max = mid_val + (max_val - mid_val) * range_factor
                            task["domain_randomization_settings"][key] = [new_min, new_max]
                
                elif difficulty == "hard":
                    for key in task["domain_randomization_settings"]:
                        if isinstance(task["domain_randomization_settings"][key], list) and len(task["domain_randomization_settings"][key]) == 2:
                            min_val, max_val = task["domain_randomization_settings"][key]
                            mid_val = (min_val + max_val) / 2
                            range_factor = 1.5  # Increase range by 50% for hard tasks
                            new_min = mid_val - (mid_val - min_val) * range_factor
                            new_max = mid_val + (max_val - mid_val) * range_factor
                            task["domain_randomization_settings"][key] = [new_min, new_max]
    
    def _apply_task_to_controller(self, controller_code: str, task_parameters: Dict[str, Any]) -> str:
        """
        Apply task-specific modifications to controller code.
        
        Args:
            controller_code: String containing controller code to be modified
            task_parameters: Dictionary containing task parameters
        
        Returns:
            Modified controller code string
        """
        modified_code = controller_code
        
        if "robot_goal" in task_parameters and "target_position" in task_parameters["robot_goal"]:
            target_pos = task_parameters["robot_goal"]["target_position"]
            target_pos_str = f"[{target_pos[0]}, {target_pos[1]}, {target_pos[2]}]"
            modified_code = modified_code.replace("TARGET_POSITION_PLACEHOLDER", target_pos_str)
        
        if "task_id" in task_parameters:
            modified_code = modified_code.replace("TASK_ID_PLACEHOLDER", task_parameters["task_id"])
        
        if "task_description" in task_parameters:
            modified_code = modified_code.replace("TASK_DESCRIPTION_PLACEHOLDER", task_parameters["task_description"])
        
        return modified_code
    
    def _get_default_tasks(self) -> List[Dict[str, Any]]:
        """
        Get a list of default predefined tasks.
        
        Returns:
            List of dictionaries containing task parameters
        """
        return [
            {
                "task_id": "mock_task_001",
                "task_description": "Move the cube to the green zone.",
                "task_type": "pick_and_place",
                "difficulty": "easy",
                "scene_config": {
                    "objects_to_spawn": [
                        {"name": "cube", "type": "box", "position": [0.0, 0.0, 0.0], "size": [0.05, 0.05, 0.05]},
                        {"name": "green_zone", "type": "zone", "position": [0.3, 0.3, 0.0], "size": [0.1, 0.1, 0.001], "color": [0, 1, 0, 0.5]}
                    ]
                },
                "robot_goal": {
                    "target_position": [0.3, 0.3, 0.05],
                    "target_object": "cube"
                },
                "domain_randomization_settings": {
                    "gravity": [-10.0, -9.8],
                    "friction_level": "medium",
                    "cube_mass": [0.1, 0.2]
                },
                "success_criteria_description": "Cube is within 0.05m of the center of the green zone."
            },
            {
                "task_id": "mock_task_002",
                "task_description": "Stack three blocks in a tower.",
                "task_type": "stacking",
                "difficulty": "medium",
                "scene_config": {
                    "objects_to_spawn": [
                        {"name": "block_1", "type": "box", "position": [0.1, 0.1, 0.0], "size": [0.05, 0.05, 0.05]},
                        {"name": "block_2", "type": "box", "position": [-0.1, 0.1, 0.0], "size": [0.05, 0.05, 0.05]},
                        {"name": "block_3", "type": "box", "position": [0.0, -0.1, 0.0], "size": [0.05, 0.05, 0.05]},
                        {"name": "target_zone", "type": "zone", "position": [0.0, 0.0, 0.0], "size": [0.1, 0.1, 0.001], "color": [1, 0, 0, 0.5]}
                    ]
                },
                "robot_goal": {
                    "target_position": [0.0, 0.0, 0.15],
                    "target_configuration": [
                        {"name": "block_1", "position": [0.0, 0.0, 0.0]},
                        {"name": "block_2", "position": [0.0, 0.0, 0.05]},
                        {"name": "block_3", "position": [0.0, 0.0, 0.1]}
                    ]
                },
                "domain_randomization_settings": {
                    "gravity": [-10.0, -9.5],
                    "friction_level": "high",
                    "block_mass": [0.05, 0.15]
                },
                "success_criteria_description": "All three blocks are stacked on top of each other within the target zone."
            },
            {
                "task_id": "mock_task_003",
                "task_description": "Navigate through an obstacle course to reach the goal.",
                "task_type": "navigation",
                "difficulty": "hard",
                "scene_config": {
                    "objects_to_spawn": [
                        {"name": "robot", "type": "robot", "position": [0.0, 0.0, 0.0]},
                        {"name": "obstacle_1", "type": "box", "position": [0.2, 0.2, 0.0], "size": [0.1, 0.1, 0.2]},
                        {"name": "obstacle_2", "type": "box", "position": [0.4, 0.0, 0.0], "size": [0.1, 0.3, 0.2]},
                        {"name": "obstacle_3", "type": "box", "position": [0.6, 0.3, 0.0], "size": [0.1, 0.1, 0.2]},
                        {"name": "goal_zone", "type": "zone", "position": [0.8, 0.0, 0.0], "size": [0.1, 0.1, 0.001], "color": [0, 0, 1, 0.5]}
                    ]
                },
                "robot_goal": {
                    "target_position": [0.8, 0.0, 0.0]
                },
                "domain_randomization_settings": {
                    "gravity": [-10.0, -9.0],
                    "friction_level": "random",
                    "obstacle_positions": [0.05, 0.1]  # Random offset to obstacle positions
                },
                "success_criteria_description": "Robot reaches the goal zone without colliding with obstacles."
            }
        ]
    
    def apply_reinforcement_feedback(self,
                                    task_parameters: Dict[str, Any],
                                    controller_code: str,
                                    reward: float,
                                    context: Optional[Dict[str, Any]] = None) -> None:
        """
        Apply reinforcement learning feedback to adjust internal state.
        
        This method implements a basic reinforcement learning feedback mechanism
        that adjusts the internal state of the GR00T N1 model based on rewards
        received from task execution.
        
        Args:
            task_parameters: Dictionary containing task parameters
            controller_code: String containing the controller code
            reward: Numerical reward value from task execution
            context: Optional dictionary containing additional context information
        """
        task_id = task_parameters.get("task_id", "unknown_task")
        task_type = task_parameters.get("task_type", "unknown_type")
        
        self.logger.info(f"Applying RL feedback for task: {task_id}, reward: {reward:.2f}")
        
        if not hasattr(self, "_last_selected_controller") or task_id not in self._last_selected_controller:
            self.logger.warning(f"No controller index found for task {task_id}, cannot apply feedback")
            return
        
        controller_index = self._last_selected_controller[task_id]
        
        if controller_index not in self.controller_performance:
            self.controller_performance[controller_index] = {
                "total_reward": 0.0,
                "count": 0,
                "success_count": 0,
                "task_types": {}
            }
        
        performance = self.controller_performance[controller_index]
        performance["total_reward"] += reward
        performance["count"] += 1
        
        if task_type not in performance["task_types"]:
            performance["task_types"][task_type] = {
                "total_reward": 0.0,
                "count": 0,
                "success_count": 0
            }
        
        task_type_perf = performance["task_types"][task_type]
        task_type_perf["total_reward"] += reward
        task_type_perf["count"] += 1
        
        if reward > 0:
            performance["success_count"] += 1
            task_type_perf["success_count"] += 1
            
            if task_type not in self.task_type_controller_map:
                self.task_type_controller_map[task_type] = []
            
            if controller_index not in self.task_type_controller_map[task_type]:
                self.task_type_controller_map[task_type].append(controller_index)
        
        current_weight = self.controller_selection_weights[controller_index]
        new_weight = max(0.1, current_weight + self.learning_rate * reward)  # Ensure weight doesn't go below 0.1
        self.controller_selection_weights[controller_index] = new_weight
        
        avg_reward = performance["total_reward"] / performance["count"]
        success_rate = performance["success_count"] / performance["count"]
        
        self.logger.info(f"Updated controller {controller_index} performance:")
        self.logger.info(f"  New weight: {new_weight:.2f} (was {current_weight:.2f})")
        self.logger.info(f"  Avg reward: {avg_reward:.2f}, Success rate: {success_rate:.2f}")
        self.logger.info(f"  Task type '{task_type}' success rate: "
                        f"{task_type_perf['success_count']}/{task_type_perf['count']}")
    
    def _get_default_controllers(self) -> List[str]:
        """
        Get a list of default predefined controller code strings.
        
        Returns:
            List of strings containing controller code
        """
        return [
            """
def execute_controller(robot_interface, world_state):
    \"\"\"
    Simple P-controller for pick and place tasks.
    
    Args:
        robot_interface: Interface to control the robot
        world_state: Current state of the world
    
    Returns:
        Status string: "success", "failure", or "running"
    \"\"\"
    task_id = "TASK_ID_PLACEHOLDER"
    task_description = "TASK_DESCRIPTION_PLACEHOLDER"
    
    target_pos = TARGET_POSITION_PLACEHOLDER  # Will be replaced with actual target position
    
    current_pos = robot_interface.get_end_effector_position()
    
    error = [t - c for t, c in zip(target_pos, current_pos)]
    
    distance = sum(e**2 for e in error) ** 0.5
    if distance < 0.05:
        return "success"
    
    p_gain = 0.1
    action = [p_gain * e for e in error]
    
    robot_interface.apply_action(action)
    
    return "running"
            """,
            
            """
def execute_controller(robot_interface, world_state):
    \"\"\"
    PD-controller for manipulation tasks.
    
    Args:
        robot_interface: Interface to control the robot
        world_state: Current state of the world
    
    Returns:
        Status string: "success", "failure", or "running"
    \"\"\"
    task_id = "TASK_ID_PLACEHOLDER"
    task_description = "TASK_DESCRIPTION_PLACEHOLDER"
    
    target_pos = TARGET_POSITION_PLACEHOLDER  # Will be replaced with actual target position
    
    current_pos = robot_interface.get_end_effector_position()
    current_vel = robot_interface.get_end_effector_velocity()
    
    pos_error = [t - c for t, c in zip(target_pos, current_pos)]
    
    distance = sum(e**2 for e in pos_error) ** 0.5
    if distance < 0.03:
        return "success"
    
    p_gain = 0.2
    d_gain = 0.05
    
    p_term = [p_gain * e for e in pos_error]
    d_term = [-d_gain * v for v in current_vel]  # Negative because we want to dampen velocity
    
    action = [p + d for p, d in zip(p_term, d_term)]
    
    robot_interface.apply_action(action)
    
    return "running"
            """,
            
            """
def execute_controller(robot_interface, world_state):
    \"\"\"
    State machine controller for complex tasks.
    
    Args:
        robot_interface: Interface to control the robot
        world_state: Current state of the world
    
    Returns:
        Status string: "success", "failure", or "running"
    \"\"\"
    task_id = "TASK_ID_PLACEHOLDER"
    task_description = "TASK_DESCRIPTION_PLACEHOLDER"
    
    if not hasattr(execute_controller, "state"):
        execute_controller.state = "INIT"
        execute_controller.target_object = None
        execute_controller.waypoints = []
        execute_controller.current_waypoint = 0
        execute_controller.timeout_counter = 0
    
    final_target_pos = TARGET_POSITION_PLACEHOLDER  # Will be replaced with actual target position
    
    current_pos = robot_interface.get_end_effector_position()
    
    if execute_controller.state == "INIT":
        execute_controller.target_object = world_state.get_object_by_name("cube")
        
        object_pos = execute_controller.target_object.get_position()
        approach_pos = [object_pos[0], object_pos[1], object_pos[2] + 0.1]  # Approach from above
        grasp_pos = object_pos
        lift_pos = [object_pos[0], object_pos[1], object_pos[2] + 0.1]  # Lift after grasping
        
        execute_controller.waypoints = [
            {"position": approach_pos, "action": "move"},
            {"position": grasp_pos, "action": "grasp"},
            {"position": lift_pos, "action": "move"},
            {"position": final_target_pos, "action": "move"},
            {"position": final_target_pos, "action": "release"}
        ]
        
        execute_controller.state = "EXECUTING"
        return "running"
    
    elif execute_controller.state == "EXECUTING":
        if execute_controller.current_waypoint >= len(execute_controller.waypoints):
            execute_controller.state = "DONE"
            return "success"
        
        waypoint = execute_controller.waypoints[execute_controller.current_waypoint]
        
        if waypoint["action"] == "move":
            target_pos = waypoint["position"]
            error = [t - c for t, c in zip(target_pos, current_pos)]
            distance = sum(e**2 for e in error) ** 0.5
            
            if distance < 0.02:
                execute_controller.current_waypoint += 1
                execute_controller.timeout_counter = 0
                return "running"
            
            p_gain = 0.15
            action = [p_gain * e for e in error]
            robot_interface.apply_action(action)
            
        elif waypoint["action"] == "grasp":
            robot_interface.grasp()
            execute_controller.current_waypoint += 1
            
        elif waypoint["action"] == "release":
            robot_interface.release()
            execute_controller.current_waypoint += 1
        
        execute_controller.timeout_counter += 1
        if execute_controller.timeout_counter > 1000:  # Arbitrary timeout value
            execute_controller.state = "FAILED"
            return "failure"
        
        return "running"
    
    elif execute_controller.state == "DONE":
        return "success"
    
    elif execute_controller.state == "FAILED":
        return "failure"
    
    return "running"
            """
        ]
