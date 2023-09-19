import openai

with open('./eric/ncsa/api_key.txt', 'r') as f:
    openai.api_key = f.read().strip()

def transform_query_to_docstring(query):
    prompt = (f"Imagine you are writing a docstring for a hypothetical function or feature in the `astropy` package related to '{query}'. "
              f"Generate a new and relevant docstring that might describe such a function or feature:\n\n")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5  # Slightly increased temperature for more diverse responses
        )

        transformed_query = response.choices[0].message.content.strip()

        return transformed_query

    except openai.error.OpenAIError:
        return query  # return original query in case of error

# Example use:

user_query = input("Enter your query: ")
transformed_docstring = transform_query_to_docstring(user_query)
print(f"Transformed Query (Docstring format): {transformed_docstring}")
