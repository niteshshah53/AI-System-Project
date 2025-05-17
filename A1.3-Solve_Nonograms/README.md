# Nonogram Solver
This project solves Nonogram puzzles (rectangular and traingular) using SAT solvers and propositional logic.

## Prerequisites
- Windows 10/11 with WSL or Linux/Unix system
- Python 3.8+
- MiniSat SAT solver

## Repository Structure
nonogram-solver/<br>
│<br>
├── clues/                  # Contains puzzle input files (.clues)<br>
│<br>
├── solution/               # Stores generated solution files<br>
│<br>
├── sat/                    # Stores SAT problem files<br>
│<br>
├── main.py                 # Main script (parsing, SAT setup, and solution conversion)<br>
├── boolean_converter.py    # Converts clues to boolean logic and CNF<br>
├── pattern_generator.py    # Generates valid clue permutations<br>
├── nonogram.py             # Script for checking and visualizing your solution<br>
│<br>
└── README.md               # This documentation<br>

## Setup

1. **Install MiniSat (Linux/WSL):**
  
     ```
     sudo apt update && sudo apt install minisat -y
     ```
2. **Clone the Repository:**
  
     ```
     git clone [your-repo-url]
     ```
3. **Run the Solver:**
  
     ```
     python3 main.py clues/[your_puzzle].clues
     ```

## How it works?

1. Input Parsing: Reads .clues files (rectangular/hexagonal formats).

2. Pattern Generation: Generates valid permutations for rows/columns (pattern_generator.py).

3. CNF Conversion: Translates puzzle constraints into Conjunctive Normal Form (boolean_converter.py).

4. SAT Solving: Uses MiniSat to solve the CNF problem.

5. Solution Mapping: Converts SAT output to a human-readable grid.

## Key Files

- `main.py`: Orchestrates parsing, SAT solving, and output.
- `boolean_converter.py`: Handles logic-to-CNF conversion.
- `pattern_generator.py`: Implements permutation generation and validation.
- `nonogram.py`: Handles checking and visualizing your solution

## Limitations 

- Puzzle size limited by SAT solver performance.
- Performance may degrade or sometimes your system may crash for very large puzzles