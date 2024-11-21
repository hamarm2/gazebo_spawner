import json

with open("waypoints.json", "r") as file:
    tmp = json.load(file)
    
print(tmp["waypoints"])
