import os
import openai
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Load your OpenAI API key from an environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define a function to interact with the OpenAI API
def generate_text_with_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error: {e}")
        return None

# Route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/generate_book', methods=['POST'])
def generate_book():
    data = request.json
    genre = data['genre']
    prompt = f"Create a book outline for a {genre} story with the following details: Plot: {data['plot']}, Setting: {data['setting']}, Themes: {data['themes']}, Plot Ideas: {data['plotIdeas']}."

    # Call the function to generate text with ChatGPT
    book_outline = generate_text_with_chatgpt(prompt)

    if book_outline:
        # Define the directory for saving outlines
        outlines_dir = 'book_outlines'
        os.makedirs(outlines_dir, exist_ok=True)
        
        # Save the book outline to a file with a timestamp and genre label
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        genre_label = genre.replace(" ", "_")
        filename = f"{outlines_dir}/{timestamp}_{genre_label}_outline.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(book_outline)
        
        return jsonify({"status": "success", "message": "Book outline generated and saved successfully.", "outline": book_outline})
    else:
        return jsonify({"status": "error", "message": "Failed to generate book outline."})

if __name__ == '__main__':
    app.run(debug=True)
