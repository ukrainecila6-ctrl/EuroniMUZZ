from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

# ====== iTunes API helper ======
def search_itunes(term, limit=25, country="us"):
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "media": "music",
        "limit": limit,
        "country": country
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for item in data.get("results", []):
        results.append({
            "trackName": item.get("trackName"),
            "artistName": item.get("artistName"),
            "previewUrl": item.get("previewUrl"),
            "artwork": item.get("artworkUrl100", "").replace("100x100", "300x300"),
            "collectionName": item.get("collectionName", "")
        })
    return results

# ====== Главная ======
@app.route("/")
def home():
    return render_template("home.html")

# ====== Поиск ======
@app.route("/search", methods=["GET", "POST"])
def index():
    songs = []
    query = ""
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            songs = search_itunes(query, limit=30)
    return render_template("index.html", songs=songs, query=query)

# ====== Рекомендации ======
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    recommendations = []
    query_params = {}
    if request.method == "POST":
        mood = request.form.get("mood")
        genre = request.form.get("genre")
        activity = request.form.get("activity")
        time = request.form.get("time")
        region = request.form.get("region")
        purpose = request.form.get("purpose")

        query_params = {"mood": mood, "genre": genre, "activity": activity,
                        "time": time, "region": region, "purpose": purpose}

        recommendations = generate_recommendations(mood, genre, activity, time, region, purpose)

    return render_template("recommend.html", recommendations=recommendations, query_params=query_params)

def generate_recommendations(mood, genre, activity, time, region, purpose):
    mood_tags = {
        "happy": ["uplifting", "positive", "feel good", "summer vibes"],
        "sad": ["melancholic", "slow", "emotional", "soft piano"],
        "romantic": ["love songs", "slow dance", "ballads", "heartfelt"],
        "calm": ["chill", "relaxing", "ambient", "lofi"],
        "energetic": ["energetic", "high tempo", "dance", "upbeat"],
        "angry": ["hard rock", "metal", "intense", "aggressive"]
    }
    activity_tags = {
        "relaxing": ["chill", "acoustic", "instrumental"],
        "studying": ["focus", "study beats", "ambient"],
        "driving": ["roadtrip", "travel", "car songs"],
        "training": ["gym", "workout", "motivation"],
        "cleaning": ["house mix", "dance pop", "good mood"],
        "party": ["party", "club", "dance hits"]
    }
    time_tags = {
        "morning": ["morning energy", "wake up songs"],
        "day": ["daytime hits", "workday pop"],
        "evening": ["evening chill", "relax vibes"],
        "night": ["night music", "late night mix"]
    }
    purpose_tags = {
        "alone": ["deep", "personal", "solo listening"],
        "friends": ["fun", "sing along", "social"],
        "work": ["focus", "instrumental", "background"],
        "chill": ["lofi", "smooth", "calm"]
    }
    country_map = {
        "us": "us", "ru": "ru", "gb": "gb", "de": "de",
        "fr": "fr", "jp": "jp", "kr": "kr", "latino": "mx"
    }
    country = country_map.get(region, "us")

    tags = []
    tags += random.sample(mood_tags.get(mood, []), min(2, len(mood_tags.get(mood, []))))
    tags += random.sample(activity_tags.get(activity, []), min(2, len(activity_tags.get(activity, []))))
    tags += random.sample(time_tags.get(time, []), min(1, len(time_tags.get(time, []))))
    tags += random.sample(purpose_tags.get(purpose, []), min(1, len(purpose_tags.get(purpose, []))))

    core_query = f"{genre} {' '.join(tags)}"
    search_query = core_query.strip()

    recommendations = search_itunes(search_query, limit=50, country=country)

    if len(recommendations) < 15:
        backup_terms = [
            f"top {genre} songs",
            f"{mood} {genre} playlist",
            f"best {genre} hits",
            f"{genre} {purpose} mix"
        ]
        for term in backup_terms:
            extra = search_itunes(term, limit=20, country=country)
            recommendations.extend(extra)

    seen = set()
    unique = []
    for song in recommendations:
        if song["trackName"] not in seen:
            seen.add(song["trackName"])
            unique.append(song)
    return unique[:60]

if __name__ == "__main__":
    app.run(debug=True)
