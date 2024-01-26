import os
import openai
from flask import Flask, jsonify, request, render_template
from datetime import datetime
from threading import Thread

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

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

def generate_book_worker(genre, plot, setting, themes, plot_ideas, chapter_length):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    genre_label = genre.replace(" ", "_")
    book_dir = f"generated_books/{timestamp}_{genre_label}"
    os.makedirs(book_dir, exist_ok=True)

    # List to keep track of generated chapters
    chapters = []

    for chapter_num in range(1, chapter_length + 1):
        prompt = {
            'genre': genre,
            'plot': plot,
            'setting': setting,
            'themes': themes,
            'plot_ideas': plot_ideas,
            'chapter': chapter_num
        }
        chapter_content = generate_text_with_chatgpt(str(prompt))
        
        if chapter_content:
            chapter_filename = os.path.join(book_dir, f"chapter_{chapter_num}.txt")
            with open(chapter_filename, 'w') as file:
                file.write(chapter_content)
            print(f"Chapter {chapter_num} saved.")
            chapters.append(chapter_filename) # Add the chapter to the list
        else:
            print(f"Failed to generate chapter {chapter_num}.")
            break

    # Additional functionality could be added here, such as notifying the user
    # when book generation is complete, or handling the generated chapters.

@app.route('/generate_book', methods=['POST'])
def generate_book():
    data = request.json
    if not all(key in data for key in ['genre', 'plot', 'setting', 'themes', 'plotIdeas', 'chapterLength']):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    Thread(target=generate_book_worker, args=(
        data['genre'],
        data['plot'],
        data['setting'],
        data['themes'],
        data['plotIdeas'],
        data['chapterLength']
    )).start()

    return jsonify({"status": "success", "message": "Book generation initiated."})

if __name__ == '__main__':
    app.run(debug=True)
