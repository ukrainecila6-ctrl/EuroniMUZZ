from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def search_itunes(query, limit=25):
    url = "https://itunes.apple.com/search"
    params = {"term": query, "media": "music", "limit": limit}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json().get("results", [])
    return []

def get_itunes_top_songs(region="us", limit=20):
    url = f"https://rss.itunes.apple.com/api/v1/{region}/itunes-music/top-songs/all/{limit}/explicit.json"
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        results = data.get("feed", {}).get("results", [])
        filtered = []
        for song in results:
            if song.get("name") and song.get("artistName") and song.get("artworkUrl100"):
                preview = search_itunes(f"{song['name']} {song['artistName']}", limit=1)
                if preview and preview[0].get("previewUrl"):
                    song['previewUrl'] = preview[0]['previewUrl']
                    filtered.append(song)
        return filtered
    return []

@app.route('/')
def home():
    top_songs = get_itunes_top_songs(region="us", limit=15)
    return render_template('home.html', top_songs=top_songs)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q') or request.form.get('q')
    results = []
    if query:
        results = search_itunes(query)
    return render_template('index.html', results=results, query=query)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    recommendations = []
    if request.method == 'POST':
        genre = request.form.get('genre')
        mood = request.form.get('mood')
        activity = request.form.get('activity')
        country = request.form.get('country')

        queries = [
            f"{genre} {mood} {activity} {country}",
            f"{genre} {mood} {activity}",
            f"{genre} {mood}",
            f"{genre}"
        ]
        seen = set()
        for q in queries:
            results = search_itunes(q, limit=10)
            for r in results:
                if r.get("previewUrl") and r['trackId'] not in seen:
                    recommendations.append(r)
                    seen.add(r['trackId'])
        recommendations = recommendations[:20]
    return render_template('recommend.html', recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
