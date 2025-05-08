# Task 1.4: AZR Loop Basic Implementation

## Objective

The objective of this task was to implement the basic structure and orchestration logic for the Absolute Zero Reasoner (AZR) learning loop. This loop connects the previously implemented SimulationEnvironment (Task 1.2) and MockGR00TN1 interface (Task 1.3) into a functioning, albeit simplified, learning system. The goal was to create a foundation for the self-play learning paradigm where the system can autonomously generate tasks, synthesize controllers, execute them in simulation, and learn from the results.

## AZR Loop Architecture

The AZR learning loop is implemented as a modular orchestration system that coordinates the interaction between the GR00T N1 foundation model (or its mock) and the Isaac Sim simulation environment. The architecture follows a clear sequence of operations and maintains a clean separation of concerns between components.

### Core Components

1. **AZRLearningLoop**: The main orchestrator class that manages the overall process
2. **GR00TN1Interface**: Abstract interface for task proposal and controller generation
3. **SimulationEnvironment**: Interface for simulation execution and observation collection
4. **RobotInterface**: Helper class that provides a simplified interface for controllers to interact with robots

### Sequence of Operations

The AZR learning loop follows this sequence of operations for each episode:

1. **Task Proposal**: The orchestrator requests a task proposal from the GR00T N1 interface based on the current context (difficulty level, learning history, etc.)
2. **Controller Generation**: The orchestrator requests controller code from the GR00T N1 interface based on the proposed task parameters
3. **Simulation Execution**:
   - The orchestrator initializes the simulation environment
   - It loads the task configuration into the simulation
   - It creates robots according to the task parameters
   - It applies domain randomization based on the task parameters
   - It compiles and executes the controller code in the simulation
4. **Result Collection**: The orchestrator collects execution results from the simulation, including success/failure status and performance metrics
5. **Result Processing**:
   - The orchestrator requests an evaluation of the controller from the GR00T N1 interface
   - It updates the learning state in the GR00T N1 interface
   - It updates its internal learning history
   - It adjusts the difficulty level based on recent performance

### Component Interaction Diagram

```
┌─────────────────┐      ┌───────────────────┐
│                 │      │                   │
│  AZRLearningLoop│◄─────┤  GR00TN1Interface │
│  (Orchestrator) │      │  (Task/Controller)│
│                 │      │                   │
└────────┬────────┘      └───────────────────┘
         │
         │ Executes controllers
         │ in simulation
         ▼
┌─────────────────┐
│                 │
│ SimulationEnv   │
│ (Isaac Sim)     │
│                 │
└─────────────────┘
```

## Data Flow

The AZR learning loop manages the flow of data between components in a structured manner:

### 1. Task Proposal Flow

- **Input**: Current context dictionary containing:
  - `difficulty_level`: Current difficulty setting (easy, medium, hard)
  - `previous_task_ids`: List of previously generated task IDs
  - `learning_history`: List of previous learning events with outcomes
- **Output**: Task parameters dictionary containing:
  - `task_id`: Unique identifier for the task
  - `task_description`: Human-readable description
  - `scene_config`: Configuration for the simulation scene
  - `robot_config`: Configuration for the robot(s)
  - `robot_goal`: Goal for the robot to achieve
  - `domain_randomization_settings`: Settings for domain randomization
  - `success_criteria_description`: Description of success criteria

### 2. Controller Generation Flow

- **Input**: Task parameters from the task proposal
- **Output**: String containing Python code for the controller

### 3. Simulation Execution Flow

- **Input**:
  - Task parameters for environment configuration
  - Controller code for execution
- **Process**:
  - The controller code is compiled into a callable function
  - The environment is configured according to task parameters
  - The controller function is executed with access to a RobotInterface
  - The controller function returns status ("success", "failure", or "continue")
- **Output**: Execution results dictionary containing:
  - `success`: Boolean indicating whether the controller succeeded
  - `metrics`: Dictionary of performance metrics (time, steps, efficiency)

### 4. Result Processing Flow

- **Input**:
  - Task parameters
  - Controller code
  - Execution results
- **Process**:
  - The GR00T N1 interface evaluates the controller performance
  - The learning state is updated in the GR00T N1 interface
  - The learning history is updated in the orchestrator
  - The difficulty level is adjusted based on recent performance
- **Output**: Updated learning context for the next episode

## Implementation Details

### AZRLearningLoop Class

The `AZRLearningLoop` class is the central component of the implementation. Key aspects include:

1. **Initialization and Configuration**:
   - Takes instances of `GR00TN1Interface` and `SimulationEnvironment`
   - Loads configuration from a config file or uses defaults
   - Initializes learning history and context

2. **Episode Management**:
   - `run_episode()`: Runs a single episode of the learning loop
   - `run(num_episodes)`: Runs multiple episodes
   - Tracks episode count and enforces maximum episode limit

3. **Controller Execution**:
   - `_execute_controller_in_simulation()`: Manages the execution of a controller in the simulation
   - `_compile_controller_code()`: Compiles controller code string into a callable function
   - `_run_controller()`: Runs the compiled controller function in the simulation

4. **Learning Management**:
   - `_update_learning_history()`: Updates the learning history with episode results
   - `_adjust_difficulty_based_on_performance()`: Adjusts difficulty based on recent success rate

### RobotInterface Class

The `RobotInterface` class provides a simplified interface for controllers to interact with robots in the simulation:

1. **Robot State Access**:
   - `get_end_effector_position()`: Gets the current position of the robot's end effector
   - `get_joint_positions()`: Gets the current positions of the robot's joints

2. **Action Application**:
   - `apply_action()`: Applies an action to the robot
   - `get_actions()`: Gets the current actions to apply to the robot

3. **Performance Metrics**:
   - `get_path_efficiency()`: Calculates the path efficiency of the robot's trajectory
   - `get_energy_efficiency()`: Calculates the energy efficiency of the robot's actions

### Dynamic Code Compilation

A key implementation detail is the dynamic compilation and execution of controller code:

1. The controller code string is written to a temporary Python file
2. The file is imported as a module using Python's importlib
3. The `execute_controller` function is extracted from the module
4. The function is called with a RobotInterface instance and world state

This approach allows for flexible controller implementation while maintaining security through isolation.

## How to Run

The AZR learning loop can be run using the provided example script:

```bash
python examples/azr/basic_learning_loop_test.py --mock-simulation --num-episodes 3
```

Command-line options:

- `--log-level`: Logging level (default: INFO)
- `--config-path`: Path to configuration file (default: None, uses default config)
- `--mock-simulation`: Use mock simulation environment (default: False)
- `--headless`: Run in headless mode (default: False)
- `--num-episodes`: Number of episodes to run (default: 3)
- `--task-selection`: Task selection mode for MockGR00TN1 (default: sequential)
- `--controller-selection`: Controller selection mode for MockGR00TN1 (default: sequential)
- `--difficulty`: Initial difficulty level (default: medium)

Example output:

```
INFO:basic_learning_loop_test:Starting basic AZR learning loop test
INFO:basic_learning_loop_test:Mock simulation: True
INFO:basic_learning_loop_test:Number of episodes: 3
INFO:basic_learning_loop_test:Creating MockGR00TN1 instance
INFO:basic_learning_loop_test:Creating SimulationEnvironment instance
INFO:basic_learning_loop_test:Creating AZRLearningLoop instance
INFO:basic_learning_loop_test:Running learning loop for 3 episodes
INFO:azr_learning_loop:Running AZR learning loop for 3 episodes
INFO:azr_learning_loop:Initializing AZR learning loop
INFO:azr_learning_loop:Running episode 1/5
INFO:azr_learning_loop:Proposing task
INFO:azr_learning_loop:Task proposed: mock_task_1
INFO:azr_learning_loop:Task description: Simple pick and place task
...
```

## Limitations of Basic Loop

The current implementation of the AZR learning loop has several limitations and simplified aspects:

1. **Learning Mechanism**: The learning mechanism is currently very basic, with a simple difficulty adjustment based on recent success rate. A more sophisticated learning algorithm would be needed for a full AZR system.

2. **Controller Compilation**: The controller compilation mechanism is functional but lacks robust error handling and security features that would be needed in a production system.

3. **Mock Components**: Both the GR00T N1 interface and simulation environment are currently using mock implementations. Integration with the real components will require additional work.

4. **Limited Metrics**: The current implementation tracks only basic metrics like success/failure, time to completion, and path efficiency. A full system would need more comprehensive metrics.

5. **Simplified Task Structure**: The task structure is currently simplified, with basic parameters for scene configuration, robot configuration, and goals. A more sophisticated task representation would be needed for complex robotics tasks.

6. **No Persistence**: The current implementation does not persist learning history or trained models between runs. A full system would need to save and load this information.

7. **Limited Validation**: The current implementation has limited validation of task parameters and controller code. A full system would need more robust validation to ensure safety and correctness.

## Testing

The AZR learning loop implementation was tested through a combination of unit tests and integration testing:

### Unit Tests

Unit tests were implemented in `tests/azr/test_orchestrator.py` using Python's unittest framework. The tests cover:

1. **AZRLearningLoop Initialization**: Tests that the learning loop initializes correctly with the provided GR00T N1 interface and simulation environment.

2. **Learning Loop Initialization**: Tests that the learning loop initializes the simulation environment correctly.

3. **Episode Execution**: Tests that a single episode runs correctly, including task proposal, controller generation, simulation execution, and result processing.

4. **Multiple Episodes**: Tests that multiple episodes run correctly and that the learning loop tracks episode count and enforces maximum episode limit.

5. **RobotInterface**: Tests that the RobotInterface correctly interacts with the simulation environment and provides the expected functionality to controllers.

### Integration Testing

Integration testing was performed using the example script `examples/azr/basic_learning_loop_test.py`. This script demonstrates the end-to-end functionality of the AZR learning loop, including:

1. **Component Integration**: Tests that the AZRLearningLoop correctly integrates with the MockGR00TN1 and SimulationEnvironment components.

2. **Data Flow**: Tests that data flows correctly between components, with task parameters, controller code, and execution results being passed as expected.

3. **Configuration Options**: Tests that the learning loop correctly handles different configuration options, such as number of episodes, difficulty level, and task/controller selection modes.

4. **Error Handling**: Tests that the learning loop correctly handles errors, such as failed controller compilation or simulation errors.

The integration testing confirmed that the AZR learning loop functions as expected and provides a solid foundation for future development.

## Next Steps

Based on the refined project plan, the next logical steps are:

### Task 1.5: AZR Loop Learning Enhancement

This task will focus on enhancing the learning mechanism of the AZR loop. Key aspects will include:

1. **Improved Learning Algorithm**: Implement a more sophisticated learning algorithm based on the AZR principles, such as a variant of REINFORCE or other policy gradient methods.

2. **Better Feedback Mechanisms**: Enhance the feedback mechanisms between the simulation environment and the GR00T N1 interface to provide more detailed information for learning.

3. **Task Difficulty Progression**: Implement a more sophisticated task difficulty progression system that considers multiple factors beyond simple success rate.

4. **Learning Persistence**: Add mechanisms to persist learning history and trained models between runs.

This enhancement will build on the solid foundation established in this task and move the system closer to the full AZR self-play paradigm described in the project vision.

## Conclusion

The implementation of the basic AZR learning loop provides a solid foundation for the GROOTZERO project. It successfully integrates the previously implemented components (SimulationEnvironment and MockGR00TN1) into a functioning learning system that can autonomously generate tasks, synthesize controllers, execute them in simulation, and learn from the results.

While the current implementation has several limitations and simplified aspects, it provides a clear structure and architecture that can be extended and enhanced in future tasks. The modular design and clean separation of concerns will facilitate the integration of more sophisticated learning algorithms and the transition from mock components to real ones.

The next steps will focus on enhancing the learning mechanism and moving the system closer to the full AZR self-play paradigm described in the project vision.
