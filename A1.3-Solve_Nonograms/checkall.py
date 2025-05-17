import requests 
import sys
import pathlib
import json

if len(sys.argv) != 3:
    print('Usage: checkall.py <solution_dir> <clue_dir>')
    sys.exit(1)

clues_dir = pathlib.Path(sys.argv[1])
solutions_dir = pathlib.Path(sys.argv[2])

correct = 0
wrong = 0

for solution_path in solutions_dir.glob('*.solution'):

    clues = (clues_dir / solution_path.name.replace('solution', 'clues')).read_text()
    clue_lines = clues.splitlines()
    solution = solution_path.read_text()

    # solution file format is different on the server
    for i, c in enumerate('-abcdefghi'):
        solution = solution.replace(c, str(i))

    data = {
        'goal': 'check',
        'clues': clues,
        'solution': 'anonymous problem\n' + clue_lines[0].split()[0] + '\n' + clue_lines[1] + '\n' + solution,
    }

    response = requests.get(f'http://jfschaefer.de:8973/verify/ws2425a31a/nonograms', data=json.dumps(data))
    print(solution_path.name)
    print('   ', response.text)
    if response.text == 'Correct':
        correct += 1
    else:
        wrong += 1

print()
print(f'Correct: {correct}, Wrong: {wrong}')
