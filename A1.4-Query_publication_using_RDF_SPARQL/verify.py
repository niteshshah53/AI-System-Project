import sys, requests, pathlib, json

if len(sys.argv) != 3 or sys.argv[1] not in {'mini', 'big'}:
    print('Usage: verify.py mini path/to/your/example-solutions-mini.xml')
    print('Usage: verify.py big path/to/your/example-solutions-big.xml')
    sys.exit()


with open(sys.argv[2]) as fp:
    data = fp.read()

response = requests.get(f'http://jfschaefer.de:8973/verify/ss24a14/check', data=json.dumps({'solution': data, 'size': sys.argv[1]}))

print(response.text)

