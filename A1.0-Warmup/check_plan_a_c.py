import glob  # Library for pattern matching files using Unix shell rules

class Robot:
    def __init__(self, map):
        self.map = map
        self.rows = len(map)
        self.cols = len(map[0])
        self.cleaned = set()
        self.directions = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}

    def find_starting_points(self):
        possible_starting_points = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.map[i][j] == 'S':
                    return [(i, j)]
                elif self.map[i][j] == ' ':
                    possible_starting_points.append((i, j))
        
        if possible_starting_points:
            return possible_starting_points
        else:
            raise ValueError("No valid starting point found in the map.")

    def move(self, instruction, starting_point):
        x, y = starting_point
        if instruction in self.directions:
            dx, dy = self.directions[instruction]
            new_x = (x + dx) % self.rows
            new_y = (y + dy) % self.cols
            if self.map[new_x][new_y] != 'X':
                if self.map[new_x][new_y] == 'P':
                    for i in range(self.rows):
                        for j in range(self.cols):
                            if self.map[i][j] == 'P' and (i, j) != (new_x, new_y):
                                new_x, new_y = i, j
                                break
                        else:
                            continue
                        break
                starting_point = new_x, new_y
                if self.map[new_x][new_y] == ' ':
                    self.cleaned.add((new_x, new_y))
        return starting_point

    def count_uncleaned(self):
        uncleaned = sum(row.count(' ') for row in self.map) - len(self.cleaned)
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols) if self.map[i][j] == ' ' and (i, j) not in self.cleaned]
        positions.sort(key=lambda pos: (pos[1], pos[0]))
        return uncleaned, positions

def case_simple_map(map, instructions):
    robot = Robot(map)
    starting_points = robot.find_starting_points()
    all_uncleaned_positions = []
    for starting_point in starting_points:
        current_point = starting_point
        for instruction in instructions:
            current_point = robot.move(instruction, current_point)
        uncleaned, positions = robot.count_uncleaned()
        all_uncleaned_positions.extend(positions)
    return all_uncleaned_positions

def case_portal_known_starting_point(map, instructions, starting_point):
    robot = Robot(map)
    all_uncleaned_positions = []
    for instruction in instructions:
        starting_point = robot.move(instruction, starting_point)
    uncleaned, positions = robot.count_uncleaned()
    all_uncleaned_positions.extend(positions)
    return all_uncleaned_positions

def case_portal_unknown_starting_point(map, instructions):
    robot = Robot(map)
    starting_points = robot.find_starting_points()
    all_uncleaned_positions = set()  # Using set to avoid duplicates
    for starting_point in starting_points:
        current_point = starting_point
        robot.cleaned = set()  # Reset cleaned set for each starting point
        for instruction in instructions:
            current_point = robot.move(instruction, current_point)
        uncleaned, positions = robot.count_uncleaned()
        all_uncleaned_positions.update(positions)  # Update the set with new positions
    return sorted(all_uncleaned_positions, key=lambda pos: (pos[1], pos[0]))

def process_file(input_path, output_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines[1:] if line.strip()]
        instructions = lines[0]
        map = lines[1:]

    if 'S' in ''.join(map):
        starting_point = [(i, j) for i in range(len(map)) for j in range(len(map[0])) if map[i][j] == 'S'][0]
        if 'P' in ''.join(map):
            all_uncleaned_positions = case_portal_known_starting_point(map, instructions, starting_point)
        else:
            all_uncleaned_positions = case_simple_map(map, instructions)
    else:
        all_uncleaned_positions = case_portal_unknown_starting_point(map, instructions)

    with open(output_path, 'w') as output_file:
        if all_uncleaned_positions:
            output_file.write("BAD PLAN\n")
            for position in all_uncleaned_positions:
                output_file.write(f"{position[1]}, {position[0]}\n")
        else:
            output_file.write("GOOD PLAN\n")
def main():
    input_files = glob.glob('C:/Users/rider/Desktop/MsAI/Projects/AISys1/ca39rapa-1/Assignment1.0/problems/problem_*.txt')
    
    # Organizing based on cases
    case1_files = input_files[:20]
    case2_files = input_files[20:40]
    case3_files = input_files[40:60]

    # Processing files for each case
    for input_path in case1_files:
        output_path = input_path.replace('problems', 'solutions').replace('problem_', 'solution_')
        process_file(input_path, output_path)

    for input_path in case2_files:
        output_path = input_path.replace('problems', 'solutions').replace('problem_', 'solution_')
        process_file(input_path, output_path)

    for input_path in case3_files:
        output_path = input_path.replace('problems', 'solutions').replace('problem_', 'solution_')
        process_file(input_path, output_path)

if __name__ == '__main__':
    main()
