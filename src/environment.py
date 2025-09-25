import numpy as np
from enum import Enum
from typing import List, Tuple, Dict, Optional

class Terrain(Enum):
    ROAD = 1
    GRASS = 3
    SAND = 5
    WATER = 10  # Unpassable

class Cell:
    def __init__(self, terrain: Terrain = Terrain.ROAD, is_obstacle: bool = False):
        self.terrain = terrain
        self.is_obstacle = is_obstacle
        self.dynamic_obstacle = False
        self.update_cost()
    
    def update_cost(self):
        if self.is_obstacle:
            self.cost = float('inf')
        else:
            self.cost = self.terrain.value
    
    def set_dynamic_obstacle(self, is_obstacle: bool):
        self.dynamic_obstacle = is_obstacle
        self.update_cost()

class MovingObstacle:
    def __init__(self, path: List[Tuple[int, int]], speed: int = 1):
        self.path = path
        self.speed = speed
        self.current_step = 0
        self.position_index = 0
    
    def get_position_at_time(self, time_step: int) -> Tuple[int, int]:
        effective_step = (time_step // self.speed) % len(self.path)
        return self.path[effective_step]
    
    def update(self, time_step: int) -> Tuple[int, int]:
        self.current_step = time_step
        self.position_index = (time_step // self.speed) % len(self.path)
        return self.path[self.position_index]

class GridEnvironment:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = np.empty((height, width), dtype=object)
        self.moving_obstacles: List[MovingObstacle] = []
        self.time_step = 0
        
        # Initialize grid with default terrain
        for y in range(height):
            for x in range(width):
                self.grid[y][x] = Cell(Terrain.ROAD)
    
    def set_terrain(self, x: int, y: int, terrain: Terrain):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].terrain = terrain
            self.grid[y][x].update_cost()
    
    def set_static_obstacle(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].is_obstacle = True
            self.grid[y][x].update_cost()
    
    def add_moving_obstacle(self, path: List[Tuple[int, int]], speed: int = 1):
        obstacle = MovingObstacle(path, speed)
        self.moving_obstacles.append(obstacle)
    
    def update_dynamic_obstacles(self):
        """Update positions of moving obstacles for current time step"""
        self.time_step += 1
        
        # Clear previous dynamic obstacles
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].set_dynamic_obstacle(False)
        
        # Set new dynamic obstacle positions
        for obstacle in self.moving_obstacles:
            x, y = obstacle.update(self.time_step)
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x].set_dynamic_obstacle(True)
    
    def get_cost(self, x: int, y: int, time: int = None) -> float:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return float('inf')
        
        cell = self.grid[y][x]
        
        # Check if cell is blocked at the given time
        if time is not None:
            for obstacle in self.moving_obstacles:
                obs_x, obs_y = obstacle.get_position_at_time(time)
                if (x, y) == (obs_x, obs_y):
                    return float('inf')
        
        return cell.cost
    
    def is_valid_position(self, x: int, y: int, time: int = None) -> bool:
        return self.get_cost(x, y, time) < float('inf')
    
    def get_neighbors(self, x: int, y: int, time: int = None) -> List[Tuple[int, int, int]]:
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4-connected movement
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                cost = self.get_cost(nx, ny, time)
                if cost < float('inf'):
                    neighbors.append((nx, ny, cost))
        
        return neighbors

    def load_from_file(self, filename: str):
        terrain_map = {
            'R': Terrain.ROAD,
            'G': Terrain.GRASS,
            'S': Terrain.SAND,
            'W': Terrain.WATER,
            'X': 'OBSTACLE'
        }
        
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if len(lines) < 3:
            raise ValueError("Map file must have at least 3 lines")
        
        # Parse dimensions
        dims = lines[0].split()
        if len(dims) != 2:
            raise ValueError("First line must contain two integers: width height")
        
        width, height = int(dims[0]), int(dims[1])
        
        # Resize grid if necessary
        if width != self.width or height != self.height:
            self.__init__(width, height)
        
        # Parse start and goal
        positions = lines[1].split()
        if len(positions) != 4:
            raise ValueError("Second line must contain four integers: start_x start_y goal_x goal_y")
        
        start_x, start_y, goal_x, goal_y = map(int, positions)
        
        # Parse grid
        grid_lines = lines[2:2+height]
        if len(grid_lines) < height:
            raise ValueError(f"Expected {height} grid lines, got {len(grid_lines)}")
        
        for y, line in enumerate(grid_lines):
            if len(line) != width:
                raise ValueError(f"Line {y+3} has length {len(line)}, expected {width}")
            
            for x, char in enumerate(line):
                if char in terrain_map:
                    if char == 'X':
                        self.set_static_obstacle(x, y)
                    else:
                        self.set_terrain(x, y, terrain_map[char])
        
        # Parse moving obstacles if present
        for line in lines[2+height:]:
            if line.startswith('MOVING'):
                parts = line.split()
                if len(parts) >= 3:
                    speed = int(parts[1])
                    path = []
                    for i in range(2, len(parts), 2):
                        if i+1 < len(parts):
                            x, y = int(parts[i]), int(parts[i+1])
                            path.append((x, y))
                    if path:
                        self.add_moving_obstacle(path, speed)
        
        return (start_x, start_y), (goal_x, goal_y)

    def visualize(self, agent_pos: Tuple[int, int] = None, path: List[Tuple[int, int]] = None):
        """Simple text visualization of the grid"""
        symbols = {
            Terrain.ROAD: '.',
            Terrain.GRASS: 'g',
            Terrain.SAND: 's',
            Terrain.WATER: '~'
        }
        
        print("\n" + "=" * (self.width * 2 + 1))
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                cell = self.grid[y][x]
                
                if agent_pos and (x, y) == agent_pos:
                    row += "A|"
                elif path and (x, y) in path:
                    index = path.index((x, y))
                    row += f"{index % 10}|"
                elif cell.is_obstacle:
                    row += "X|"
                elif cell.dynamic_obstacle:
                    row += "D|"
                else:
                    symbol = symbols.get(cell.terrain, '?')
                    row += f"{symbol}|"
            print(row)
        print("=" * (self.width * 2 + 1))