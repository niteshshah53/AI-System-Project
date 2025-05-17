# main.py
import subprocess
import os
import sys
from typing import List, Dict, Any, Set, Tuple
from boolean_converter import convert_to_boolean_expressions, convert_to_cnf, convert_solution_to_grid

class ClueParser:
    @staticmethod
    def parse_clue(clue: str) -> Dict[str, Any]:
        """
        Parses a clue file into a structured dictionary.

        Args:
            clue: Filename of the clue (e.g., 'puzzle1.txt').

        Returns:
            Dict: Puzzle metadata including dimensions, colors, and clues.

        Raises:
            FileNotFoundError: If the clue file is missing.
            ValueError: If the puzzle type is unsupported or dimensions are invalid.
        """
        path = f"./clues/{clue}"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Clue file '{path}' not found.")

        puzzle_info = {}
        with open(path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise ValueError("Invalid clue file: Insufficient lines.")

            first_line = lines[0].split(' ')
            puzzle_type = first_line[0]
            if puzzle_type != 'rect':
                raise ValueError(f"Unsupported puzzle type: {puzzle_type}")

            try:
                rows, cols = int(first_line[1]), int(first_line[2])
            except (IndexError, ValueError) as e:
                raise ValueError(f"Invalid dimensions in clue file: {e}")

            puzzle_info['dimensions'] = (rows, cols)
            puzzle_info['puzzle_type'] = puzzle_type

            colors = {}
            color_values = "abcdefghijklmnopqrstuvwxyz"
            index = 0
            for color in lines[1].strip().split(' '):
                if color == '#ffffff':
                    colors["W"] = color
                else:
                    colors[color_values[index]] = color
                    index += 1
            puzzle_info['colors'] = colors

            clues = {}
            row_start_index = 2
            clues['rows'] = []
            for i in range(row_start_index, row_start_index + rows):
                values = lines[i].strip().split(' ')
                clues['rows'].append(values if values[0] != '' else [])

            col_start_index = row_start_index + rows
            clues['cols'] = []
            for i in range(col_start_index, col_start_index + cols):
                values = lines[i].strip().split(' ')
                clues['cols'].append(values if values[0] != '' else [])

            puzzle_info['clues'] = clues

        return puzzle_info

def write_sat_file(name: str, cnf: Tuple[Set, List[List[str]]]) -> Dict[int, str]:
    """
    Writes CNF clauses to a SAT file.

    Args:
        name: Name of the puzzle.
        cnf: CNF clauses and variables.

    Returns:
        Dict[int, str]: Mapping of variable IDs to cell values.
    """
    variables, clauses = cnf
    var_map = {}
    int_var_map = {}

    for count, var in enumerate(variables, 1):
        var_map[var] = count
        int_var_map[count] = var

    os.makedirs('sat', exist_ok=True)
    sat_file_path = os.path.join('sat', f"{name}.sat")

    with open(sat_file_path, "w") as f:
        num_clauses = len(clauses)
        num_vars = len(variables)
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        for clause in clauses:
            for expr in clause:
                if expr[0] == '-':
                    f.write(f"-{var_map[expr[1:]]} ")
                else:
                    f.write(f"{var_map[expr]} ")
            f.write("0\n")

    return int_var_map

def run_sat_solver(name: str):
    """
    Runs the SAT solver on the generated SAT file.

    Args:
        name: Name of the puzzle.

    Raises:
        FileNotFoundError: If the SAT solver is not found.
    """
    sat_file_path = os.path.join('sat', f"{name}.sat")
    os.makedirs('solution', exist_ok=True)
    solution_file_path = os.path.join('solution', f"{name}.solution")

    if not os.path.exists('/usr/bin/minisat'):
        raise FileNotFoundError("SAT solver not found at /usr/bin/minisat")

    subprocess.run(['/usr/bin/minisat', sat_file_path, solution_file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(solution_file_path, 'r') as f:
        lines = f.readlines()
    if len(lines) > 1:
        with open(solution_file_path, 'w') as f:
            f.write(lines[1])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <clue_file>")
        sys.exit(1)

    clue_file = sys.argv[1]
    puzzle_name = clue_file.split('.')[0]

    try:
        puzzle_data = ClueParser.parse_clue(clue_file)
        print(f"Read from clues complete for file: {puzzle_name}")

        if puzzle_data['puzzle_type'] == 'rect':
            boolean_exprs = convert_to_boolean_expressions(puzzle_data['clues'], puzzle_data['dimensions'])
            vars, clauses = convert_to_cnf(boolean_exprs)
            var_mapping = write_sat_file(puzzle_name, (vars, clauses))

            run_sat_solver(puzzle_name)
            solution_file_path = os.path.join('solution', f"{puzzle_name}.solution")

            with open(solution_file_path, 'r') as f:
                result = f.read().strip().split()

            result = [r for r in result if r.lstrip('-').isdigit()]
            grid_solution = convert_solution_to_grid(result, var_mapping, puzzle_data['dimensions'])

            output = ""
            for row in grid_solution:
                output += ''.join(row) + '\n'

            print("Solution:")
            print(output)

            with open(solution_file_path, 'w') as f:
                f.write(output)
        else:
            print(f"Unknown puzzle type: {puzzle_data['puzzle_type']}")
            sys.exit(1)

        print(f"Solution for {puzzle_name} has been generated and saved in the 'solution' folder.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)