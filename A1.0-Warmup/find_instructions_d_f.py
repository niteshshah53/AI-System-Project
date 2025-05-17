from collections import deque
import random

class Robot:
    def __init__(self, map):
        self.map = [list(row) for row in map]
        self.directions = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
        self.start = self.find_start()
        self.portals = self.find_portals()
        self.instructions = []
    
    def find_start(self):
        start_positions = []
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j] == 'S':
                    return (i, j)
                elif self.map[i][j] == ' ':
                    start_positions.append((i, j))
        
        # If there is no explicit starting point, choose randomly from available empty spaces
        if start_positions:
            return random.choice(start_positions)
        else:
            raise ValueError("No starting point ('S') or empty spaces ('.') found in the map.")

    def find_portals(self):
        portals = []
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j] == 'P':
                    portals.append((i, j))
        return portals
    
    def bfs(self, start):
        queue = deque([(start, [])])
        visited = set()
        visited.add(start)
        
        while queue:
            (x, y), path = queue.popleft()
            
            for direction, (dx, dy) in self.directions.items():
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < len(self.map) and 0 <= ny < len(self.map[0]) and (nx, ny) not in visited:
                    if self.map[nx][ny] == ' ':
                        return (nx, ny), path + [direction]
                    elif self.map[nx][ny] == 'S' or self.map[nx][ny] == '.':
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [direction]))
                    elif self.map[nx][ny] == 'P':
                        visited.add((nx, ny))
                        for portal in self.portals:
                            if portal != (nx, ny) and portal not in visited:
                                queue.append((portal, path + [direction]))
                                visited.add(portal)                            
        return None, []

    def clean(self):
        current_pos = self.start
        
        while True:
            new_pos, new_path = self.bfs(current_pos)
            if not new_path:
                break
            
            self.instructions.extend(new_path)
            current_pos = new_pos
            self.map[current_pos[0]][current_pos[1]] = '.'  # Mark as cleaned
        
        return ''.join(self.instructions)

def process_file(input_filename, output_filename):
    with open(input_filename, 'r') as f:
        lines = f.readlines()[1:]  # Ignore the first line
        map = [line.strip() for line in lines]
    
    robot = Robot(map)
    solution = robot.clean()
    
    with open(output_filename, 'w') as f:
        f.write(solution)

# Process 20 input files
for i in range(20):
    input_filename = f"C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/problems/problem_d_{i:02}.txt"
    output_filename = f"C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/solutions/solution_d_{i:02}.txt"
    process_file(input_filename, output_filename)

# Processing the second set of problem files (problem_e_00.txt to problem_e_19.txt)
for i in range(20):
    input_filename_e = f"C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/problems/problem_e_{i:02}.txt"
    output_filename_e = f"C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/solutions/solution_e_{i:02}.txt"
    process_file(input_filename_e, output_filename_e)

# Processing the second set of problem files (problem_f_00.txt to problem_f_19.txt)
for i in range(20):
    input_filename_f = f"C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/problems/problem_f_{i:02}.txt"
    output_filename_f = f"C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/solutions/solution_f_{i:02}.txt"
    process_file(input_filename_f, output_filename_f)