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
    genre = request.form.get('genre') or 'pop'
    mood = request.form.get('mood') or 'happy'
    activity = request.form.get('activity') or 'rest'
    country = request.form.get('country') or 'USA'
    people = request.form.get('people') or 'one'
    time_of_day = request.form.get('time_of_day') or 'day'

    search_terms = f"{genre} {mood} {activity}"
    url = "https://itunes.apple.com/search"
    params = {'term': search_terms, 'media': 'music', 'limit': 10}
    response = requests.get(url, params=params)
    recs = response.json().get('results', []) if response.status_code == 200 else []

    return render_template('recommend.html', recommendations=recs)

if __name__ == '__main__':
    app.run(debug=True)
