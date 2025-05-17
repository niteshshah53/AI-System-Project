import sys

def parse_plan(plan_file):
    with open(plan_file, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith(';')]

def convert_action(action):
    parts = action.split()
    action_type = parts[0][1:]  # Remove the opening parenthesis
    
    if action_type == 'walk':
        direction = parts[4][:-1]  # Remove the closing parenthesis
        return f"walk {direction}"
    elif action_type == 'walk-off-map':
        direction = parts[3][:-1]  # Remove the closing parenthesis
        return f"walk {direction}"
    elif action_type == 'push':
        direction = parts[5][:-1]  # Remove the closing parenthesis
        return f"push {direction}"
    elif action_type == 'shoot':
        direction = parts[4][:-1]  # Remove the closing parenthesis
        return f"shoot {direction}"
    elif action_type == 'unlock':
        direction = parts[4][:-1]  # Remove the closing parenthesis
        return f"unlock {direction}"
    elif action_type == 'jump':
        direction = parts[5][:-1]  # Remove the closing parenthesis
        return f"jump {direction}"
    elif action_type == 'jump-off-map':
        direction = parts[4][:-1]  # Remove the closing parenthesis
        return f"jump {direction}"
    else:
        return action

def execute_plan(plan_file, output_file):
    plan = parse_plan(plan_file)
    converted_plan = [convert_action(action) for action in plan]
    
    with open(output_file, 'w') as f:
        for action in converted_plan:
            f.write(f"{action}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python execute_plan.py <plan_file> <output_file>")
        sys.exit(1)
    
    plan_file = sys.argv[1]
    output_file = sys.argv[2]
    execute_plan(plan_file, output_file)