from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Титульная страница
@app.route('/')
def index():
    return render_template('index.html')

# Поиск песен через iTunes API
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q') or request.form.get('q')
    results = []
    if query:
        url = f"https://itunes.apple.com/search"
        params = {
            'term': query,
            'media': 'music',
            'limit': 20
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
    return render_template('index.html', results=results, query=query)

# Рекомендации на основе жанра и других факторов
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    genre = request.form.get('genre') or 'pop'
    mood = request.form.get('mood') or 'happy'
    tempo = request.form.get('tempo') or 'medium'

    # Простейший пример рекомендаций: ищем песни по жанру и слову настроения
    url = f"https://itunes.apple.com/search"
    params = {
        'term': f"{genre} {mood}",
        'media': 'music',
        'limit': 10
    }
    response = requests.get(url, params=params)
    recs = response.json().get('results', []) if response.status_code == 200 else []

    return render_template('recommend.html', recommendations=recs)

if __name__ == '__main__':
    app.run(debug=True)
