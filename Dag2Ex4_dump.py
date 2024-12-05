import pickle
import json

data = {'name':'Peter', 'woonplaats':'Lhee', 'leeftijd':65}


# Pickle
filename = 'data.pickle'

with open(filename, 'wb') as f:
    pickle.dump(data, f)

# JSON
filename = 'data.json'

with open(filename, 'w') as f:
    json.dump(data, f)