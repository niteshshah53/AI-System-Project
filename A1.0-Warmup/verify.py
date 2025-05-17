import sys, requests, pathlib, json

if len(sys.argv) != 2:
    print('Usage: verify.py path/to/your/example-solutions')
    sys.exit()

example_solutions_dir = pathlib.Path(sys.argv[1])

data = {}

for letter in 'abcdef':
    for number in range(20):
        path = example_solutions_dir / f'solution_{letter}_{number:02d}.txt'
        if path.is_file():
            with open(path) as fp:
                data[path.name] = fp.read()

response = requests.get(f'http://jfschaefer.de:8973/verify/ss24a10a/cavecleaning', data=json.dumps(data))

print(response.text)

print()
print('WARNING: YOU MAY GET A DIFFERENT NUMBER OF POINTS')
print('The script only checks your solutions for the example problems, '
        'but your grade will depend on the actual solutions. '
        'Furthermore, there is a chance that the script contains mistakes. '
        'The script is only intended to help you with debugging.')

