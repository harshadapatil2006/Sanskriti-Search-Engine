# Sanskriti Search Engine — Backend + Database

## Files
- `init_db.py` — Creates `sanskriti.db` (SQLite) with tables and seed data (Dharma, Karma, Moksha, Atman & Brahman, Ahimsa, Yoga, OM/AUM, Advaita Vedanta).
- `app.py` — Flask REST API that serves search results to your `ui.html`.
- `requirements.txt` — Python dependencies.

## Setup (ek baar karna hai)

```bash
cd sanskriti_backend
pip install -r requirements.txt

python init_db.py     # database banega: sanskriti.db
python app.py          # server chalu hoga: http://127.0.0.1:5000
```

## Database Schema
Table `scriptures`:
| column | type | notes |
|---|---|---|
| id | INTEGER PK | auto |
| title | TEXT | e.g. "Sa Vidya Ya Vimuktaye" |
| category | TEXT | Dharma / Karma / Moksha / etc. |
| source | TEXT | e.g. "Bhagavad Gita 2.47" |
| sanskrit_text | TEXT | devanagari |
| transliteration | TEXT | roman script |
| translation | TEXT | English meaning |
| explanation | TEXT | context/commentary |
| tags | TEXT | comma-separated keywords |

Plus a `scriptures_fts` virtual table (SQLite FTS5) for fast full-text search, kept in sync automatically via triggers. Also a `favorites` table if you want a "save this shloka" feature later.

## API Endpoints
| Method | URL | Purpose |
|---|---|---|
| GET | `/api/health` | check server is running |
| GET | `/api/search?q=karma` | search across all fields |
| GET | `/api/categories` | list categories with counts |
| GET | `/api/category/Dharma` | all entries in one category |
| GET | `/api/entry/3` | single entry by id |
| GET | `/api/favorites` | list saved favorites |
| POST | `/api/favorites` | body `{"scripture_id": 3}` |

## Connect to your `ui.html`
Add this JS to your search button's click handler (adjust selector IDs to match your HTML):

```javascript
async function searchScriptures(query) {
  const res = await fetch(`http://127.0.0.1:5000/api/search?q=${encodeURIComponent(query)}`);
  const data = await res.json();
  return data.results;
}

document.querySelector('.search-button').addEventListener('click', async () => {
  const query = document.querySelector('.search-input').value;
  const results = await searchScriptures(query);
  console.log(results); // render these into your results section
});
```

Since `ui.html` is opened via `file://`, `flask-cors` is already enabled in `app.py` so the browser won't block the request.

## Add more scripture data
Open `init_db.py`, add more tuples to the `SEED_DATA` list following the same
`(title, category, source, sanskrit_text, transliteration, translation, explanation, tags)`
format, delete `sanskriti.db`, and re-run `python init_db.py`.

## Submitted BY
Name : Harshada Ashok Patil
Class : Tybca (C)
