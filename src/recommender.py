import csv
from operator import itemgetter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

def _user_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the dict shape score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }

def _song_dict(song: Song) -> Dict:
    """Converts a Song into the dict shape score_song expects."""
    return {
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "acousticness": song.acousticness,
    }

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = [(score_song(_user_prefs(user), _song_dict(song))[0], song) for song in self.songs]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(_user_prefs(user), _song_dict(song))
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

# Genres that share a similar sound/vibe, used for partial credit when a
# song isn't an exact genre match but is closely related to it.
#
# Built from an undirected graph (cliques + bridges) instead of a hand-typed
# dict, so "A relates to B" always implies "B relates to A" by construction --
# a prior hand-maintained version had folk -> country without the reverse
# picking up folk's other neighbors, which meant a country fan got zero
# credit for a jazz song even though a folk fan would have gotten credit for
# that same song.
#
# GENRE_CLIQUES group genres that are mutually, fully related to each other.
GENRE_CLIQUES: List[set] = [
    {"pop", "indie pop", "k-pop", "synthwave"},
    # lofi/ambient/jazz/classical/folk/country: all sit in the catalog's
    # high-acousticness band (country=0.68, the rest 0.68-0.95), clearly
    # separated from the produced/pop-rock genres (0.03-0.40) -- country
    # belongs in this "acoustic roots" clique on the data, not just vibes.
    {"lofi", "ambient", "jazz", "classical", "folk", "country"},
    {"rock", "metal"},
    {"hip-hop", "r&b", "reggae"},
]

# GENRE_BRIDGES are single, deliberate cross-clique edges for well-established
# crossover genres, so the smallest clique (rock/metal, 2 catalog songs) isn't
# permanently stuck with far less credit-eligible surface area than the
# largest (8 songs). Each bridge is named after a real, commonly cited
# fusion genre rather than an arbitrary pairing.
GENRE_BRIDGES: List[Tuple[str, str]] = [
    ("rock", "country"),      # country rock / outlaw country
    ("metal", "classical"),   # neoclassical / symphonic metal
]

def _build_genre_families(cliques: List[set], bridges: List[Tuple[str, str]]) -> Dict[str, set]:
    families: Dict[str, set] = {}
    for clique in cliques:
        for genre in clique:
            families.setdefault(genre, set()).update(clique)
    for a, b in bridges:
        families.setdefault(a, {a}).add(b)
        families.setdefault(b, {b}).add(a)
    return families

GENRE_FAMILIES: Dict[str, set] = _build_genre_families(GENRE_CLIQUES, GENRE_BRIDGES)

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Algorithm Recipe (max 77.5 points, energy-weighted):
      - Genre match:        32.5 pts exact, 16.25 pts (50%) for a related genre
                             - halved from its original 65/32.5 split
      - Mood match:         20 pts (binary) - unchanged
      - Energy closeness:   20 pts (distance-based) - doubled from its original 10
      - Acousticness fit:    5 pts (distance-based) - unchanged

    NOTE: this is no longer a 100-point scale (32.5 + 20 + 20 + 5 = 77.5), and
    genre no longer dominates by design: an exact genre match (32.5) is now
    LESS than mood+energy+acoustic combined (45), so a song matching on
    mood+energy+acoustic alone can outscore a genre-only match. A related-genre
    match (16.25) still gives partial credit rather than scoring like a total
    mismatch.
    """
    GENRE_POINTS = 32.5
    GENRE_PARTIAL_CREDIT = 0.5
    MOOD_POINTS = 20
    ENERGY_POINTS = 20
    ACOUSTIC_POINTS = 5

    score = 0.0
    reasons: List[str] = []

    favorite_genre = user_prefs["genre"]
    if song["genre"] == favorite_genre:
        score += GENRE_POINTS
        reasons.append(f"Matches your favorite genre ({song['genre']}) (+{GENRE_POINTS:.1f})")
    elif song["genre"] in GENRE_FAMILIES.get(favorite_genre, set()):
        genre_score = GENRE_POINTS * GENRE_PARTIAL_CREDIT
        score += genre_score
        reasons.append(
            f"Genre ({song['genre']}) is related to your favorite ({favorite_genre}) (+{genre_score:.1f})"
        )

    if song["mood"] == user_prefs["mood"]:
        score += MOOD_POINTS
        reasons.append(f"Matches your favorite mood ({song['mood']}) (+{MOOD_POINTS:.1f})")

    energy_diff = abs(float(song["energy"]) - float(user_prefs["energy"]))
    energy_score = ENERGY_POINTS * max(0.0, 1 - energy_diff)
    score += energy_score
    if energy_diff <= 0.15:
        reasons.append(
            f"Energy ({song['energy']}) is close to your target ({user_prefs['energy']}) (+{energy_score:.1f})"
        )

    acousticness = float(song["acousticness"])
    if user_prefs.get("likes_acoustic"):
        acoustic_score = ACOUSTIC_POINTS * acousticness
        if acousticness >= 0.5:
            reasons.append(f"Has an acoustic sound, matching your preference (+{acoustic_score:.1f})")
    else:
        acoustic_score = ACOUSTIC_POINTS * (1 - acousticness)
        if acousticness < 0.5:
            reasons.append(
                f"Has a less acoustic, more produced sound, matching your preference (+{acoustic_score:.1f})"
            )
    score += acoustic_score

    if not reasons:
        reasons.append("No strong matches on genre, mood, energy, or acousticness")

    return score, reasons

def _score_entry(user_prefs: Dict, song: Dict) -> Tuple[Dict, float, str]:
    """Scores one song and packs it into a (song, score, explanation) tuple."""
    score, reasons = score_song(user_prefs, song)
    return song, score, "; ".join(reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [_score_entry(user_prefs, song) for song in songs]
    return sorted(scored, key=itemgetter(1), reverse=True)[:k]

if __name__ == "__main__":
    from pathlib import Path

    songs_csv = Path(__file__).resolve().parent.parent / "data" / "songs.csv"
    songs = load_songs(songs_csv)

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"Loaded {len(songs)} songs from {songs_csv.name}")
    print(f"\nTop 5 recommendations for {user_prefs}:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']} (Score: {score:.2f}/77.5)")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()
