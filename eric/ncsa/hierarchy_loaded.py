import json
with open('function_generation_langchain/hierarchy.json', 'r') as file:
    loaded_hierarchy = json.load(file)

def count_keys(d):
    """
    Count all keys in a dictionary, including those in nested dictionaries.
    """
    if not d:
        return 0
    count = len(d)
    for key, value in d.items():
        if isinstance(value, dict):
            count += count_keys(value)
    return count

# After computing the hierarchy (or loading it from the file):
total_keys = count_keys(loaded_hierarchy)
print(total_keys)
print(loaded_hierarchy)