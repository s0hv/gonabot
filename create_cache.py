import pokebase as pb
from collections import OrderedDict
import json

g = pb.generation(1)
l = []
data = OrderedDict()

for p in g.pokemon_species:
    p.id = int(p.id)
    l.append(p)
    
l = sorted(l, key=lambda x: x.id)

for p in l: 
    data[p.id] = {'name': p.name, 'url': p.url}
    
with open('pokemon.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
