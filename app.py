from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q') or request.form.get('q')
    results = []
    if query:
        url = "https://itunes.apple.com/search"
        params = {'term': query, 'media': 'music', 'limit': 20}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
    return render_template('index.html', results=results, query=query)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    # Получаем все параметры анкеты
    genre = request.form.get('genre') or 'pop'
    country = request.form.get('country') or 'USA'
    mood = request.form.get('mood') or ''
    activity = request.form.get('activity') or ''
    people = request.form.get('people') or ''
    time_of_day = request.form.get('time_of_day') or ''

    # Основной поисковый запрос — жанр + страна
    search_terms = f"{genre} {country}"

    # Добавляем остальные параметры вторично
    if mood:
        search_terms += f" {mood}"
    if activity:
        search_terms += f" {activity}"
    if people:
        search_terms += f" {people}"
    if time_of_day:
        search_terms += f" {time_of_day}"

    url = "https://itunes.apple.com/search"
    params = {'term': search_terms, 'media': 'music', 'limit': 15}
    response = requests.get(url, params=params)

    recommendations = []
    if response.status_code == 200:
        data = response.json()
        recommendations = data.get('results', [])

    return render_template('recommend.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
