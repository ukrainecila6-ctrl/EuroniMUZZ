from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET','POST'])
def search():
    query = request.args.get('q') or request.form.get('q')
    results = []
    if query:
        url = "https://itunes.apple.com/search"
        params = {'term': query, 'media': 'music', 'limit': 20}
        r = requests.get(url, params=params)
        if r.status_code == 200:
            results = r.json().get('results', [])
    return render_template('index.html', results=results, query=query)

@app.route('/recommend', methods=['GET','POST'])
def recommend():
    genre = request.form.get('genre') or 'pop'
    mood = request.form.get('mood') or ''
    activity = request.form.get('activity') or ''
    country = request.form.get('country') or ''
    time_of_day = request.form.get('time_of_day') or ''

    # Первый запрос — по жанру как ключевому слову
    base_query = genre
    url = "https://itunes.apple.com/search"
    params = {'term': base_query, 'media': 'music', 'limit': 20}
    resp = requests.get(url, params=params)
    recs = []
    if resp.status_code == 200:
        recs = resp.json().get('results', [])

    # Извлекаем жанры / теги из первых результатов
    tags = set()
    for track in recs:
        # Например, primaryGenreName
        g = track.get('primaryGenreName')
        if g:
            tags.add(g)
        # Можно также анализировать часть trackName, artistName как ключевые слова
        name = track.get('trackName')
        if name:
            for w in name.split():
                tags.add(w)

    # Используем лучшие теги + остальные параметры для уточнения
    # Формируем итоговый запрос
    extra = []
    if mood:
        extra.append(mood)
    if activity:
        extra.append(activity)
    if country:
        extra.append(country)
    if time_of_day:
        extra.append(time_of_day)

    # Собираем запросы по тегам + доп. условия
    # Например, первые 3 наиболее частых тега
    selected_tags = list(tags)[:3]
    query_parts = selected_tags + extra

    final_query = " ".join(query_parts)

    params2 = {'term': final_query, 'media': 'music', 'limit': 15}
    resp2 = requests.get(url, params=params2)
    final_recs = []
    if resp2.status_code == 200:
        final_recs = resp2.json().get('results', [])

    # Если всё ещё мало, fallback к простому жанру
    if len(final_recs) < 5:
        params2['term'] = genre
        resp3 = requests.get(url, params=params2)
        if resp3.status_code == 200:
            final_recs += resp3.json().get('results', [])

    # Убедимся, что нет дубликатов
    seen = set()
    unique_recs = []
    for t in final_recs:
        tid = t.get('trackId')
        if tid and tid not in seen:
            seen.add(tid)
            unique_recs.append(t)

    return render_template('recommend.html', recommendations=unique_recs)

if __name__ == '__main__':
    app.run(debug=True)
