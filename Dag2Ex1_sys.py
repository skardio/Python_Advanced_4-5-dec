import sys

info = sys.version_info

print(f'You are currently using Python version {info.major}')

print(sys.path)

print('Python path: ')
for d in sys.path:
    print(d)
