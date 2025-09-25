# Autonomous Delivery Agent

An intelligent delivery agent that navigates a 2D grid city to deliver packages using various path planning algorithms.

## Features

- **Multiple Planning Algorithms**: BFS, Uniform Cost Search, A*, Hill Climbing, Simulated Annealing
- **Dynamic Environment**: Static obstacles, varying terrain costs, moving obstacles
- **Comprehensive Testing**: Unit tests and experimental comparisons
- **Visualization**: Text-based grid visualization
- **Modular Design**: Easy to extend and modify

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd delivery_agent

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
delivery_agent/
├── src/                    # Source code
│   ├── environment.py     # Grid environment and obstacles
│   ├── agent.py          # Delivery agent implementation
│   ├── planners/         # Path planning algorithms
│   └── utils.py          # Utility functions
├── maps/                 # Test maps
├── tests/               # Unit tests
├── run_agent.py         # Main CLI runner
├── experiments.py       # Algorithm comparison
└── requirements.txt     # Dependencies
```

## Usage

### Basic Usage

```bash
# Run with different planners
python run_agent.py maps/small.map --planner bfs
python run_agent.py maps/medium.map --planner ucs
python run_agent.py maps/large.map --planner astar --heuristic manhattan
```

### With Dynamic Obstacles

```bash
python run_agent.py maps/dynamic.map --planner astar --dynamic --visualize
```

### Local Search Algorithms

```bash
python run_agent.py maps/medium.map --planner hillclimb
python run_agent.py maps/medium.map --planner annealing
```

### Command Line Options

- `--planner`: Planning algorithm (bfs, ucs, astar, hillclimb, annealing)
- `--heuristic`: Heuristic for A* (manhattan, euclidean, chebyshev)
- `--dynamic`: Enable dynamic obstacles
- `--visualize`: Show grid visualization
- `--fuel`: Set initial fuel amount

## Map File Format

Map files use the following format:

```
# First line: width height
5 5
# Second line: start_x start_y goal_x goal_y  
0 0 4 4
# Grid terrain (R=road, G=grass, S=sand, W=water, X=obstacle)
R R R R R
R G G R R
R X X R R
R R R R R
R R R R R
# Moving obstacles (optional)
MOVING speed x1 y1 x2 y2 ...
```

### Terrain Costs
- Road (R): 1
- Grass (G): 3  
- Sand (S): 5
- Water (W): 10 (impassable)
- Obstacle (X): impassable

## Algorithms

### Uninformed Search
- **BFS**: Breadth-first search, optimal for step cost
- **UCS**: Uniform cost search, optimal for varying costs

### Informed Search
- **A***: Uses heuristics for efficient optimal search

### Local Search
- **Hill Climbing**: Gradient ascent with random restarts
- **Simulated Annealing**: Probabilistic acceptance of worse solutions

## Examples

### Small Map
```bash
python run_agent.py maps/small.map --planner bfs --visualize
```

### Dynamic Environment
```bash
python run_agent.py maps/dynamic.map --planner astar --dynamic --visualize
```

### Performance Comparison
```bash
python experiments.py
```

## Testing

Run unit tests:

```bash
python -m pytest tests/ -v
```

Or run individual test files:

```bash
python tests/test_environment.py
python tests/test_planners.py
python tests/test_agent.py
```

## Results Format

The program outputs:
- Path success/failure
- Path length and total cost
- Nodes expanded during search
- Execution time
- Fuel consumption

## Dynamic Replanning

When dynamic obstacles are enabled, the agent:
1. Plans an initial path considering future obstacle positions
2. Replans if the path becomes blocked during execution
3. Updates obstacle positions at each time step

## Dependencies

- Python 3.7+
- NumPy
- Matplotlib (for experiments)

## Extending the Project

### Adding New Algorithms
1. Create a new class in `src/planners/` that inherits from `Planner`
2. Implement the `plan()` method
3. Add to the planner map in `run_agent.py`

### Adding New Terrain Types
1. Add to the `Terrain` enum in `environment.py`
2. Update the map loading and visualization code

### Custom Maps
Create new `.map` files in the `maps/` directory following the format above.

## License

This project is for educational purposes as part of VITYARTHI course assignment.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run a simple test**:
   ```bash
   python run_agent.py maps/small.map --planner astar --visualize
   ```

3. **Compare all algorithms**:
   ```bash
   python experiments.py
   ```

4. **Test dynamic obstacles**:
   ```bash
   python run_agent.py maps/dynamic.map --planner ucs --dynamic
   ```

## Sample Output

```
Loaded map: maps/small.map
Grid size: 5 x 5
Start: (0, 0), Goal: (4, 4)

Using planner: A* Search
Heuristic: manhattan

Planning path...

==================================================
A* Search Results:
==================================================
Success: Yes
Path length: 9
Total cost: 13
Nodes expanded: 15
Time taken: 0.0023 seconds
Path (first 10): [(0, 0), (0, 1), (0, 2)] ... [(4, 2), (4, 3), (4, 4)]

Executing path...
Goal reached successfully!

Final Status:
Position: (4, 4)
Fuel remaining: 987
Total cost: 13
Time elapsed: 8
Goal reached: True
```

