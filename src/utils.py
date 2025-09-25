import time
import json
from typing import List, Tuple, Dict
from .environment import GridEnvironment

def load_map(filename: str) -> Tuple[GridEnvironment, Tuple[int, int], Tuple[int, int]]:
    """Load map from file and return environment with start and goal positions"""
    env = GridEnvironment(1, 1)  # Temporary, will be resized
    start, goal = env.load_from_file(filename)
    return env, start, goal

def calculate_path_cost(path: List[Tuple[int, int]], env: GridEnvironment) -> float:
    """Calculate total cost of a path"""
    if len(path) < 2:
        return 0
    
    total_cost = 0
    for i in range(len(path) - 1):
        x, y = path[i + 1]
        cost = env.get_cost(x, y)
        if cost == float('inf'):
            return float('inf')
        total_cost += cost
    return total_cost

def print_statistics(planner_name: str, path: List[Tuple[int, int]], 
                    nodes_expanded: int, time_taken: float, env: GridEnvironment):
    """Print planning statistics"""
    path_length = len(path) if path else 0
    total_cost = calculate_path_cost(path, env) if path else float('inf')
    success = path is not None and len(path) > 0 and path[-1] == env.goal if hasattr(env, 'goal') else False
    
    print(f"\n{'='*50}")
    print(f"{planner_name} Results:")
    print(f"{'='*50}")
    print(f"Success: {'Yes' if success else 'No'}")
    print(f"Path length: {path_length}")
    print(f"Total cost: {total_cost if total_cost != float('inf') else 'Infinite'}")
    print(f"Nodes expanded: {nodes_expanded}")
    print(f"Time taken: {time_taken:.4f} seconds")
    
    if path and len(path) > 10:
        print(f"Path (first 10): {path[:5]} ... {path[-5:]}")
    elif path:
        print(f"Path: {path}")

def save_results(results: Dict, filename: str):
    """Save experiment results to JSON file"""
    with open(filename, 'w') as f:
        # Convert any non-serializable values
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                serializable_results[key] = value
            else:
                serializable_results[key] = str(value)
        
        json.dump(serializable_results, f, indent=2)

def visualize_path(env: GridEnvironment, path: List[Tuple[int, int]], 
                  agent_pos: Tuple[int, int] = None):
    """Visualize the environment with path and agent position"""
    print("\nGrid Visualization:")
    symbols = {
        'road': '.',
        'grass': 'g', 
        'sand': 's',
        'water': '~',
        'obstacle': 'X',
        'dynamic': 'D',
        'agent': 'A',
        'path': '*',
        'start': 'S',
        'goal': 'G'
    }
    
    print("+" + "-" * (env.width * 2) + "+")
    for y in range(env.height):
        row = "|"
        for x in range(env.width):
            cell = env.grid[y][x]
            
            if agent_pos and (x, y) == agent_pos:
                row += " A"
            elif path and (x, y) in path:
                idx = path.index((x, y))
                if idx == 0:
                    row += " S"
                elif idx == len(path) - 1:
                    row += " G"
                else:
                    row += " *"
            elif cell.is_obstacle:
                row += " X"
            elif cell.dynamic_obstacle:
                row += " D"
            else:
                if cell.terrain.value == 1:  # Road
                    row += " ."
                elif cell.terrain.value == 3:  # Grass
                    row += " g"
                elif cell.terrain.value == 5:  # Sand
                    row += " s"
                elif cell.terrain.value == 10:  # Water
                    row += " ~"
                else:
                    row += " ?"
        row += " |"
        print(row)
    print("+" + "-" * (env.width * 2) + "+")
    
    print("\nLegend: S=Start, G=Goal, A=Agent, *=Path, X=Obstacle, D=Dynamic, .=Road, g=Grass, s=Sand, ~=Water")