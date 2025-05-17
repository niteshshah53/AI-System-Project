import sys

def generate_pddl_problem(map_file, problem_file):
    with open(map_file, 'r') as f:
        map_data = [line.rstrip() for line in f]  # Preserve leading spaces

    rows = len(map_data)
    cols = max(len(row) for row in map_data)  # Use the longest row for column count

    problem = f"""
(define (problem wumpus-escape-{map_file.split('.')[0]})
  (:domain wumpus-world)
  (:objects
    agent - agent
    {' '.join([f'loc-{i}-{j}' for i in range(rows) for j in range(cols)])} - location
    north south east west - direction
  )
  (:init
    {generate_adjacency(rows, cols)}
    {generate_map_objects(map_data, cols)}
    {generate_edge_cells(rows, cols)}
  )
  (:goal (free agent))
)
"""
    with open(problem_file, 'w') as f:
        f.write(problem.strip())

def generate_adjacency(rows, cols):
    adjacency = []
    for i in range(rows):
        for j in range(cols):
            if i > 0:
                adjacency.append(f"(adjacent loc-{i}-{j} loc-{i-1}-{j} north)")
            if i < rows - 1:
                adjacency.append(f"(adjacent loc-{i}-{j} loc-{i+1}-{j} south)")
            if j > 0:
                adjacency.append(f"(adjacent loc-{i}-{j} loc-{i}-{j-1} west)")
            if j < cols - 1:
                adjacency.append(f"(adjacent loc-{i}-{j} loc-{i}-{j+1} east)")
    return '\n    '.join(adjacency)

def generate_map_objects(map_data, cols):
    objects = []
    for i, row in enumerate(map_data):
        for j, cell in enumerate(row):
            loc = f"loc-{i}-{j}"
            if cell == 'S':
                objects.append(f"(at agent {loc})")
                objects.append(f"(empty {loc})")
            elif cell == 'X':
                objects.append(f"(wall {loc})")
            elif cell == 'W':
                objects.append(f"(wumpus {loc})")
            elif cell == 'A':
                objects.append(f"(arrow {loc})")
            elif cell == 'K':
                objects.append(f"(key {loc})")
            elif cell == 'D':
                objects.append(f"(door {loc})")
            elif cell == 'C':
                objects.append(f"(crate {loc})")
            elif cell == 'T':
                objects.append(f"(trampoline {loc})")
            elif cell == ' ' or cell == 'Z':  # Handle both space and 'Z' as empty
                objects.append(f"(empty {loc})")
        
        # Fill in any remaining columns with empty spaces
        for j in range(len(row), cols):
            objects.append(f"(empty loc-{i}-{j})")
    
    return '\n    '.join(objects)

def generate_edge_cells(rows, cols):
    edge_cells = []
    for i in range(rows):
        edge_cells.append(f"(edge loc-{i}-0 west)")
        edge_cells.append(f"(edge loc-{i}-{cols-1} east)")
    for j in range(cols):
        edge_cells.append(f"(edge loc-0-{j} north)")
        edge_cells.append(f"(edge loc-{rows-1}-{j} south)")
    return '\n    '.join(edge_cells)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_problem.py <map_file> <problem_file>")
        sys.exit(1)
    
    map_file = sys.argv[1]
    problem_file = sys.argv[2]
    generate_pddl_problem(map_file, problem_file)