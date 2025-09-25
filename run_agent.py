#!/usr/bin/env python3
"""
Autonomous Delivery Agent Runner
"""

import argparse
import time
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from environment import GridEnvironment
from agent import DeliveryAgent
from planners.uninformed import BFSPlanner, UniformCostPlanner
from planners.informed import AStarPlanner
from planners.local_search import HillClimbingPlanner, SimulatedAnnealingPlanner
from utils import load_map, print_statistics, visualize_path

def main():
    parser = argparse.ArgumentParser(description='Autonomous Delivery Agent')
    parser.add_argument('map_file', help='Path to the map file')
    parser.add_argument('--planner', choices=['bfs', 'ucs', 'astar', 'hillclimb', 'annealing'],
                       default='astar', help='Path planning algorithm')
    parser.add_argument('--heuristic', choices=['manhattan', 'euclidean', 'chebyshev'],
                       default='manhattan', help='Heuristic for A*')
    parser.add_argument('--dynamic', action='store_true', help='Enable dynamic obstacles')
    parser.add_argument('--visualize', action='store_true', help='Show visualization')
    parser.add_argument('--fuel', type=int, default=1000, help='Initial fuel amount')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.map_file):
        print(f"Error: Map file '{args.map_file}' not found")
        return 1
    
    try:
        # Load environment and positions
        env, start, goal = load_map(args.map_file)
        
        print(f"Loaded map: {args.map_file}")
        print(f"Grid size: {env.width} x {env.height}")
        print(f"Start: {start}, Goal: {goal}")
        
        # Create agent
        agent = DeliveryAgent(start, goal, env, fuel=args.fuel)
        
        # Select planner
        planner_map = {
            'bfs': BFSPlanner(env),
            'ucs': UniformCostPlanner(env),
            'astar': AStarPlanner(env, args.heuristic),
            'hillclimb': HillClimbingPlanner(env),
            'annealing': SimulatedAnnealingPlanner(env)
        }
        
        planner = planner_map[args.planner]
        planner_name = {
            'bfs': 'Breadth-First Search',
            'ucs': 'Uniform Cost Search', 
            'astar': 'A* Search',
            'hillclimb': 'Hill Climbing',
            'annealing': 'Simulated Annealing'
        }[args.planner]
        
        print(f"\nUsing planner: {planner_name}")
        if args.planner == 'astar':
            print(f"Heuristic: {args.heuristic}")
        
        # Plan path
        print("\nPlanning path...")
        start_time = time.time()
        path = planner.plan(start, goal)
        planning_time = time.time() - start_time
        
        # Print statistics
        print_statistics(planner_name, path, planner.nodes_expanded, planning_time, env)
        
        if not path:
            print("No path found!")
            return 1
        
        # Visualize if requested
        if args.visualize:
            visualize_path(env, path, start)
        
        # Execute path
        print(f"\nExecuting path...")
        success = agent.execute_path(path, dynamic=args.dynamic)
        
        # Print final status
        status = agent.get_status()
        print(f"\nFinal Status:")
        print(f"Position: {status['position']}")
        print(f"Fuel remaining: {status['fuel_remaining']}")
        print(f"Total cost: {status['total_cost']}")
        print(f"Time elapsed: {status['time_elapsed']}")
        print(f"Goal reached: {status['at_goal']}")
        
        if args.visualize:
            visualize_path(env, path, agent.position)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())