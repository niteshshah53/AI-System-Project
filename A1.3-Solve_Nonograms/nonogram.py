import sys, requests, pathlib, json

if len(sys.argv) != 4:
    print('Usage: nonogram.py [check|visualize] path/to/nonogram.clues path/to/nonogram.solution')
    sys.exit()


def read(file):
    with open(file) as fp:
        return fp.read()

goal = sys.argv[1]
assert goal in {'check', 'visualize'}
clues = read(sys.argv[2])
clue_lines = clues.splitlines()
solution_path = pathlib.Path(sys.argv[3])

data = {
    'goal': goal,
    'clues': clues,
    # solution file format is different on the server
    'solution': 'anonymous problem\n' + clue_lines[0].split()[0] + '\n' + clue_lines[1] + '\n' + read(solution_path).replace('-', '0').replace('a', '1').replace('b', '2').replace('c', '3'),
}

response = requests.get(f'http://jfschaefer.de:8973/verify/ss23a31a/nonograms', data=json.dumps(data))

if goal == 'check':
    print(response.text)
else:
    path = solution_path.parent / (solution_path.name + '.html')
    print(f'Creating {path}')
    with open(path, 'w') as fp:
        fp.write(f'<html><body><div style="width: 10cm;">{response.text}</div></body></html>')
