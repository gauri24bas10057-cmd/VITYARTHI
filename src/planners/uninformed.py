from collections import deque
import heapq
from typing import List, Tuple, Dict
from src.agent import Planner

class BFSPlanner(Planner):
    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        self.nodes_expanded = 0
        
        if start == goal:
            return [start]
        
        queue = deque([start])
        came_from = {start: None}
        visited = set([start])
        
        while queue:
            current = queue.popleft()
            self.nodes_expanded += 1
            
            if current == goal:
                return self.reconstruct_path(came_from, current)
            
            x, y = current
            neighbors = self.environment.get_neighbors(x, y)
            
            for nx, ny, cost in neighbors:
                neighbor = (nx, ny)
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
        
        return []  # No path found

class UniformCostPlanner(Planner):
    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        self.nodes_expanded = 0
        
        if start == goal:
            return [start]
        
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current_cost, current = heapq.heappop(frontier)
            self.nodes_expanded += 1
            
            if current == goal:
                return self.reconstruct_path(came_from, current)
            
            x, y = current
            neighbors = self.environment.get_neighbors(x, y)
            
            for nx, ny, move_cost in neighbors:
                neighbor = (nx, ny)
                new_cost = current_cost + move_cost
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(frontier, (new_cost, neighbor))
                    came_from[neighbor] = current
        
        return []  # No path found