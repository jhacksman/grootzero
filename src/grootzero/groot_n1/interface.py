"""
Interface definition for GR00T N1 foundation model.

This module defines the abstract interface for interacting with the NVIDIA GR00T N1
foundation model for task proposal and controller synthesis.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union


class GR00TN1Interface(ABC):
    """
    Abstract interface for interacting with the GR00T N1 foundation model.
    
    This interface defines the methods that must be implemented by any class
    that provides access to the GR00T N1 foundation model, whether it's a
    real implementation or a mock.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def generate_controller_code(self, task_parameters: Dict[str, Any]) -> str:
        """
        Generate controller code for a given task.
        
        Args:
            task_parameters: Dictionary containing task parameters (output from propose_task)
        
        Returns:
            String containing Python code for the controller
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
