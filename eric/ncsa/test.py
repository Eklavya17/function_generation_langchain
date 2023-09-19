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
embeddings = np.load('../astropy_embeddings.npy')

with open('./eric/ncsa/api_key.txt', 'r') as f:
    openai.api_key = f.read().strip()

def transform_query_to_docstring_format(query):
    try:
        prompt = f"Translate the user's query '{query}' into a simple docstring or phrase that might describe a relevant function."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,  # Limit the response length
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except openai.error.OpenAIError:
        return query  # Return the original query as a fallback
    


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

def search_data(data_dict, query):
    keys = list(data_dict.keys())
    values = list(data_dict.values())
    _, best_match = find_most_similar(query, values, embeddings)
    best_match_key = keys[values.index(best_match)]
    return best_match, best_match_key

# Load the hierarchical docstrings from the generated JSON file
with open('../astropy_docstrings.json', 'r') as file:
    data = json.load(file)

user_query = input("Enter your query: ")

# Transform the user's query into docstring format using GPT

start_time = time.time()  # Start the timer
best_match_description, best_match_url = search_data(data, user_query)  # Use transformed query
end_time = time.time()  # End the timer

runtime = end_time - start_time

print(f"Search completed in {runtime:.4f} seconds.")
print(f"Best match function: {best_match_url}\nDocstring: {best_match_description}")
