import sys, requests, pathlib, json

if len(sys.argv) != 3:
    print('Usage: verify.py path/to/maps path/to/solutions')
    sys.exit()

maps_dir = pathlib.Path(sys.argv[1])
solutions_dir = pathlib.Path(sys.argv[2])

data = {}

for i in range(80):
    map_file = maps_dir / f'map{i:03d}.txt'
    solution_file = solutions_dir / f'map{i:03d}-solution.txt'
    data[map_file.name] = map_file.read_text()
    if solution_file.is_file():
        data[solution_file.name] = solution_file.read_text()
    else:
        print(f'{solution_file} does not exist')



response = requests.get(f'http://jfschaefer.de:8973/verify/ws2324a15/wumpusplan', data=json.dumps(data))

print(response.text)

print()
print('WARNING: THERE IS NO GUARANTEE THAT THE OUTPUT OF THE SCRIPT IS CORRECT. '
        'IT IS THEREFORE POSSIBLE THAT YOU WILL GET A DIFFERENT NUMBER OF POINTS.')

