from typing import List, Tuple, Dict, Optional
from abc import ABC, abstractmethod
from .environment import GridEnvironment

class Planner(ABC):
    def __init__(self, environment: GridEnvironment):
        self.environment = environment
        self.nodes_expanded = 0
    
    @abstractmethod
    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        pass
    
    def reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], 
                        current: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [current]
        while current in came_from and came_from[current] is not None:
            current = came_from[current]
            path.append(current)
        return path[::-1]

class DeliveryAgent:
    def __init__(self, start: Tuple[int, int], goal: Tuple[int, int], 
                 environment: GridEnvironment, fuel: int = 1000):
        self.start_position = start
        self.position = start
        self.goal = goal
        self.environment = environment
        self.initial_fuel = fuel
        self.fuel = fuel
        self.path: List[Tuple[int, int]] = []
        self.total_cost = 0
        self.time_elapsed = 0
        self.history: List[Tuple[int, int]] = [start]
        
    def move(self, new_position: Tuple[int, int], time: int = None) -> bool:
        x, y = new_position
        move_cost = self.environment.get_cost(x, y, time)
        
        if (self.environment.is_valid_position(x, y, time) and 
            self.fuel >= move_cost and 
            self._is_adjacent(self.position, new_position)):
            
            self.position = new_position
            self.fuel -= move_cost
            self.total_cost += move_cost
            self.time_elapsed += 1
            self.history.append(new_position)
            return True
        return False
    
    def _is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2) == 1
    
    def has_reached_goal(self) -> bool:
        return self.position == self.goal
    
    def get_path_cost(self, path: List[Tuple[int, int]]) -> float:
        if len(path) < 2:
            return 0
        
        total_cost = 0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            total_cost += self.environment.get_cost(x2, y2)
        return total_cost
    
    def execute_path(self, path: List[Tuple[int, int]], dynamic: bool = False) -> bool:
        """Execute a planned path, handling dynamic obstacles if needed"""
        if not path or path[0] != self.position:
            return False
        
        for i, next_pos in enumerate(path[1:], 1):
            if dynamic:
                self.environment.update_dynamic_obstacles()
            
            success = self.move(next_pos, self.time_elapsed if dynamic else None)
            
            if not success:
                print(f"Movement blocked at step {i}! Replanning needed.")
                return False
            
            if self.has_reached_goal():
                print("Goal reached successfully!")
                return True
        
        return self.has_reached_goal()
    
    def get_status(self) -> Dict:
        return {
            'position': self.position,
            'fuel_remaining': self.fuel,
            'total_cost': self.total_cost,
            'time_elapsed': self.time_elapsed,
            'at_goal': self.has_reached_goal()
        }