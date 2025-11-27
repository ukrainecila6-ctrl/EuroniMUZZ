from flask import Flask, render_template, request, redirect, url_for, make_response, session, flash
import requests
import json
import time
from collections import Counter

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-random-key"  # change for production

# --- In-memory users (demo). For production use real DB.
USERS = {}  # username -> {password: "...", display: "..."}

# Config
DEFAULT_REGION = "us"
RECOMMEND_LIMIT = 20

# --------------------------
# iTunes helpers
# --------------------------
def search_itunes(term, limit=25):
    """Search iTunes and return list of results (may be empty)."""
    if not term or not term.strip():
        return []
    try:
        resp = requests.get("https://itunes.apple.com/search",
                            params={"term": term, "media": "music", "limit": limit},
                            timeout=6)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception as e:
        print("search_itunes error:", e)
    return []

def enrich_preview(result):
    """Normalize fields for templates."""
    return {
        "trackId": result.get("trackId"),
        "trackName": result.get("trackName") or result.get("collectionName") or result.get("name"),
        "artistName": result.get("artistName") or result.get("artist"),
        "artworkUrl100": result.get("artworkUrl100") or result.get("artworkUrl60") or "",
        "previewUrl": result.get("previewUrl")
    }

# --------------------------
# Cookie helpers (rec history)
# --------------------------
def read_rec_history_from_cookie():
    raw = request.cookies.get("rec_history")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}

def update_rec_history_cookie(resp, form_data):
    """
    form_data: dict of submitted fields, e.g. genre/mood/activity/...
    We'll count genres and also save last_searches list.
    """
    history = read_rec_history_from_cookie()
    # count genres
    genre = form_data.get("genre")
    if genre:
        counts = history.get("genre_counts", {})
        counts[genre] = counts.get(genre, 0) + 1
        history["genre_counts"] = counts
    # store last form (for personal profile)
    last = history.get("last_forms", [])
    last.insert(0, form_data)
    history["last_forms"] = last[:10]
    # persist
    resp.set_cookie("rec_history", json.dumps(history), max_age=60*60*24*60)  # 60 days
    return resp

# --------------------------
# Recommendation engine (simple, robust)
# --------------------------
def build_recommendations_from_form(genre="", mood="", activity="", country="", people="", time_of_day=""):
    """
    Produce recommendations using iTunes search. Prioritise genre + country,
    then add mood/activity keywords. Deduplicate by trackId and require previewUrl.
    """
    queries = []
    # main priority
    if genre and country:
        queries.append(f"{genre} {country}")
    if genre:
        queries.append(genre)
    # mood/activity/time mapped to keywords
    mood_map = {
        "весёлое": "happy upbeat",
        "грустное": "sad mellow",
        "злостное": "angry heavy",
        "нейтральное": "calm chill"
    }
    activity_map = {
        "отдых": "relax lounge",
        "тренировка": "workout energetic",
        "поездка": "roadtrip driving",
        "учёба": "study focus instrumental"
    }
    extras = []
    if mood and mood in mood_map: extras.append(mood_map[mood])
    if activity and activity in activity_map: extras.append(activity_map[activity])
    if time_of_day:
        extras.append(time_of_day)
    # build combined queries
    for e in extras:
        if genre:
            queries.append(f"{genre} {e}")
        else:
            queries.append(e)
    # fallback queries
    queries.append("popular")
    queries.append("top hits")
    # run searches
    collected = []
    seen = set()
    for q in queries:
        if len(collected) >= RECOMMEND_LIMIT:
            break
        results = search_itunes(q, limit=20)
        for r in results:
            if not r.get("previewUrl"):
                continue
            tid = r.get("trackId") or (r.get("trackName","")+"_"+r.get("artistName",""))
            if tid in seen:
                continue
            seen.add(tid)
            collected.append(enrich_preview(r))
            if len(collected) >= RECOMMEND_LIMIT:
                break
        time.sleep(0.05)
    return collected

# --------------------------
# Routes
# --------------------------
@app.route("/")
def home():
    # show features and personal recommendations (if cookie)
    history = read_rec_history_from_cookie()
    personal_recs = []
    # compute top genre from history
    if history.get("genre_counts"):
        top_genre = max(history["genre_counts"].items(), key=lambda x: x[1])[0]
        # build recommendations based on top genre
        personal_recs = build_recommendations_from_form(genre=top_genre)
    return render_template("home.html", personal_recs=personal_recs)

@app.route("/search", methods=["GET","POST"])
def search():
    query = request.args.get("q") or ""
    results = []
    if request.method == "POST":
        query = request.form.get("q") or ""
    if query:
        results_raw = search_itunes(query, limit=30)
        results = [enrich_preview(r) for r in results_raw]
    return render_template("index.html", results=results, query=query)

@app.route("/recommend", methods=["GET","POST"])
def recommend():
    recommendations = []
    submitted = False
    if request.method == "POST":
        submitted = True
        genre = request.form.get("genre") or ""
        mood = request.form.get("mood") or ""
        activity = request.form.get("activity") or ""
        country = request.form.get("country") or ""
        people = request.form.get("people") or ""
        time_of_day = request.form.get("time_of_day") or ""

        # build recommendations
        recommendations = build_recommendations_from_form(genre=genre, mood=mood, activity=activity,
                                                         country=country, people=people, time_of_day=time_of_day)
        # set cookie with history
        resp = make_response(render_template("recommend.html", recommendations=recommendations, submitted=submitted, form=request.form))
        resp = update_rec_history_cookie(resp, dict(request.form))
        return resp
    return render_template("recommend.html", recommendations=recommendations, submitted=submitted)

# Simple registration/login/logout (demo)
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        display = request.form.get("display", username)
        if not username or not password:
            flash("Введите имя пользователя и пароль", "error")
            return render_template("register.html")
        if username in USERS:
            flash("Пользователь уже существует", "error")
            return render_template("register.html")
        USERS[username] = {"password": password, "display": display}
        session["user"] = username
        flash("Регистрация успешна", "success")
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        user = USERS.get(username)
        if not user or user.get("password") != password:
            flash("Неверные имя или пароль", "error")
            return render_template("login.html")
        session["user"] = username
        flash("Вход успешен", "success")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Вы вышли", "info")
    return redirect(url_for("home"))

@app.route("/profile")
def profile():
    user = session.get("user")
    history = read_rec_history_from_cookie()
    return render_template("profile.html", user=user, history=history)

# static helper route names are standard; no special endpoints necessary.

if __name__ == "__main__":
    app.run(debug=True)

