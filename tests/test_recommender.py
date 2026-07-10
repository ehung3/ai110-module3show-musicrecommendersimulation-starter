from src.recommender import Song, UserProfile, Recommender, score_song

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_gives_partial_credit_for_related_genre():
    # Mood, energy, and acousticness are identical across all three songs
    # so any score difference comes only from the genre match.
    user_prefs = {"genre": "pop", "mood": "energetic", "energy": 0.5, "likes_acoustic": False}

    exact_match_song = {"genre": "pop", "mood": "mismatch", "energy": 0.5, "acousticness": 0.5}
    related_genre_song = {"genre": "synthwave", "mood": "mismatch", "energy": 0.5, "acousticness": 0.5}
    unrelated_genre_song = {"genre": "metal", "mood": "mismatch", "energy": 0.5, "acousticness": 0.5}

    exact_score, _ = score_song(user_prefs, exact_match_song)
    related_score, related_reasons = score_song(user_prefs, related_genre_song)
    unrelated_score, _ = score_song(user_prefs, unrelated_genre_song)

    assert exact_score > related_score > unrelated_score
    assert any("related" in reason for reason in related_reasons)
