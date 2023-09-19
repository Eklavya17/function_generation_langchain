import importlib
import inspect
import json
import pkgutil
import astropy
import numpy as np
from transformers import GPT2Tokenizer, GPT2Model
import torch
# Load GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2Model.from_pretrained('gpt2')
tokenizer.pad_token = tokenizer.eos_token
# Assuming the model is loaded globally for embedding computation
def fetch_docstrings_for_module(module_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        # Skip modules that cannot be imported
        return {}

    results = {}
    for name, obj in inspect.getmembers(module):
        if name.startswith('_'):
            continue

        full_name = f"{module_name}.{name}"
        docstring = obj.__doc__
        if docstring and isinstance(docstring, str):
            results[full_name] = docstring.strip()

    return results

def build_tree(docstrings):
    tree = {}
    for full_name, docstring in docstrings.items():
        parts = full_name.split('.')
        current_node = tree
        for part in parts:
            if part not in current_node:
                current_node[part] = {}
            current_node = current_node[part]
        current_node['__doc__'] = docstring
    return tree
from tqdm import tqdm
def compute_and_save_embeddings(docstrings, filename="astropy_embeddings.npy", batch_size=64):
    keys = list(docstrings.keys())
    values = list(docstrings.values())

    all_embeddings = []
    print(len(values)//batch_size)
    for i in tqdm(range(0, len(values), batch_size)):
        batch = values[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
        all_embeddings.append(embeddings)
    
    final_embeddings = np.vstack(all_embeddings)
    np.save(filename, final_embeddings)

    return final_embeddings

all_docstrings = {}

for _, module_name, _ in pkgutil.walk_packages(astropy.__path__, astropy.__name__ + '.'):
    docstrings = fetch_docstrings_for_module(module_name)
    all_docstrings.update(docstrings)

# Check if embeddings are already computed and saved
embeddings_filename = "astropy_embeddings.npy"
import os
compute_and_save_embeddings(all_docstrings, embeddings_filename)

# Load the embeddings for use
embeddings = np.load(embeddings_filename)

# Build the hierarchical tree from the flat docstrings (assuming you still want this for some other purpose)
doc_tree = build_tree(all_docstrings)

json_object = json.dumps(doc_tree, indent=4)

# Save to a file
with open('astropy_docstrings_tree.json', 'w') as file:
    file.write(json_object)

print("Docstrings saved to astropy_docstrings_tree.json")