"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

try:
    from recommender import load_songs, recommend_songs
except ImportError:
    from src.recommender import load_songs, recommend_songs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SONGS_CSV = PROJECT_ROOT / "data" / "songs.csv"

TASTE_PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
}

# Adversarial / edge-case profiles for system evaluation.
# Each one targets a specific way score_song's genre-first weighting could
# produce a confusing or "tricked" result. See recommender.py for the
# scoring recipe these are designed to stress.
ADVERSARIAL_PROFILES = {
    # Metal fan who also wants low-energy, peaceful, acoustic songs. Tests
    # whether genre's 65pt weight steamrolls three conflicting signals.
    "Contradictory Metal Fan": {"genre": "metal", "mood": "relaxed", "energy": 0.1, "likes_acoustic": True},

    # Wants a fast (0.9 energy), sad song. "sad" only pairs with low-energy
    # songs in the catalog, so this preference is internally inconsistent.
    "Energetic Sadness": {"genre": "classical", "mood": "sad", "energy": 0.9, "likes_acoustic": True},

    # Probes the GENRE_FAMILIES asymmetry: "folk" lists "country" as related,
    # but "country" doesn't list folk's other neighbors (jazz/ambient/etc).
    "Country Fan (asymmetry probe)": {"genre": "country", "mood": "nostalgic", "energy": 0.5, "likes_acoustic": True},

    # Genre with no catalog presence and no GENRE_FAMILIES entry.
    "Unknown Genre": {"genre": "vaporwave", "mood": "happy", "energy": 0.5, "likes_acoustic": False},

    # Same genre as real songs, wrong case — exact/family lookups are
    # case-sensitive string comparisons.
    "Case Mismatch": {"genre": "Pop", "mood": "Happy", "energy": 0.8, "likes_acoustic": False},

    # Legal boundary values for energy.
    "Zero Energy Extreme": {"genre": "ambient", "mood": "chill", "energy": 0.0, "likes_acoustic": True},
    "Max Energy Extreme": {"genre": "metal", "mood": "angry", "energy": 1.0, "likes_acoustic": False},

    # target_energy outside the valid [0, 1] range — nothing validates this.
    "Out-of-Range Energy": {"genre": "pop", "mood": "happy", "energy": 1.8, "likes_acoustic": False},

    # Non-bool truthy value for likes_acoustic ("False" the string is truthy
    # in Python) — the dict-based API doesn't enforce types.
    "String False Gotcha": {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": "False"},

    # Empty preferences.
    "Empty Genre": {"genre": "", "mood": "", "energy": 0.5, "likes_acoustic": False},
}


def main() -> None:
    songs = load_songs(SONGS_CSV)
    print(f"Loaded songs: {len(songs)}")

    all_profiles = {**TASTE_PROFILES, **ADVERSARIAL_PROFILES}
    for profile_name, user_prefs in all_profiles.items():
        print(f"\n=== {profile_name} ===")
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\nTop recommendations:\n")
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"{rank}. {song['title']} - {song['artist']} (Score: {score:.2f}/77.5)")
            for reason in explanation.split("; "):
                print(f"     - {reason}")
            print()


if __name__ == "__main__":
    main()
