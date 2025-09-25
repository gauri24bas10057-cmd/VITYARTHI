import random
import math
from typing import List, Tuple, Dict
from src.agent import Planner

class HillClimbingPlanner(Planner):
    def __init__(self, environment, max_iterations=1000, max_sideways=100):
        super().__init__(environment)
        self.max_iterations = max_iterations
        self.max_sideways = max_sideways
    
    def get_random_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                       max_length: int = 50) -> List[Tuple[int, int]]:
        """Generate a random valid path using random walks"""
        path = [start]
        current = start
        steps = 0
        
        while current != goal and steps < max_length:
            x, y = current
            neighbors = self.environment.get_neighbors(x, y)
            valid_neighbors = [n for n in neighbors if n[:2] not in path]
            
            if not valid_neighbors:
                # Dead end, try to backtrack
                if len(path) > 1:
                    path.pop()
                    current = path[-1]
                else:
                    break
                continue
            
            next_pos = random.choice(valid_neighbors)[:2]
            path.append(next_pos)
            current = next_pos
            steps += 1
        
        return path if current == goal else []
    
    def path_cost(self, path: List[Tuple[int, int]]) -> float:
        """Calculate total cost of a path"""
        if len(path) < 2:
            return float('inf')
        
        total_cost = 0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            cost = self.environment.get_cost(x2, y2)
            if cost == float('inf'):
                return float('inf')
            total_cost += cost
        return total_cost
    
    def get_neighbor_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate a neighboring path by mutation"""
        if len(path) <= 2:
            return path
        
        new_path = path.copy()
        mutation_type = random.choice(['swap', 'insert', 'remove', 'replace'])
        
        try:
            if mutation_type == 'swap' and len(path) > 3:
                i = random.randint(1, len(path) - 3)
                new_path[i], new_path[i + 1] = new_path[i + 1], new_path[i]
            
            elif mutation_type == 'insert' and len(path) > 2:
                i = random.randint(1, len(path) - 2)
                x, y = new_path[i]
                neighbors = self.environment.get_neighbors(x, y)
                if neighbors:
                    new_pos = random.choice(neighbors)[:2]
                    if new_pos not in new_path:
                        new_path.insert(i + 1, new_pos)
            
            elif mutation_type == 'remove' and len(path) > 3:
                i = random.randint(1, len(path) - 2)
                # Check if removal maintains connectivity
                if i > 0 and i < len(new_path) - 1:
                    prev = new_path[i - 1]
                    next_pos = new_path[i + 1]
                    if self._are_adjacent(prev, next_pos):
                        new_path.pop(i)
            
            elif mutation_type == 'replace' and len(path) > 2:
                i = random.randint(1, len(path) - 2)
                x, y = new_path[i]
                neighbors = self.environment.get_neighbors(x, y)
                if neighbors:
                    new_pos = random.choice(neighbors)[:2]
                    if new_pos not in new_path:
                        new_path[i] = new_pos
            
        except (IndexError, ValueError):
            return path  # Return original if mutation fails
        
        return new_path if self._is_valid_path(new_path) else path
    
    def _are_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2) == 1
    
    def _is_valid_path(self, path: List[Tuple[int, int]]) -> bool:
        """Check if path is valid (connected and traversable)"""
        if not path or path[0] != path[0] or path[-1] != path[-1]:
            return False
        
        for i in range(len(path) - 1):
            if not self._are_adjacent(path[i], path[i + 1]):
                return False
            if not self.environment.is_valid_position(path[i + 1][0], path[i + 1][1]):
                return False
        
        return True
    
    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        self.nodes_expanded = 0
        
        # Generate initial solution
        current_path = self.get_random_path(start, goal)
        if not current_path:
            return []
        
        current_cost = self.path_cost(current_path)
        best_path = current_path.copy()
        best_cost = current_cost
        sideways_moves = 0
        
        for iteration in range(self.max_iterations):
            self.nodes_expanded += 1
            
            # Generate neighbor
            neighbor_path = self.get_neighbor_path(current_path)
            neighbor_cost = self.path_cost(neighbor_path)
            
            if neighbor_cost < current_cost:
                # Better solution found
                current_path = neighbor_path
                current_cost = neighbor_cost
                sideways_moves = 0
                
                if neighbor_cost < best_cost:
                    best_path = neighbor_path.copy()
                    best_cost = neighbor_cost
            
            elif neighbor_cost == current_cost and sideways_moves < self.max_sideways:
                # Equal cost, accept with sideways motion
                current_path = neighbor_path
                sideways_moves += 1
            
            else:
                # Random restart
                current_path = self.get_random_path(start, goal)
                if not current_path:
                    continue
                current_cost = self.path_cost(current_path)
                sideways_moves = 0
            
            # Check for goal
            if current_path and current_path[-1] == goal:
                if self.path_cost(current_path) < best_cost:
                    best_path = current_path.copy()
                break
        
        return best_path if best_path and best_path[-1] == goal else []

class SimulatedAnnealingPlanner(HillClimbingPlanner):
    def __init__(self, environment, initial_temp=1000, cooling_rate=0.95, min_temp=1):
        super().__init__(environment)
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
    
    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        self.nodes_expanded = 0
        
        current_path = self.get_random_path(start, goal)
        if not current_path:
            return []
        
        current_cost = self.path_cost(current_path)
        best_path = current_path.copy()
        best_cost = current_cost
        
        temperature = self.initial_temp
        
        while temperature > self.min_temp and current_path[-1] != goal:
            self.nodes_expanded += 1
            
            neighbor_path = self.get_neighbor_path(current_path)
            neighbor_cost = self.path_cost(neighbor_path)
            
            cost_diff = neighbor_cost - current_cost
            
            if cost_diff < 0 or random.random() < math.exp(-cost_diff / temperature):
                current_path = neighbor_path
                current_cost = neighbor_cost
                
                if current_cost < best_cost and current_path[-1] == goal:
                    best_path = current_path.copy()
                    best_cost = current_cost
            
            temperature *= self.cooling_rate
        
        return best_path if best_path and best_path[-1] == goal else []