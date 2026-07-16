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


def main() -> None:
    songs = load_songs(SONGS_CSV)
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: favorite_genre=pop, favorite_mood=chill, target_energy=0.45, likes_acoustic=True
    user_prefs = {"genre": "pop", "mood": "chill", "energy": 0.45, "likes_acoustic": True}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']} (Score: {score:.2f}/100)")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()


if __name__ == "__main__":
    main()
