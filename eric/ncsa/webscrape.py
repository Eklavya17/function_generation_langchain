import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import openai
import json
BASE_URL = 'https://docs.astropy.org/en/stable/'

class Node:
    def __init__(self, url):
        self.url = url
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def count_links(self):
        count = 1
        for child in self.children:
            count += child.count_links()
        return count

def get_links_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a', href=True) 
                 if urljoin(BASE_URL, a['href']).startswith(BASE_URL)]
        return set(links)
    
    except requests.RequestException:
        return []

def build_tree(root_url, depth_limit=3, depth=0, visited=None):
    if depth > depth_limit:
        return None

    if visited is None:
        visited = set()

    if root_url in visited:
        return None

    visited.add(root_url)

    root = Node(root_url)
    child_links = get_links_from_url(root_url)

    for link in child_links:
        child_node = build_tree(link, depth_limit, depth+1, visited)
        if child_node:
            root.add_child(child_node)
    
    return root

def chunk_text(text, length=2000, overlap=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), length-overlap):
        chunks.append(' '.join(words[i:i+length]))
    return chunks

with open('/Users/eric/Desktop/more/ncsa/api_key.txt', 'r') as f:
    openai.api_key = f.read().strip()

def extract_functions_from_chunk(chunk):
    try:
        prompt = (f"Given the content below, extract and list all identifiable "
                  f"programming constructs such as functions, methods, classes, modules, "
                  f"and constants. Please provide the output in a structured JSONL format.\n\n{chunk}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500 
        )
        
        response_text = response.choices[0].message.content.strip()
        jsonl_lines = response_text.split("\n")
        valid_jsonl_objects = []
        for line in jsonl_lines:
            try:
                json_obj = json.loads(line)
                valid_jsonl_objects.append(json_obj)
            except json.JSONDecodeError:
                pass

        return valid_jsonl_objects
    
    except openai.error.OpenAIError:
        return []

tree = build_tree(BASE_URL)

def extract_links(node):
    if not node:
        return []
    links = [node.url]
    for child in node.children:
        links.extend(extract_links(child))
    return links

links = extract_links(tree)

data = []
count=0
for link in links:
    print(count)
    count+=1
    try:
        response = requests.get(link)
        if response.status_code == 404:
            continue
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        chunks = chunk_text(text)
        
        for chunk in chunks:
            descriptions = extract_functions_from_chunk(chunk)
            if descriptions:
                data.append({
                    "link": link,
                    "chunk": chunk,
                    "descriptions": descriptions
                })
    except requests.RequestException:
        pass

with open('link_descriptions_better.txt', 'w') as file:
    for item in data:
        file.write(f"URL: {item['link']}\n")
        file.write(f"Chunk: {item['chunk']}\n")
        file.write("Descriptions:\n")
        for desc in item['descriptions']:
            file.write(f"- {desc}\n")
        file.write("\n")