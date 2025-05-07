# Task 1.3: GR00T N1 Mock Interface

## Step Objective
The objective of this task was to create a well-defined mock interface for the NVIDIA GR00T N1 foundation model that can simulate its role in task proposal and controller synthesis for the GROOTZERO project. This mock interface provides a configurable stand-in for the actual GR00T N1 SDK, allowing for development and testing of other components without requiring the actual foundation model.

## Implementation Details

### 1. Interface Definition
- Created `GR00TN1Interface` abstract base class in `src/grootzero/groot_n1/interface.py` with the following methods:
  - `propose_task(current_context)`: Generate a task proposal based on the current context
  - `generate_controller_code(task_parameters)`: Generate controller code for a given task
  - `evaluate_controller(task_parameters, controller_code, execution_results)`: Evaluate the performance of a controller on a task
  - `update_learning(task_parameters, controller_code, evaluation_results)`: Update the learning state based on task execution results

### 2. Mock Implementation
- Implemented `MockGR00TN1` class in `src/grootzero/groot_n1/mock.py` that implements the `GR00TN1Interface`:
  - Configurable task and controller selection modes: "sequential", "random", "difficulty", and "match_task"
  - Predefined tasks and controllers with the ability to provide custom ones
  - Task parameter generation with unique IDs and context-specific modifications
  - Controller code generation with task-specific placeholder replacement
  - Controller evaluation based on execution results
  - Learning state tracking for future task proposals

### 3. Example Script
- Created `examples/groot_n1/basic_mock_test.py` to demonstrate the usage of the mock interface:
  - Command-line argument parsing for configuration options
  - Task proposal with different difficulty levels
  - Controller code generation for proposed tasks
  - Controller evaluation with simulated execution results
  - Learning state updates based on evaluation results

### 4. Unit Tests
- Created comprehensive unit tests in `tests/test_groot_n1.py`:
  - Tests for initialization with different configurations
  - Tests for task proposal with different selection modes
  - Tests for controller code generation with different selection modes
  - Tests for placeholder replacement in controller code
  - Tests for controller evaluation and learning state updates
  - Tests for task and controller structure validation

## Design of the Mock Interface

### Task Parameters Structure
The `propose_task` method returns a dictionary with the following structure:

```python
{
    'task_id': 'mock_task_001',                # Unique identifier for the task
    'task_description': 'Move the cube to the green zone.',  # Human-readable description
    'task_type': 'pick_and_place',             # Type of task (for controller matching)
    'difficulty': 'easy',                      # Difficulty level
    'scene_config': {                          # Configuration for the simulation scene
        'objects_to_spawn': [                  # Objects to spawn in the scene
            {
                'name': 'cube',                # Object name
                'type': 'box',                 # Object type
                'position': [0.0, 0.0, 0.0],   # Initial position
                'size': [0.05, 0.05, 0.05]     # Object size
            },
            # ... more objects
        ]
    },
    'robot_goal': {                            # Goal for the robot to achieve
        'target_position': [0.3, 0.3, 0.05],   # Target position
        'target_object': 'cube'                # Target object
    },
    'domain_randomization_settings': {         # Settings for domain randomization
        'gravity': [-10.0, -9.8],              # Range for gravity
        'friction_level': 'medium',            # Friction level
        'cube_mass': [0.1, 0.2]                # Range for cube mass
    },
    'success_criteria_description': 'Cube is within 0.05m of the center of the green zone.'
}
```

### Controller Code Structure
The `generate_controller_code` method returns a string containing Python code for the controller. The code follows this general structure:

```python
def execute_controller(robot_interface, world_state):
    """
    Controller for [task description].
    
    Args:
        robot_interface: Interface to control the robot
        world_state: Current state of the world
    
    Returns:
        Status string: "success", "failure", or "running"
    """
    # Task information
    task_id = "[task_id]"
    task_description = "[task_description]"
    
    # Target position from task parameters
    target_pos = [x, y, z]  # Target position
    
    # Get current position of the end effector
    current_pos = robot_interface.get_end_effector_position()
    
    # Calculate error
    error = [t - c for t, c in zip(target_pos, current_pos)]
    
    # Check if we've reached the target
    distance = sum(e**2 for e in error) ** 0.5
    if distance < 0.05:
        return "success"
    
    # Apply control
    action = [...]  # Calculate action based on error
    
    # Apply the action
    robot_interface.apply_action(action)
    
    # Return running status
    return "running"
```

### Evaluation Results Structure
The `evaluate_controller` method returns a dictionary with the following structure:

```python
{
    'success': True,                          # Boolean indicating whether the controller succeeded
    'score': 0.85,                            # Numerical score for the controller's performance
    'feedback': 'The controller successfully completed the task.',  # Textual feedback
    'improvement_suggestions': [              # Suggestions for improving the controller
        'The controller could be optimized for better efficiency.',
        'Consider adding smoothing to the trajectory.'
    ]
}
```

### Learning History Structure
The `update_learning` method updates an internal list of learning events with the following structure:

```python
[
    {
        'task_id': 'mock_task_001',           # Task ID
        'task_description': 'Move the cube to the green zone.',  # Task description
        'success': True,                       # Whether the controller succeeded
        'score': 0.85,                         # Score for the controller's performance
        'timestamp': '1746660761'              # Timestamp for the learning event
    },
    # ... more learning events
]
```

## How to Use/Configure the Mock Interface

### Basic Usage
Here's a simple example of how to use the `MockGR00TN1` interface:

```python
from grootzero.groot_n1.mock import MockGR00TN1

# Create a mock GR00T N1 interface with default settings
mock_groot = MockGR00TN1()

# Create context for task proposal
context = {
    "difficulty_level": "medium",
    "previous_task_ids": []
}

# Propose a task
task_params = mock_groot.propose_task(context)
print(f"Task ID: {task_params['task_id']}")
print(f"Task Description: {task_params['task_description']}")

# Generate controller code for the task
controller_code = mock_groot.generate_controller_code(task_params)
print(f"Controller Code Length: {len(controller_code)}")

# Simulate execution results
execution_results = {
    "success": True,
    "metrics": {
        "time_to_completion": 5.0,
        "path_efficiency": 0.8
    }
}

# Evaluate the controller
evaluation = mock_groot.evaluate_controller(
    task_params, controller_code, execution_results
)
print(f"Success: {evaluation['success']}")
print(f"Score: {evaluation['score']:.2f}")

# Update learning state
mock_groot.update_learning(task_params, controller_code, evaluation)
print(f"Learning History Size: {len(mock_groot.learning_history)}")
```

### Configuration Options
The `MockGR00TN1` constructor accepts several parameters for configuring its behavior:

```python
mock_groot = MockGR00TN1(
    config=None,                        # Configuration dictionary
    predefined_tasks=None,              # List of predefined task parameter dictionaries
    predefined_controllers=None,        # List of predefined controller code strings
    task_selection_mode="sequential",   # Mode for selecting tasks
    controller_selection_mode="sequential"  # Mode for selecting controllers
)
```

#### Task Selection Modes
- `"sequential"`: Select tasks in sequence, wrapping around when reaching the end
- `"random"`: Select a random task from the predefined tasks
- `"difficulty"`: Select a task based on the difficulty level in the context

```python
# Create a mock that selects tasks based on difficulty
mock_groot = MockGR00TN1(task_selection_mode="difficulty")

# Propose an easy task
easy_task = mock_groot.propose_task({"difficulty_level": "easy"})

# Propose a hard task
hard_task = mock_groot.propose_task({"difficulty_level": "hard"})
```

#### Controller Selection Modes
- `"sequential"`: Select controllers in sequence, wrapping around when reaching the end
- `"random"`: Select a random controller from the predefined controllers
- `"match_task"`: Try to match the controller to the task type

```python
# Create a mock that matches controllers to task types
mock_groot = MockGR00TN1(controller_selection_mode="match_task")

# Generate a controller for a pick_and_place task
pick_place_task = {"task_id": "task1", "task_type": "pick_and_place"}
pick_place_controller = mock_groot.generate_controller_code(pick_place_task)

# Generate a controller for a navigation task
navigation_task = {"task_id": "task2", "task_type": "navigation"}
navigation_controller = mock_groot.generate_controller_code(navigation_task)
```

#### Custom Tasks and Controllers
You can provide your own predefined tasks and controllers:

```python
# Define custom tasks
custom_tasks = [
    {
        "task_id": "custom_task_001",
        "task_description": "Custom task 1",
        "task_type": "custom",
        "difficulty": "medium",
        "scene_config": {...},
        "robot_goal": {...},
        "domain_randomization_settings": {...},
        "success_criteria_description": "..."
    },
    # ... more tasks
]

# Define custom controllers
custom_controllers = [
    """
    def execute_controller(robot_interface, world_state):
        # Custom controller code
        return "success"
    """,
    # ... more controllers
]

# Create a mock with custom tasks and controllers
mock_groot = MockGR00TN1(
    predefined_tasks=custom_tasks,
    predefined_controllers=custom_controllers
)
```

## Contribution to Overall Project
This task establishes the foundation for integrating the GR00T N1 foundation model into the GROOTZERO project. Specifically:

1. **Clear Interface Definition**: The `GR00TN1Interface` provides a well-defined contract for interacting with the GR00T N1 foundation model, ensuring that both the mock and real implementations will have consistent behavior.

2. **Mock Implementation**: The `MockGR00TN1` class provides a configurable stand-in for the actual GR00T N1 SDK, allowing for development and testing of other components without requiring the actual foundation model.

3. **Integration with Simulation**: The task parameters structure is designed to be compatible with the `SimulationEnvironment` from Task 1.2, ensuring that the two components can work together seamlessly.

4. **Learning Loop Support**: The mock implementation includes support for tracking learning history and updating the learning state, which will be essential for implementing the AZR-inspired learning loop in future tasks.

5. **Testing Infrastructure**: The comprehensive unit tests ensure that the mock interface works as expected and will help catch regressions as the codebase evolves.

## Challenges & Solutions

### Challenge 1: Designing a Flexible Interface
**Challenge**: Designing an interface that is flexible enough to accommodate both the mock implementation and the eventual real implementation of the GR00T N1 SDK was challenging. The interface needed to be comprehensive enough to support all the required functionality while remaining adaptable to future changes.

**Solution**: Implemented a clean, abstract interface using Python's ABC module that defines the core methods required for task proposal, controller generation, evaluation, and learning. The interface is designed to be implementation-agnostic, focusing on the contract rather than the implementation details. This approach ensures that both the mock and real implementations will have consistent behavior while allowing for flexibility in how they achieve that behavior.

### Challenge 2: Creating Realistic Mock Tasks and Controllers
**Challenge**: Creating mock tasks and controllers that are realistic enough to be useful for testing while remaining simple enough to be maintainable was challenging. The mock tasks needed to cover a range of difficulty levels and task types, and the mock controllers needed to be structured in a way that resembles real controller code.

**Solution**: Implemented a set of predefined tasks and controllers that cover different difficulty levels and task types. The tasks include detailed scene configurations, robot goals, and domain randomization settings, while the controllers include different control strategies (P-controller, PD-controller, state machine). The mock implementation also supports providing custom tasks and controllers, allowing for easy extension as the project evolves.

### Challenge 3: Configurable Behavior
**Challenge**: Making the mock behavior configurable in a way that is useful for testing different scenarios was challenging. The mock needed to support different ways of selecting tasks and controllers, as well as different ways of modifying them based on context.

**Solution**: Implemented multiple selection modes for both tasks and controllers, including sequential, random, difficulty-based, and task-type-based selection. The mock also supports context-specific modifications to tasks and task-specific modifications to controllers, allowing for fine-grained control over the mock behavior. This approach ensures that the mock can be configured to test a wide range of scenarios.

## Testing & Validation
The implemented functionality was tested and validated through:

1. **Unit Tests**: Created comprehensive unit tests for the `MockGR00TN1` class:
   - `test_initialization`: Verifies correct initialization with different configurations
   - `test_propose_task_sequential`: Tests sequential task selection
   - `test_propose_task_random`: Tests random task selection
   - `test_propose_task_difficulty`: Tests difficulty-based task selection
   - `test_generate_controller_code_sequential`: Tests sequential controller selection
   - `test_generate_controller_code_random`: Tests random controller selection
   - `test_generate_controller_code_match_task`: Tests task-type-based controller selection
   - `test_controller_code_placeholder_replacement`: Tests placeholder replacement in controller code
   - `test_evaluate_controller`: Tests controller evaluation
   - `test_update_learning`: Tests learning state updates
   - `test_task_structure`: Tests task structure validation
   - `test_controller_code_structure`: Tests controller code structure validation

2. **Example Script**: Created a basic example script (`examples/groot_n1/basic_mock_test.py`) that demonstrates the end-to-end usage of the mock interface:
   - Task proposal with different difficulty levels
   - Controller code generation for proposed tasks
   - Controller evaluation with simulated execution results
   - Learning state updates based on evaluation results

3. **Manual Testing**: Manually verified:
   - Command-line argument parsing works correctly
   - Task and controller selection modes work as expected
   - Placeholder replacement in controller code works correctly
   - Controller evaluation and learning state updates work as expected

## Relation to Real GR00T N1
The mock interface is designed to pave the way for eventual integration with a real GR00T N1 SDK. The following aspects of the interface are expected to remain stable:

1. **Method Signatures**: The method signatures of the `GR00TN1Interface` are designed to be implementation-agnostic and should remain stable when transitioning to a real implementation.

2. **Data Structures**: The structure of task parameters, controller code, evaluation results, and learning history is designed to be compatible with both the mock and real implementations.

3. **Integration Points**: The integration points with other components of the GROOTZERO project, such as the `SimulationEnvironment` from Task 1.2, are designed to be stable across implementations.

When transitioning to a real GR00T N1 SDK, the following changes are expected:

1. **Implementation Details**: The implementation details of the methods will change to interact with the real GR00T N1 SDK rather than using predefined tasks and controllers.

2. **Configuration Options**: The configuration options will change to reflect the capabilities of the real GR00T N1 SDK, such as model parameters, inference settings, and API credentials.

3. **Error Handling**: The error handling will need to be updated to handle errors from the real GR00T N1 SDK, such as API rate limits, authentication errors, and model-specific errors.

## Next Planned Step(s)
Based on the refined project plan, the next logical steps are:

### Task 1.4: AZR Loop Basic Implementation
- Implement the basic structure of the AZR-inspired learning loop
- Create data structures for tracking learning progress
- Develop the loop control flow for task proposal, controller generation, simulation, and evaluation
- Implement the learning update mechanism based on evaluation results

This will build on the foundation established in this task by integrating the mock GR00T N1 interface with the simulation environment from Task 1.2 to create a complete learning loop. The loop will propose tasks, generate controllers, simulate their execution, evaluate their performance, and update the learning state to improve future task proposals and controller generation.

## References to Primary Document
The implementation of the GR00T N1 mock interface aligns with the requirements in the primary reference PDF in the following ways:

1. **Task Proposal**: The `propose_task` method generates task parameters that include scene configuration, robot goals, domain randomization settings, and success criteria, as specified in the primary document.

2. **Controller Synthesis**: The `generate_controller_code` method generates Python controller functions that can be executed within the Isaac Sim environment, as specified in the primary document.

3. **Learning Loop**: The `evaluate_controller` and `update_learning` methods support the self-play learning loop described in the primary document, where the system learns from binary success/fail rewards.

4. **Domain Randomization**: The task parameters include domain randomization settings that can be used by the simulation environment to create diverse training scenarios, as specified in the primary document.

5. **Sim2Real Transfer**: The mock interface is designed to work with the simulation environment from Task 1.2, which will eventually support sim-to-real transfer through domain randomization and structured validation, as specified in the primary document.
