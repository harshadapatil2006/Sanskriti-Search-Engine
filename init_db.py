"""
init_db.py
Sanskriti Search Engine - Database setup script
Yeh script SQLite database banata hai aur usme sample scripture data
(Vedas, Upanishads, Dharma, Karma, Moksha, etc.) daalta hai.

Run karne ke liye:
    python init_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sanskriti.db")


def create_tables(conn):
    cur = conn.cursor()

    # Main table: scripture entries (Vedas, Upanishads, Gita shlokas, concepts, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scriptures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT,
            sanskrit_text TEXT,
            transliteration TEXT,
            translation TEXT,
            explanation TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Full text search table (SQLite FTS5) for fast keyword search
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS scriptures_fts USING fts5(
            title, category, sanskrit_text, transliteration, translation, explanation, tags,
            content='scriptures',
            content_rowid='id'
        )
    """)

    # Triggers to keep FTS table in sync with the main table
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS scriptures_ai AFTER INSERT ON scriptures BEGIN
            INSERT INTO scriptures_fts(rowid, title, category, sanskrit_text, transliteration, translation, explanation, tags)
            VALUES (new.id, new.title, new.category, new.sanskrit_text, new.transliteration, new.translation, new.explanation, new.tags);
        END;
    """)
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS scriptures_ad AFTER DELETE ON scriptures BEGIN
            INSERT INTO scriptures_fts(scriptures_fts, rowid, title, category, sanskrit_text, transliteration, translation, explanation, tags)
            VALUES('delete', old.id, old.title, old.category, old.sanskrit_text, old.transliteration, old.translation, old.explanation, old.tags);
        END;
    """)
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS scriptures_au AFTER UPDATE ON scriptures BEGIN
            INSERT INTO scriptures_fts(scriptures_fts, rowid, title, category, sanskrit_text, transliteration, translation, explanation, tags)
            VALUES('delete', old.id, old.title, old.category, old.sanskrit_text, old.transliteration, old.translation, old.explanation, old.tags);
            INSERT INTO scriptures_fts(rowid, title, category, sanskrit_text, transliteration, translation, explanation, tags)
            VALUES (new.id, new.title, new.category, new.sanskrit_text, new.transliteration, new.translation, new.explanation, new.tags);
        END;
    """)

    # Optional: users table if you later want saved searches / favorites
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scripture_id INTEGER NOT NULL,
            user_name TEXT DEFAULT 'guest',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scripture_id) REFERENCES scriptures(id)
        )
    """)

    conn.commit()


SEED_DATA = [
    # (title, category, source, sanskrit_text, transliteration, translation, explanation, tags)
    ("Sa Vidya Ya Vimuktaye", "Moksha", "Vishnu Purana",
     "सा विद्या या विमुक्तये",
     "sā vidyā yā vimuktaye",
     "That alone is knowledge which liberates.",
     "This verse defines true education as that which frees a person from ignorance and the cycle of birth and death, not merely information gathering.",
     "knowledge,liberation,education,moksha"),

    ("What is Dharma", "Dharma", "Mahabharata",
     "धर्म एव हतो हन्ति धर्मो रक्षति रक्षितः",
     "dharma eva hato hanti dharmo rakshati rakshitah",
     "Dharma destroyed destroys; Dharma protected protects.",
     "Dharma refers to righteous duty and moral order. This verse teaches that living in accordance with dharma protects a person, while abandoning it leads to one's own downfall.",
     "dharma,duty,righteousness,ethics"),

    ("Law of Karma", "Karma", "Bhagavad Gita 2.47",
     "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
     "karmaṇy-evādhikāras te mā phaleṣu kadācana",
     "You have the right to perform your duty, but never to the fruits of action.",
     "One of the most famous verses of the Gita, teaching detachment from results while remaining committed to right action.",
     "karma,action,duty,detachment,gita"),

    ("Atman is Brahman", "Atman & Brahman", "Chandogya Upanishad",
     "तत्त्वमसि",
     "tat tvam asi",
     "Thou art That.",
     "One of the four Mahavakyas (great sayings) of the Upanishads, declaring the identity of the individual soul (Atman) with the universal reality (Brahman).",
     "atman,brahman,upanishad,mahavakya,advaita"),

    ("Ahimsa Paramo Dharma", "Ahimsa", "Mahabharata",
     "अहिंसा परमो धर्मः",
     "ahiṃsā paramo dharmaḥ",
     "Non-violence is the highest duty.",
     "This teaching places non-violence at the very top of ethical conduct, forming the basis of Jain, Buddhist and Hindu ethics alike.",
     "ahimsa,nonviolence,dharma,ethics"),

    ("Yoga as Union", "Yoga", "Yoga Sutras of Patanjali 1.2",
     "योगश्चित्तवृत्तिनिरोधः",
     "yogaś citta-vṛtti-nirodhaḥ",
     "Yoga is the stilling of the fluctuations of the mind.",
     "Patanjali defines yoga not as physical postures but as the disciplined stilling of mental modifications to reach clarity and self-realization.",
     "yoga,patanjali,mind,meditation"),

    ("The Sound of Om", "OM / AUM", "Mandukya Upanishad",
     "ॐ इत्येतदक्षरमिदं सर्वं",
     "oṃ ity etad akṣaram idaṃ sarvaṃ",
     "Om, this syllable, is all this.",
     "The Mandukya Upanishad opens by declaring Om as the primordial sound representing all of past, present, future, and the Self beyond time.",
     "om,aum,pranava,sound,upanishad"),

    ("Non-Duality", "Advaita Vedanta", "Adi Shankaracharya, Vivekachudamani",
     "ब्रह्म सत्यं जगन्मिथ्या जीवो ब्रह्मैव नापरः",
     "brahma satyaṃ jagan mithyā jīvo brahmaiva nāparaḥ",
     "Brahman alone is real, the world is illusory, the individual soul is non-different from Brahman.",
     "This is the central teaching of Advaita (non-dual) Vedanta as systematized by Adi Shankaracharya, distinguishing absolute reality from apparent phenomenal existence.",
     "advaita,vedanta,brahman,maya,nonduality"),

    ("Sarve Bhavantu Sukhinah", "Dharma", "Brihadaranyaka Upanishad (Shanti Mantra)",
     "सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः",
     "sarve bhavantu sukhinaḥ sarve santu nirāmayāḥ",
     "May all beings be happy, may all beings be free from illness.",
     "A universal peace prayer (shanti mantra) wishing wellbeing for all creation without exception, reflecting the inclusive spirit of dharma.",
     "dharma,peace,prayer,universal wellbeing"),

    ("Three Gunas and Karma", "Karma", "Bhagavad Gita 14.5",
     "सत्त्वं रजस्तम इति गुणाः प्रकृतिसम्भवाः",
     "sattvaṃ rajas tama iti guṇāḥ prakṛti-sambhavāḥ",
     "Goodness, passion, and ignorance are the three qualities born of material nature.",
     "The Gita explains that actions (karma) are shaped by the three gunas, and understanding them helps one act with greater awareness and less bondage.",
     "karma,guna,gita,nature,action"),

    ("Neti Neti", "Atman & Brahman", "Brihadaranyaka Upanishad",
     "नेति नेति",
     "neti neti",
     "Not this, not this.",
     "A method of negation used to describe Brahman, indicating that the ultimate reality cannot be fully captured by any finite description.",
     "atman,brahman,neti neti,negation,upanishad"),

    ("Moksha as Freedom", "Moksha", "Katha Upanishad",
     "उत्तिष्ठत जाग्रत प्राप्य वरान्निबोधत",
     "uttiṣṭhata jāgrata prāpya varān nibodhata",
     "Arise, awake, and learn by approaching the excellent ones.",
     "A call to spiritual awakening, often cited as encouragement to pursue self-knowledge and liberation (moksha) actively rather than passively.",
     "moksha,awakening,katha upanishad,liberation"),
]


def seed_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scriptures")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"Database already has {count} entries. Skipping seed to avoid duplicates.")
        return

    cur.executemany("""
        INSERT INTO scriptures
        (title, category, source, sanskrit_text, transliteration, translation, explanation, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, SEED_DATA)
    conn.commit()
    print(f"Inserted {len(SEED_DATA)} seed entries.")


def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_data(conn)
    conn.close()
    print(f"Database ready at: {DB_PATH}")


if __name__ == "__main__":
    main()
