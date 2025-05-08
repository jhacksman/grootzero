# Task 1.5: Basic Reinforcement Learning Feedback Mechanism

## Objective

The primary goal of Task 1.5 was to implement a basic reinforcement learning (RL) feedback mechanism for the AZR learning loop. This mechanism allows the outcomes of simulation tasks (rewards) to influence future decisions made by the MockGR00TN1 system, creating a rudimentary learning capability that adapts based on past performance.

## Implementation Overview

The implementation focuses on controller selection adaptation, where successful controllers are more likely to be selected for similar tasks in the future. This creates a simple but effective feedback loop that demonstrates the core principles of reinforcement learning.

### Key Components

1. **Reward Function**: A reward calculation system that evaluates controller performance based on task success, time efficiency, path efficiency, and energy efficiency.

2. **Reinforcement Feedback Mechanism**: A method in MockGR00TN1 that adjusts controller selection probabilities based on received rewards.

3. **Integration with AZR Loop**: Updates to the AZRLearningLoop to calculate rewards and apply feedback after each episode.

4. **Enhanced Logging**: Comprehensive logging to observe the learning process and adaptation over time.

## Reward Function Design

The reward function (`calculate_reward`) in `src/grootzero/azr/rewards.py` implements a multi-factor reward calculation:

1. **Base Reward**: +1.0 for success, -1.0 for failure
2. **Time Efficiency Bonus**: Up to +0.5 for completing tasks quickly
3. **Path Efficiency Bonus**: Up to +0.3 for efficient movement paths
4. **Energy Efficiency Bonus**: Up to +0.2 for energy-efficient solutions
5. **Difficulty Adjustment**: Rewards are scaled based on task difficulty (easy: x0.8, medium: x1.0, hard: x1.2)

A normalized version (`calculate_normalized_reward`) is also provided, which maps rewards to the range [-1, 1] using the tanh function, useful for some RL algorithms.

## RL Feedback Mechanism

The reinforcement learning feedback mechanism is implemented in the `apply_reinforcement_feedback` method of the `MockGR00TN1` class. The key aspects of this implementation are:

### Data Structures

1. **Controller Performance Tracking**: A dictionary that maps controller indices to performance metrics, including total reward, success count, and task-specific performance.

2. **Controller Selection Weights**: A list of weights that influence the probability of selecting each controller. These weights are adjusted based on rewards.

3. **Task Type to Controller Mapping**: A dictionary that maps task types to lists of successful controllers, enabling task-specific controller selection.

### Update Logic

The update logic follows a simple rule:

```
new_weight = current_weight + learning_rate * reward
```

Where:
- `current_weight` is the existing selection weight for the controller
- `learning_rate` is a configurable parameter (default: 0.1) that controls how quickly weights adapt
- `reward` is the calculated reward value from the task execution

This approach ensures that:
- Controllers that receive positive rewards have their selection probability increased
- Controllers that receive negative rewards have their selection probability decreased
- The magnitude of the adjustment is proportional to both the reward and the learning rate

A minimum weight of 0.1 is enforced to ensure all controllers maintain some probability of selection, preventing premature convergence and allowing for exploration.

### Controller Selection

The controller selection process in `_get_controller_by_selection_mode` has been enhanced to use these weights:

1. **Random Mode**: Uses weighted random selection based on the adjusted weights
2. **Match Task Mode**: Incorporates a 70% chance to use controllers that previously succeeded on similar task types
3. **Sequential Mode**: Remains unchanged for deterministic testing

## Integration with AZR Learning Loop

The AZRLearningLoop has been updated to:

1. Import the reward calculation functions
2. Calculate rewards after task execution in the `run_episode` method
3. Call `apply_reinforcement_feedback` on the GR00T N1 interface to pass the feedback
4. Include the reward in the learning history and episode results
5. Add enhanced logging to track the reinforcement learning process

## How to Observe the Learning Effect

The learning effect can be observed by running the provided example script:

```bash
python examples/azr/reinforcement_learning_test.py --num-episodes 10 --controller-selection random --learning-rate 0.1
```

Key indicators of learning in the logs:

1. **Controller Selection Weights**: The weights for successful controllers should increase over time, while weights for unsuccessful controllers should decrease.

2. **Task Type to Controller Mapping**: Successful controllers should be associated with specific task types.

3. **Success Rate**: The overall success rate should improve over multiple episodes as the system learns which controllers work best for which tasks.

4. **Reward Trends**: Average rewards should trend upward as the system learns to select better controllers.

The example script outputs detailed information about controller selection weights and task-type mappings after running all episodes, making it easy to observe the learning effect.

## Limitations

This implementation has several deliberate simplifications:

1. **Focus on Controller Selection**: The current implementation only adapts controller selection, not task proposal.

2. **Simple Update Rule**: The weight update rule is a basic linear adjustment rather than a more sophisticated RL algorithm.

3. **Limited Memory**: The system doesn't implement experience replay or other techniques to leverage historical data more effectively.

4. **No Exploration Strategy**: There's no explicit exploration strategy beyond the inherent randomness in controller selection.

5. **No Hyperparameter Tuning**: The learning rate and other parameters are fixed rather than adaptively tuned.

These limitations are appropriate for this initial implementation, which focuses on establishing the core feedback pathway rather than implementing a sophisticated RL algorithm.

## Testing

The implementation includes comprehensive unit tests:

1. **Reward Function Tests** (`tests/azr/test_rewards.py`): Tests for the reward calculation functions, including success/failure cases, difficulty adjustment, and normalization.

2. **RL Feedback Tests** (`tests/azr/test_rl_feedback.py`): Tests for the reinforcement learning feedback mechanism, including positive/negative feedback, learning rate effects, and controller selection probability changes.

These tests ensure that the reward calculation and feedback mechanism work as expected and that the learning effect is observable.

## Next Steps

Future enhancements to the learning mechanism could include:

1. **Task Proposal Adaptation**: Extending the feedback mechanism to adapt task proposal based on past performance.

2. **More Sophisticated RL Algorithms**: Implementing more advanced algorithms like REINFORCE++ or Q-learning.

3. **Experience Replay**: Adding a memory buffer to store and replay past experiences for more efficient learning.

4. **Exploration Strategies**: Implementing explicit exploration strategies like epsilon-greedy or UCB.

5. **Hyperparameter Tuning**: Adding mechanisms to adaptively tune learning rates and other parameters.

6. **Multi-Agent Learning**: Extending the system to support multiple agents learning from each other.

7. **Transfer Learning**: Enabling knowledge transfer between similar tasks.

These enhancements would move the system closer to the sophisticated learning capabilities envisioned for the full GROOTZERO project.

## Conclusion

The basic reinforcement learning feedback mechanism implemented in Task 1.5 establishes the core feedback pathway where task outcomes influence future decisions made by the MockGR00TN1 system. While deliberately simplified, it demonstrates the fundamental principles of reinforcement learning and provides a foundation for more sophisticated learning mechanisms in future tasks.
