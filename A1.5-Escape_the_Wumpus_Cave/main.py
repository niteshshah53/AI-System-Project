import os
import subprocess
import sys
import shlex
import glob

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(error.decode('utf-8'))
        return False
    return True

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_empty_solution(map_file, solution_dir):
    base_name = os.path.splitext(os.path.basename(map_file))[0]
    solution_file = os.path.join(solution_dir, f"{base_name}-solution.txt")
    
    with open(solution_file, 'w') as f:
        f.write("# No solution found\n")
    
    print(f"Created empty solution file for: {base_name}")

def solve_wumpus_map(map_file, domain_file, planner):
    base_name = os.path.splitext(os.path.basename(map_file))[0]
    
    # Define output directories
    problem_dir = "problem_files"
    plan_dir = "plan_files"
    solution_dir = "solution_files"
    
    # Ensure directories exist
    ensure_dir(problem_dir)
    ensure_dir(plan_dir)
    ensure_dir(solution_dir)
    
    # Define output files
    problem_file = os.path.join(problem_dir, f"{base_name}.pddl")
    plan_file = os.path.join(plan_dir, f"{base_name}.pddl.soln")
    solution_file = os.path.join(solution_dir, f"{base_name}-solution.txt")

    # Convert Windows paths to WSL paths if necessary
    map_file = map_file.replace('\\', '/')
    domain_file = domain_file.replace('\\', '/')
    problem_file = problem_file.replace('\\', '/')
    plan_file = plan_file.replace('\\', '/')
    solution_file = solution_file.replace('\\', '/')

    # Get the current directory
    current_dir = os.getcwd().replace('\\', '/')

    # Generate PDDL problem file
    if not run_command(f"python3 {current_dir}/generate_problem.py {map_file} {problem_file}"):
        return False

    # Run Fast Downward planner with a configuration that supports conditional effects
    fd_command = f"{planner} --plan-file {plan_file} {domain_file} {problem_file} --search 'lazy_greedy([add()],preferred=[add()])'"
    if not run_command(fd_command):
        return False

    # Check if a plan was actually generated
    if not os.path.exists(plan_file) or os.path.getsize(plan_file) == 0:
        print(f"No solution found for: {base_name}")
        return False

    # Execute plan and convert to required format
    if not run_command(f"python3 {current_dir}/execute_plan.py {plan_file} {solution_file}"):
        return False

    print(f"Processed map: {base_name}")
    print(f"  PDDL problem file saved to: {problem_file}")
    print(f"  Raw PDDL solution saved to: {plan_file}")
    print(f"  Formatted solution saved to: {solution_file}")
    print()

    return True

def process_map_range(maps_folder, domain_file, planner, start_index, end_index):
    map_files = sorted(glob.glob(os.path.join(maps_folder, "map*.txt")))
    total_maps = len(map_files)
    
    if start_index < 0 or end_index > total_maps or start_index >= end_index:
        print(f"Invalid range. Please specify a range between 0 and {total_maps - 1}")
        return

    maps_to_process = map_files[start_index:end_index]
    successful_maps = 0
    solution_dir = "solution_files"
    ensure_dir(solution_dir)

    for i, map_file in enumerate(maps_to_process, start_index + 1):
        print(f"Processing map {i} of {total_maps}: {os.path.basename(map_file)}")
        if solve_wumpus_map(map_file, domain_file, planner):
            successful_maps += 1
        else:
            create_empty_solution(map_file, solution_dir)
        print(f"Progress: {i - start_index}/{end_index - start_index} maps processed in current range")
        print("--------------------")

    print(f"\nProcessing complete. Successfully solved {successful_maps} out of {end_index - start_index} maps in the specified range.")
    print(f"Empty solution files created for {end_index - start_index - successful_maps} unsolved maps.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <maps_folder> <start_index> <end_index>")
        sys.exit(1)

    maps_folder = sys.argv[1]
    start_index = int(sys.argv[2])
    end_index = int(sys.argv[3])
    domain_file = "wumpus_domain.pddl"
    
    # Use the correct path for Fast Downward
    planner = "/mnt/c/Users/rider/Desktop/MsAI/Projects/AISys1/team660/downward/fast-downward.py"
    process_map_range(maps_folder, domain_file, planner, start_index, end_index)