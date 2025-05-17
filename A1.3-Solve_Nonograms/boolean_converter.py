# boolean_converter.py
from typing import List, Dict, Any, Tuple, Set
from pattern_generator import generate_permutations, PatternGenerator

# Global counter for auxiliary variables in CNF conversion.
# Note: Not thread-safe. Reset to 1 if processing multiple puzzles sequentially.
_counter = 1  # Renamed to avoid shadowing the keyword 'counter'

def convert_to_boolean_expressions(clue: Dict, size: Tuple[int, int]) -> Dict:
    """
    Converts row/column clues into boolean expressions for SAT solving.

    Args:
        clue: Dictionary with 'rows' and 'cols' clues.
        size: Puzzle dimensions (height, width).

    Returns:
        Dict: Boolean expressions for rows, columns, and cell constraints.
    """
    height, width = size
    boolean_expressions = {}
    cell_to_color = {}  # Maps cell positions to possible colors

    # Generate boolean expressions for rows
    boolean_expressions['rows'] = []
    for i, row_clue in enumerate(clue['rows']):
        permutations = generate_permutations(row_clue, width)
        list_expr = []
        for pattern in permutations:
            expr = []
            for j, p in enumerate(pattern):
                color = 'W' if p == 0 else p.upper()
                exp = f"R{i + 1}C{j + 1}{color}"
                expr.append(exp)
                key = f"{i + 1},{j + 1}"
                if key not in cell_to_color:
                    cell_to_color[key] = set()
                cell_to_color[key].add(color)
            list_expr.append(expr)
        boolean_expressions['rows'].append(list_expr)

    # Generate boolean expressions for columns
    boolean_expressions['cols'] = []
    for i, col_clue in enumerate(clue['cols']):
        permutations = generate_permutations(col_clue, height)
        list_expr = []
        for pattern in permutations:
            expr = []
            for j, p in enumerate(pattern):
                color = 'W' if p == 0 else p.upper()
                exp = f"R{j + 1}C{i + 1}{color}"
                expr.append(exp)
                key = f"{j + 1},{i + 1}"
                if key not in cell_to_color:
                    cell_to_color[key] = set()
                cell_to_color[key].add(color)
            list_expr.append(expr)
        boolean_expressions['cols'].append(list_expr)

    # Generate cell constraints
    boolean_expressions['cells'] = []
    for r, rval in enumerate(clue['rows'], 1):
        for c, cval in enumerate(clue['cols'], 1):
            cell_name = f"R{r}C{c}"
            cell_key = f"{r},{c}"
            cell_colors = list(cell_to_color[cell_key])
            if len(cell_colors) == 2:
                boolean_expressions['cells'].append([f"-{cell_name}{c}" for c in cell_colors])
            else:
                for i in range(len(cell_colors)):
                    for j in range(i + 1, len(cell_colors)):
                        boolean_expressions['cells'].append([f"-{cell_name}{cell_colors[i]}", f"-{cell_name}{cell_colors[j]}"])

    return boolean_expressions

def convert_dnf_to_cnf(pls: List[List[str]]) -> List[List[str]]:
    """
    Converts Disjunctive Normal Form (DNF) to Conjunctive Normal Form (CNF).

    Args:
        pls: List of DNF clauses.

    Returns:
        List[List[str]]: CNF clauses.
    """
    global _counter
    pl_map = {}
    cnf = []
    aux_cnf = []

    for pl in pls:
        aux = f"A{_counter}"
        pl_map[aux] = pl
        _counter += 1
        aux_cnf.append(aux)

    cnf.append(aux_cnf)
    for key, val in pl_map.items():
        for v in val:
            cnf.append([f"-{key}", v])

    return cnf

def convert_to_cnf(boolean_expressions: Dict) -> Tuple[Set, List[List[str]]]:
    """
    Converts boolean expressions to CNF format.

    Args:
        boolean_expressions: Dictionary of boolean expressions.

    Returns:
        Tuple[Set, List[List[str]]]: Variables and CNF clauses.
    """
    variables = set()
    clauses = []

    # Convert row patterns to CNF
    for patterns in boolean_expressions['rows']:
        if len(patterns) == 1:
            for exp in patterns[0]:
                clauses.append([exp])
                variables.add(exp)
        else:
            for clause in convert_dnf_to_cnf(patterns):
                clauses.append(clause)
                for e in clause:
                    variables.add(e if '-' not in e else e[1:])

    # Convert column patterns to CNF
    for patterns in boolean_expressions['cols']:
        if len(patterns) == 1:
            for exp in patterns[0]:
                clauses.append([exp])
                variables.add(exp)
        else:
            for clause in convert_dnf_to_cnf(patterns):
                clauses.append(clause)
                for e in clause:
                    variables.add(e if '-' not in e else e[1:])

    # Add cell constraints
    for cell in boolean_expressions['cells']:
        clauses.append(cell)

    return variables, clauses

def convert_solution_to_grid(result: List[str], mapping: Dict[int, str], size: Tuple[int, int]) -> List[List[str]]:
    """
    Converts SAT solver output to a grid representation.

    Args:
        result: SAT solver output (list of variables).
        mapping: Mapping of variable IDs to cell values.
        size: Puzzle dimensions (rows, cols).

    Returns:
        List[List[str]]: Solved grid.
    """
    if isinstance(size, int):
        rows = cols = size
    else:
        rows, cols = size

    grid = [['-' for _ in range(cols)] for _ in range(rows)]

    for ele in result:
        if int(ele) > 0:
            cell_val = mapping[int(ele)]
            if not cell_val.startswith('R'):
                continue  # Skip auxiliary variables

            if 'C' not in cell_val:
                print(f"Warning: Invalid cell format (missing 'C'): {cell_val}")
                continue

            row_part, rest = cell_val.split('C', 1)
            row = row_part[1:]  # Remove 'R' prefix
            if not rest:
                print(f"Warning: Invalid column/color: {cell_val}")
                continue

            color = rest[-1].lower()
            col_part = rest[:-1]

            try:
                x = int(row) - 1
                y = int(col_part) - 1
            except ValueError:
                print(f"Warning: Invalid row/column in {cell_val}")
                continue

            if 0 <= x < rows and 0 <= y < cols:
                grid[x][y] = color if color != 'w' else '-'
            else:
                print(f"Warning: Position ({x}, {y}) out of bounds")

    return grid