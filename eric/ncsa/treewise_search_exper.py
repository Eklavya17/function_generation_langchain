
import openai
import numpy as np
from sentence_transformers import SentenceTransformer, util
from joblib import Parallel, delayed
import json
import time
import os

# Configuration
os.environ["TOKENIZERS_PARALLELISM"] = "false"
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
def compute_similarity(input_embedding, sentence_embedding):
    return float(util.pytorch_cos_sim(input_embedding, sentence_embedding))

def find_most_similar(input_string, sentences, precomputed_embeddings):
    input_embedding = model.encode(input_string[:256], convert_to_tensor=True)
    similarities = Parallel(n_jobs=-1)(
        delayed(compute_similarity)(input_embedding, sentence_embedding) 
        for sentence_embedding in precomputed_embeddings
    )

    most_similar_index = np.argmax(similarities)
    return similarities[most_similar_index], sentences[most_similar_index]


def recursive_search(data_dict, query, path=[]):
    # If the current data is not a dictionary, return the current path
    print(path)
    if not isinstance(data_dict, dict):
        return path

    # Get only dictionary keys since we can't search None values with the embeddings
    keys = [key for key, value in data_dict.items()]

    # If no more dictionary keys, return the current path
    if not keys:
        return path

    # Use find_most_similar to get the most similar key
    print("choices:")
    print(keys)
    _, best_match_key = find_most_similar(query, keys, [model.encode(key, convert_to_tensor=True) for key in keys])

    # Recursively search within the best match key's sub-dictionary
    return recursive_search(data_dict[best_match_key], query, path + [best_match_key])
import json
with open('./hierarchy.json', 'r') as file:
    data = json.load(file)
def search_data(data_dict, query):
    path = recursive_search(data_dict, query)
    return path
