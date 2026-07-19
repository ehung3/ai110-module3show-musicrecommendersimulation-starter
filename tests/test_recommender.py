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


# --- Adversarial / edge-case profiles -------------------------------------
# These document how score_song behaves under contradictory or malformed
# input, not just "happy path" preferences. Some assertions describe
# existing behavior (including a real asymmetry bug) rather than ideal
# behavior — see comments on each test.

def test_contradictory_metal_fan_no_longer_favors_genre_after_weight_shift():
    # User wants metal (genre) but also relaxed/low-energy/acoustic (everything
    # else) -- a combination that doesn't really exist.
    #
    # Under the original weights (genre=65) a real metal song still beat a
    # genuinely relaxed/acoustic song, because genre alone (65) outweighed
    # mood+energy+acoustic combined (35). After halving genre and doubling
    # energy (genre=32.5, energy=20), that invariant flips: genre (32.5) is
    # now less than mood+energy+acoustic combined (45), so a song that
    # matches everything BUT genre can outscore a genre-only match. This test
    # documents the flip rather than asserting the old (no longer true) result.
    user_prefs = {"genre": "metal", "mood": "relaxed", "energy": 0.1, "likes_acoustic": True}

    real_metal_song = {"genre": "metal", "mood": "angry", "energy": 0.97, "acousticness": 0.03}
    relaxed_acoustic_song = {"genre": "ambient", "mood": "relaxed", "energy": 0.1, "acousticness": 0.95}

    metal_score, _ = score_song(user_prefs, real_metal_song)
    relaxed_score, _ = score_song(user_prefs, relaxed_acoustic_song)

    assert metal_score == 35.25  # genre (32.5) + energy (2.6) + acoustic (0.15), no mood
    assert relaxed_score == 44.75  # mood (20) + energy (20) + acoustic (4.75), no genre
    assert relaxed_score > metal_score


def test_energetic_sadness_mismatch_genre_and_mood_still_win():
    # "Sad" pairs with low energy in practice; asking for energy=0.9 with a
    # sad mood is internally contradictory. Genre+mood match should still
    # beat a song that only matches the (contradictory) energy target.
    user_prefs = {"genre": "classical", "mood": "sad", "energy": 0.9, "likes_acoustic": True}

    classical_sad_low_energy_song = {"genre": "classical", "mood": "sad", "energy": 0.20, "acousticness": 0.95}
    unrelated_high_energy_song = {"genre": "pop", "mood": "intense", "energy": 0.93, "acousticness": 0.05}

    classical_score, _ = score_song(user_prefs, classical_sad_low_energy_song)
    high_energy_score, _ = score_song(user_prefs, unrelated_high_energy_song)

    assert classical_score > high_energy_score


def test_genre_family_asymmetry_bug_is_fixed():
    # Previously: GENRE_FAMILIES["folk"] included "country", but
    # GENRE_FAMILIES["country"] didn't include folk's other neighbors
    # (jazz/ambient/lofi/classical), so a country fan got zero credit for a
    # jazz song even though a folk fan got credit for that same song.
    # GENRE_FAMILIES is now built from a symmetric clique (see
    # GENRE_CLIQUES), so country and folk share the exact same family.
    country_song = {"genre": "country", "mood": "mismatch", "energy": 0.5, "acousticness": 0.5}
    jazz_song = {"genre": "jazz", "mood": "mismatch", "energy": 0.5, "acousticness": 0.5}
    unrelated_genre_song = {"genre": "hip-hop", "mood": "mismatch", "energy": 0.5, "acousticness": 0.5}

    folk_fan_prefs = {"genre": "folk", "mood": "x", "energy": 0.5, "likes_acoustic": False}
    country_fan_prefs = {"genre": "country", "mood": "x", "energy": 0.5, "likes_acoustic": False}

    # Baseline: score when genre gives zero credit (mood/energy/acoustic only).
    no_genre_credit_baseline, _ = score_song(country_fan_prefs, unrelated_genre_song)

    folk_fan_on_country_score, _ = score_song(folk_fan_prefs, country_song)
    country_fan_on_jazz_score, _ = score_song(country_fan_prefs, jazz_song)

    assert folk_fan_on_country_score > no_genre_credit_baseline  # folk -> country gets partial credit
    assert country_fan_on_jazz_score > no_genre_credit_baseline  # country -> jazz now gets partial credit too
    assert country_fan_on_jazz_score == folk_fan_on_country_score  # same partial-credit amount either direction


def test_genre_families_are_symmetric():
    # Regression guard for the whole class of bug above: for every genre, if
    # B is in A's family, A must be in B's family.
    from src.recommender import GENRE_FAMILIES

    for genre, related in GENRE_FAMILIES.items():
        for other in related:
            assert genre in GENRE_FAMILIES.get(other, set()), (
                f"{other!r} is in {genre!r}'s family but not vice versa"
            )


def test_rock_metal_country_are_no_longer_stuck_at_two_related_genres():
    # Previously rock/metal/country each had only their own 2-genre clique
    # (or, for country, a lopsided 2-genre link to folk) while folk's cluster
    # spanned 6 genres. The rock<->country and metal<->classical bridges
    # give the smallest cluster more credit-eligible genres without
    # merging it wholesale into the acoustic-roots clique.
    from src.recommender import GENRE_FAMILIES

    assert GENRE_FAMILIES["rock"] == {"rock", "metal", "country"}
    assert GENRE_FAMILIES["metal"] == {"rock", "metal", "classical"}
    assert "rock" in GENRE_FAMILIES["country"]
    assert "metal" in GENRE_FAMILIES["classical"]


def test_unknown_genre_gets_no_genre_credit_but_does_not_crash():
    user_prefs = {"genre": "vaporwave", "mood": "happy", "energy": 0.5, "likes_acoustic": False}
    song = {"genre": "pop", "mood": "happy", "energy": 0.5, "acousticness": 0.5}

    score, reasons = score_song(user_prefs, song)

    # Mood match (20) + energy match (20) + acoustic match (2.5) = 42.5, no genre points
    assert score == 42.5
    assert not any("genre" in reason.lower() for reason in reasons)


def test_genre_case_mismatch_scores_as_no_match():
    # Same genre, different case -- current implementation is case-sensitive
    # so this scores identically to a genre with no relation at all.
    user_prefs = {"genre": "Pop", "mood": "happy", "energy": 0.5, "likes_acoustic": False}
    song = {"genre": "pop", "mood": "happy", "energy": 0.5, "acousticness": 0.5}

    score, _ = score_song(user_prefs, song)

    assert score == 42.5  # mood (20) + energy (20) + acoustic (2.5), no genre credit


def test_energy_boundary_values_do_not_crash_and_stay_in_range():
    song = {"genre": "ambient", "mood": "chill", "energy": 0.0, "acousticness": 0.5}

    zero_score, _ = score_song({"genre": "ambient", "mood": "chill", "energy": 0.0, "likes_acoustic": False}, song)
    max_score, _ = score_song({"genre": "ambient", "mood": "chill", "energy": 1.0, "likes_acoustic": False}, song)

    assert zero_score > max_score  # target 0.0 exactly matches song energy 0.0
    assert 0 <= zero_score <= 77.5  # 77.5 is the current max possible score
    assert 0 <= max_score <= 77.5


def test_out_of_range_target_energy_is_not_validated():
    # target_energy=1.8 is outside the valid [0, 1] range; nothing in
    # score_song rejects it. energy_diff exceeds 1, so energy_score clamps
    # to 0 via max(0.0, 1 - energy_diff) rather than going negative.
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 1.8, "likes_acoustic": False}
    song = {"genre": "pop", "mood": "happy", "energy": 0.5, "acousticness": 0.5}

    score, reasons = score_song(user_prefs, song)

    assert score == 32.5 + 20 + 0 + 2.5  # genre + mood + zero energy credit + acoustic
    assert not any("close to your target" in reason for reason in reasons)


def test_truthy_string_for_likes_acoustic_is_treated_as_true():
    # likes_acoustic="False" (a non-empty string) is truthy in Python, so
    # score_song's `if user_prefs.get("likes_acoustic"):` branch treats it
    # as True. This documents that the dict-based API trusts caller types.
    user_prefs = {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": "False"}
    high_acousticness_song = {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "acousticness": 0.9}

    score, reasons = score_song(user_prefs, high_acousticness_song)

    assert any("acoustic sound, matching your preference" in reason for reason in reasons)


def test_empty_genre_and_mood_get_no_credit():
    user_prefs = {"genre": "", "mood": "", "energy": 0.5, "likes_acoustic": False}
    song = {"genre": "pop", "mood": "happy", "energy": 0.5, "acousticness": 0.5}

    score, _ = score_song(user_prefs, song)

    assert score == 22.5  # energy (20) + acoustic (2.5) only
