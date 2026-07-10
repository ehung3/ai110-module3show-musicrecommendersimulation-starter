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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # TODO: Implement CSV loading logic
    print(f"Loading songs from {csv_path}...")
    return []

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
        reasons.append(f"Matches your favorite genre ({song['genre']})")
    elif song["genre"] in GENRE_FAMILIES.get(favorite_genre, set()):
        score += GENRE_POINTS * GENRE_PARTIAL_CREDIT
        reasons.append(f"Genre ({song['genre']}) is related to your favorite ({favorite_genre})")

    if song["mood"] == user_prefs["mood"]:
        score += MOOD_POINTS
        reasons.append(f"Matches your favorite mood ({song['mood']})")

    energy_diff = abs(float(song["energy"]) - float(user_prefs["energy"]))
    energy_score = ENERGY_POINTS * max(0.0, 1 - energy_diff)
    score += energy_score
    if energy_diff <= 0.15:
        reasons.append(f"Energy ({song['energy']}) is close to your target ({user_prefs['energy']})")

    acousticness = float(song["acousticness"])
    if user_prefs.get("likes_acoustic"):
        acoustic_score = ACOUSTIC_POINTS * acousticness
        if acousticness >= 0.5:
            reasons.append("Has an acoustic sound, matching your preference")
    else:
        acoustic_score = ACOUSTIC_POINTS * (1 - acousticness)
        if acousticness < 0.5:
            reasons.append("Has a less acoustic, more produced sound, matching your preference")
    score += acoustic_score

    if not reasons:
        reasons.append("No strong matches on genre, mood, energy, or acousticness")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
