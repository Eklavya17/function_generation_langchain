import json

with open('../astropy_docstrings.json', 'r') as file:
    data = json.load(file)
    
groups = {key.split('.')[0] + '.' + key.split('.')[1] for key in data.keys()}
num_groups = len(groups)

print(f"Number of unique groups: {num_groups}")
print(groups)

def get_subgroups(prefix, data):
    print(prefix)
    """Get subgroups for a given prefix in the data."""
    level = len(prefix.split('.')) if prefix else 0
    
    if prefix:
        potential_subgroups = {key.split('.')[level] for key in data.keys() if key.startswith(prefix + '.')}
    else:
        potential_subgroups = {key.split('.')[0] for key in data.keys()}
    
    valid_subgroups = {}
    for subgroup in potential_subgroups:
        full_group = prefix + '.' + subgroup if prefix else subgroup
        entries = [key for key in data if key.startswith(full_group + '.')]
        
        if entries: 
            deeper_subgroups = get_subgroups(full_group, data)
            if deeper_subgroups:
                valid_subgroups[subgroup] = deeper_subgroups
            else:
                valid_subgroups.update({entry: None for entry in entries})

    return valid_subgroups if valid_subgroups else None

hierarchy = get_subgroups('', data)
print([key for key in hierarchy.keys() if hierarchy[key] != None])

with open('hierarchy.json', 'w') as file:
    json.dump(hierarchy, file)
