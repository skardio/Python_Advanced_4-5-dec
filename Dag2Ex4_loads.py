import pickle
import json

# Pickle
filename = 'data.pickle'

with open(filename, 'rb') as f:
    data = pickle.load(f)

print(data)

# Json
filename = 'data.json'

with open(filename, 'r') as f:
    data = json.load(f)

print(data)