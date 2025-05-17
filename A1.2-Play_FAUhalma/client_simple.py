import itertools
import json
import logging
import requests
import time
import random
from typing import List, Tuple, Dict

class Hex:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.z = -x-y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def distance(self, other: 'Hex') -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y), abs(self.z - other.z))

    def neighbors(self) -> List['Hex']:
        return [Hex(self.x+dx, self.y+dy) for dx, dy in 
                [(1,-1), (1,0), (0,1), (-1,1), (-1,0), (0,-1)]]

RHOMBUS_VALID_POSITIONS = {
    (-3,6), (-3,5), (-2,5), (-3,4), (-2,4), (-1,4),
    (-3,3), (-2,3), (-1,3), (0,3),
    (-3,2), (-2,2), (0,2), (1,2),
    (-3,1), (-2,1), (-1,1), (0,1), (1,1), (2,1),
    (-3,0), (-2,0), (-1,0), (1,0), (2,0), (3,0),
    (-2,-1), (0,-1), (1,-1), (3,-1),
    (-1,-2), (0,-2), (1,-2), (2,-2), (3,-2),
    (0,-3), (1,-3), (2,-3), (3,-3),
    (1,-4), (2,-4), (3,-4),
    (2,-5), (3,-5),
    (3,-6)
}

STAR_VALID_POSITIONS = {
    (-3,6), (-3,5), (-2,5), (-3,4), (-2,4), (-1,4),
    (-6,3), (-5,3), (-4,3), (-3,3), (-2,3), (-1,3), (0,3), (1,3), (2,3), (3,3),
    (-5,2), (-4,2), (-3,2), (-2,2), (0,2), (1,2), (2,2), (3,2),
    (-4,1), (-3,1), (-2,1), (-1,1), (0,1), (1,1), (2,1), (3,1),
    (-3,0), (-2,0), (-1,0), (1,0), (2,0), (3,0),
    (-3,-1), (-2,-1), (0,-1), (1,-1), (3,-1), (4,-1),
    (-3,-2), (-2,-2), (-1,-2), (0,-2), (1,-2), (2,-2), (3,-2), (4,-2), (5,-2),
    (-3,-3), (-2,-3), (-1,-3), (0,-3), (1,-3), (2,-3), (3,-3), (4,-3), (5,-3), (6,-3),
    (1,-4), (2,-4), (3,-4),
    (2,-5), (3,-5),
    (3,-6)
}

def is_valid_position(hex: Hex, board_type: str) -> bool:
    # Check for permanently blocked spaces
    blocked_spaces = {(-1, 2), (0, 0), (-1, -1), (2, -1)}
    if (hex.x, hex.y) in blocked_spaces:
        return False

    if board_type == 'rhombus':
        return (hex.x, hex.y) in RHOMBUS_VALID_POSITIONS
    elif board_type == 'star':
        return (hex.x, hex.y) in STAR_VALID_POSITIONS
    
    return False

def get_goal_area(player: str, board_type: str) -> List[Hex]:
    if player == 'A':
        return [Hex(-3, 6), Hex(-3, 5), Hex(-2, 5), Hex(-3, 4), Hex(-2, 4), Hex(-1, 4)]
    elif player == 'B':
        return [Hex(3, -6), Hex(3, -5), Hex(2, -5), Hex(3, -4), Hex(2, -4), Hex(1, -4)]
    else:  # player C (for 3-player game on star board)
        return [Hex(6, -3), Hex(5, -3), Hex(5, -2), Hex(4, -3), Hex(4, -2), Hex(4, -1)]

def get_possible_moves(hex: Hex, board: Dict[str, List[Hex]], board_type: str) -> List[List[Hex]]:
    occupied = set(peg for pegs in board.values() for peg in pegs)
    moves = []
    
    for neighbor in hex.neighbors():
        if is_valid_position(neighbor, board_type) and neighbor not in occupied:
            moves.append([hex, neighbor])
    
    def hop(start: Hex, current: Hex, path: List[Hex]):
        for next_hex in current.neighbors():
            if next_hex in occupied:
                jump = Hex(next_hex.x + (next_hex.x - current.x), 
                           next_hex.y + (next_hex.y - current.y))
                if is_valid_position(jump, board_type) and jump not in occupied and jump not in path:
                    new_path = path + [jump]
                    moves.append([start] + new_path)
                    hop(start, jump, new_path)

    hop(hex, hex, [])
    return moves

def manhattan_distance(hex1: Hex, hex2: Hex) -> int:
    return (abs(hex1.x - hex2.x) + abs(hex1.y - hex2.y) + abs(hex1.z - hex2.z)) // 2

def evaluate_position(position: Dict[str, List[Hex]], player: str, board_type: str) -> float:
    goal_area = get_goal_area(player, board_type)
    opponent = 'B' if player == 'A' else 'A'
    opponent_goal_area = get_goal_area(opponent, board_type)
    
    player_score = 0
    opponent_score = 0
    
    for peg in position[player]:
        if peg in goal_area:
            player_score += 10
        else:
            player_score += 10 - min(peg.distance(goal) for goal in goal_area)
    
    for peg in position[opponent]:
        if peg in opponent_goal_area:
            opponent_score += 10
        else:
            opponent_score += 10 - min(peg.distance(goal) for goal in opponent_goal_area)
    
    # Add bonus for pieces that can hop over each other
    player_score += sum(2 for peg in position[player] if any(other.distance(peg) == 1 for other in position[player] if other != peg))
    opponent_score += sum(2 for peg in position[opponent] if any(other.distance(peg) == 1 for other in position[opponent] if other != peg))
    
    # Penalize isolated pieces
    player_score -= sum(5 for peg in position[player] if all(other.distance(peg) > 2 for other in position[player] if other != peg))
    opponent_score -= sum(5 for peg in position[opponent] if all(other.distance(peg) > 2 for other in position[opponent] if other != peg))
    
    return player_score - opponent_score

def minimax(position: Dict[str, List[Hex]], depth: int, alpha: float, beta: float, maximizing_player: bool, 
            player: str, players: List[str], board_type: str, time_limit: float, start_time: float) -> Tuple[float, List[Hex]]:
    if depth == 0 or time.time() - start_time > time_limit:
        return evaluate_position(position, player, board_type), None

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for peg in position[player]:
            for move in get_possible_moves(peg, position, board_type):
                new_position = {p: [hex for hex in pegs] for p, pegs in position.items()}
                new_position[player].remove(move[0])
                new_position[player].append(move[-1])
                
                eval, _ = minimax(new_position, depth - 1, alpha, beta, False, player, players, board_type, time_limit, start_time)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        next_player = players[(players.index(player) + 1) % len(players)]
        for peg in position[next_player]:
            for move in get_possible_moves(peg, position, board_type):
                new_position = {p: [hex for hex in pegs] for p, pegs in position.items()}
                new_position[next_player].remove(move[0])
                new_position[next_player].append(move[-1])
                
                eval, _ = minimax(new_position, depth - 1, alpha, beta, True, player, players, board_type, time_limit, start_time)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval, best_move

def agent_function(request_dict: Dict) -> List[List[int]]:
    position = {player: [Hex(x, y) for x, y in pegs] for player, pegs in request_dict.items()}
    player = 'A'  # We are always player A
    # board_type = request_dict.get('board_type', 'rhombus')  # Default to star if not specified
    players = list(position.keys())
    num_players = len(players)
    
    #function to choose board based on the configuration file
    import os
    import sys
    def choose_board(file_name):
        if file_name == 'ss24.1.2.1.json':
            return 'rhombus'
        else:
            return 'star'
    full_path = sys.argv[1]
    file_name = os.path.basename(full_path)
    board_type = choose_board(file_name)

    max_depth = 3 if board_type == 'rhombus' else 4
    time_limit = 1.5 if board_type == 'rhombus' else 2.0
    
    start_time = time.time()
    best_eval = float('-inf')
    best_move = None
    
    for depth in range(1, max_depth + 1):
        eval, move = minimax(position, depth, float('-inf'), float('inf'), True, player, players, board_type, time_limit, start_time)
        # print(f"Depth {depth}: Eval = {eval}, Move = {move}")
        if time.time() - start_time > time_limit:
            # print("Time limit reached")
            break
        if eval > best_eval:
            best_eval = eval
            best_move = move
    
    if best_move:
        if all(is_valid_position(hex, board_type) for hex in best_move):
            # print(f"Chosen move: {best_move}")
            return [[hex.x, hex.y] for hex in best_move]
        else:
            # print(f"Warning: Invalid move detected: {best_move}")
            return None
    
    # print("No valid move found")
    return None

def run(config_file, action_function, single_request=False):
    logger = logging.getLogger(__name__)

    with open(config_file, 'r') as fp:
        config = json.load(fp)
    
    logger.info(f'Running agent {config["agent"]} on environment {config["env"]}')
    logger.info(f'Hint: You can see how your agent performs at {config["url"]}agent/{config["env"]}/{config["agent"]}')

    actions = []
    for request_number in itertools.count():
        logger.debug(f'Iteration {request_number} (sending {len(actions)} actions)')
        # send request
        response = requests.put(f'{config["url"]}/act/{config["env"]}', json={
            'agent': config['agent'],
            'pwd': config['pwd'],
            'actions': actions,
            'single_request': single_request,
        })
        if response.status_code == 200:
            response_json = response.json()
            for error in response_json['errors']:
                logger.error(f'Error message from server: {error}')
            for message in response_json['messages']:
                logger.info(f'Message from server: {message}')

            action_requests = response_json['action-requests']
            if not action_requests:
                logger.info('The server has no new action requests - waiting for 1 second.')
                time.sleep(1)  # wait a moment to avoid overloading the server and then try again
            # get actions for next request
            actions = []
            for action_request in action_requests:
                actions.append({'run': action_request['run'], 'action': action_function(action_request['percept'])})
        elif response.status_code == 503:
            logger.warning('Server is busy - retrying in 3 seconds')
            time.sleep(3)  # server is busy - wait a moment and then try again
        else:
            # other errors (e.g. authentication problems) do not benefit from a retry
            logger.error(f'Status code {response.status_code}. Stopping.')
            break

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    run(sys.argv[1], agent_function, single_request=False)