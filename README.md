# GROOTZERO - Autonomous Sim2Real Robotics Pipeline

## Project Overview

GROOTZERO is an end-to-end sim-to-real robotics pipeline that integrates a zero-data self-play learning loop (inspired by Absolute Zero Reasoner - AZR) with NVIDIA Isaac Sim for high-fidelity simulation and the NVIDIA GR00T N1 foundation model for task proposal and controller synthesis. The ultimate goal is a system that can autonomously generate robotics tasks, learn to solve them in simulation, and transfer that learning to real-world (or simulated real-world equivalent) hardware with minimal human-curated data.

## Core Components

- **Absolute Zero Reasoner (AZR)**: A self-play loop where an LLM proposes Python-based tasks and attempts to solve them, learning from binary success/fail rewards.
- **NVIDIA Isaac Sim**: Used as the primary simulation environment for task execution, physics simulation, domain randomization, and providing success/fail feedback.
- **NVIDIA GR00T N1 Foundation Model**: Used for task definition and controller synthesis.
- **Sim2Real Transfer**: Facilitated by domain randomization in Isaac Sim and a structured approach to validating simulated policies.

## Project Structure

- `src/`: Core source code for the project
- `sim_environments/`: Isaac Sim environment configurations and setup scripts
- `controllers/`: Robot controller implementations
- `tasks/`: Task definition scripts
- `reports/`: Project progress reports
- `docs/`: Documentation files

## Getting Started

*Detailed setup instructions will be added as the project develops.*
