from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def find_most_similar(input_string, sentences):
    input_embedding = model.encode(input_string, convert_to_tensor=True)
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    
    similarities = [util.pytorch_cos_sim(input_embedding, sentence_embedding) for sentence_embedding in sentence_embeddings]
    
    most_similar_index = np.argmax(similarities)
    
    return sentences[most_similar_index]

descriptions = []
urls = []

with open('link_descriptions_better.txt', 'r') as file:
    lines = file.readlines()
    current_url = None
    for line in lines:
        line = line.strip()
        if line.startswith("URL:"):
            current_url = line[len("URL: "):].strip()
        elif line.startswith("- "):  
            descriptions.append(line[2:].strip()) 
            urls.append(current_url)

user_query = input("Enter your query: ")

best_match_description = find_most_similar(user_query, descriptions)

best_match_url = urls[descriptions.index(best_match_description)]

print(f"Best match page: {best_match_url}\nDescription: {best_match_description}")
