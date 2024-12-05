import os

dirname = os.getcwd() #'/users/peter'

listing = os.listdir(dirname)

print(listing)

for entry in sorted(listing, key = lambda e: e.lower()):
    if not entry.startswith('.'):
        print(entry)