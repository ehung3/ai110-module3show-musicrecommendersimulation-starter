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
GENRE_FAMILIES: Dict[str, set] = {
    "pop": {"pop", "indie pop", "k-pop", "synthwave"},
    "indie pop": {"pop", "indie pop", "k-pop", "synthwave"},
    "k-pop": {"pop", "indie pop", "k-pop", "synthwave"},
    "synthwave": {"pop", "indie pop", "k-pop", "synthwave"},
    "lofi": {"lofi", "ambient", "jazz", "folk", "classical"},
    "ambient": {"lofi", "ambient", "jazz", "folk", "classical"},
    "jazz": {"lofi", "ambient", "jazz", "folk", "classical"},
    "classical": {"lofi", "ambient", "jazz", "folk", "classical"},
    "folk": {"lofi", "ambient", "jazz", "folk", "classical", "country"},
    "country": {"folk", "country"},
    "rock": {"rock", "metal"},
    "metal": {"rock", "metal"},
    "hip-hop": {"hip-hop", "r&b", "reggae"},
    "r&b": {"hip-hop", "r&b", "reggae"},
    "reggae": {"hip-hop", "r&b", "reggae"},
}

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Algorithm Recipe (max 100 points, genre-first hierarchical weighting):
      - Genre match:        65 pts exact, 32.5 pts (50%) for a related genre
                             - strongest, most explicit taste signal
      - Mood match:         20 pts (binary) - real signal, but fuzzier than genre
      - Energy closeness:   10 pts (distance-based) - a target, not a hard rule
      - Acousticness fit:    5 pts (distance-based) - soft secondary preference

    An exact genre match (65) still outweighs the max combined score of
    every other feature (35), so it can never lose to a song that only
    matches on mood/energy/acousticness. A related-genre match (32.5) gives
    partial credit instead of scoring identically to a total mismatch.
    """
    GENRE_POINTS = 65
    GENRE_PARTIAL_CREDIT = 0.5
    MOOD_POINTS = 20
    ENERGY_POINTS = 10
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
