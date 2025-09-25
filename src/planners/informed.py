import heapq
from typing import List, Tuple, Dict
from src.agent import Planner

class AStarPlanner(Planner):
    def __init__(self, environment, heuristic_type='manhattan'):
        super().__init__(environment)
        self.heuristic_type = heuristic_type
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        x1, y1 = a
        x2, y2 = b
        
        if self.heuristic_type == 'manhattan':
            return abs(x1 - x2) + abs(y1 - y2)
        elif self.heuristic_type == 'euclidean':
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        elif self.heuristic_type == 'chebyshev':
            return max(abs(x1 - x2), abs(y1 - y2))
        else:
            return 0  # Fallback to UCS
    
    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        self.nodes_expanded = 0
        
        if start == goal:
            return [start]
        
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current_priority, current = heapq.heappop(frontier)
            self.nodes_expanded += 1
            
            if current == goal:
                return self.reconstruct_path(came_from, current)
            
            x, y = current
            neighbors = self.environment.get_neighbors(x, y)
            
            for nx, ny, move_cost in neighbors:
                neighbor = (nx, ny)
                new_cost = cost_so_far[current] + move_cost
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, goal)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current
        
        return []  # No path found