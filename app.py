"""
app.py
Sanskriti Search Engine - Backend API (Flask + SQLite)

Endpoints:
    GET  /api/health                  -> server check
    GET  /api/categories              -> list of all categories with counts
    GET  /api/search?q=karma          -> full text search across all fields
    GET  /api/category/<name>         -> all entries in a category
    GET  /api/entry/<id>              -> single entry by id
    POST /api/favorites               -> save an entry as favorite (body: {"scripture_id": 1})
    GET  /api/favorites                -> list favorites

Run:
    pip install -r requirements.txt
    python init_db.py      # only once, to create + seed the database
    python app.py           # starts server on http://127.0.0.1:5000
"""

import sqlite3
import os
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS

DB_PATH = os.path.join(os.path.dirname(__file__), "sanskriti.db")

app = Flask(__name__)
CORS(app)  # allows ui.html (opened via file://) to call this API


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "category": row["category"],
        "source": row["source"],
        "sanskrit_text": row["sanskrit_text"],
        "transliteration": row["transliteration"],
        "translation": row["translation"],
        "explanation": row["explanation"],
        "tags": row["tags"].split(",") if row["tags"] else [],
    }
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "message": "Sanskriti Search Engine backend running"})


@app.route("/api/categories")
def categories():
    db = get_db()
    rows = db.execute("""
        SELECT category, COUNT(*) as count
        FROM scriptures
        GROUP BY category
        ORDER BY category
    """).fetchall()
    return jsonify([{"category": r["category"], "count": r["count"]} for r in rows])


@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Please provide a search query using ?q="}), 400

    db = get_db()

    # Use FTS5 for ranked full text search. Wrap query terms for basic safety
    # and to support partial word matches with a trailing wildcard.
    fts_query = " OR ".join(f"{term}*" for term in query.split())

    try:
        rows = db.execute("""
            SELECT s.* FROM scriptures s
            JOIN scriptures_fts f ON s.id = f.rowid
            WHERE scriptures_fts MATCH ?
            ORDER BY rank
            LIMIT 50
        """, (fts_query,)).fetchall()
    except sqlite3.OperationalError:
        # Fallback to simple LIKE search if FTS query syntax fails
        like_q = f"%{query}%"
        rows = db.execute("""
            SELECT * FROM scriptures
            WHERE title LIKE ? OR translation LIKE ? OR explanation LIKE ?
               OR tags LIKE ? OR category LIKE ?
            LIMIT 50
        """, (like_q, like_q, like_q, like_q, like_q)).fetchall()

    results = [row_to_dict(r) for r in rows]
    return jsonify({"query": query, "count": len(results), "results": results})


@app.route("/api/category/<name>")
def by_category(name):
    db = get_db()
    rows = db.execute("""
        SELECT * FROM scriptures WHERE category = ? COLLATE NOCASE
    """, (name,)).fetchall()
    return jsonify({"category": name, "count": len(rows), "results": [row_to_dict(r) for r in rows]})


@app.route("/api/entry/<int:entry_id>")
def entry(entry_id):
    db = get_db()
    row = db.execute("SELECT * FROM scriptures WHERE id = ?", (entry_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify(row_to_dict(row))


@app.route("/api/favorites", methods=["GET"])
def list_favorites():
    db = get_db()
    rows = db.execute("""
        SELECT f.id as fav_id, f.user_name, f.created_at, s.*
        FROM favorites f
        JOIN scriptures s ON f.scripture_id = s.id
        ORDER BY f.created_at DESC
    """).fetchall()
    results = []
    for r in rows:
        item = row_to_dict(r)
        item["favorite_id"] = r["fav_id"]
        item["saved_at"] = r["created_at"]
        results.append(item)
    return jsonify(results)


@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json(silent=True) or {}
    scripture_id = data.get("scripture_id")
    user_name = data.get("user_name", "guest")

    if not scripture_id:
        return jsonify({"error": "scripture_id is required"}), 400

    db = get_db()
    exists = db.execute("SELECT id FROM scriptures WHERE id = ?", (scripture_id,)).fetchone()
    if not exists:
        return jsonify({"error": "No scripture found with that id"}), 404

    db.execute("INSERT INTO favorites (scripture_id, user_name) VALUES (?, ?)",
               (scripture_id, user_name))
    db.commit()
    return jsonify({"message": "Added to favorites"}), 201


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database not found. Run 'python init_db.py' first.")
    app.run(debug=True, port=5000)
