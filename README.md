# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

Song Features Included:
- id, title, artist, genre, mood, energy, acousticness, tempo_bpm, valence, danceability
- Used in scoring: genre, mood, energy, acousticness

UserProfile Features:
- favorite_genre, favorite_mood, target_energy, likes_acoustic

### Algorithm Recipe

Each song is scored out of 100 points using genre-first hierarchical weighting, so a genre match can never be outranked by a song that only matches on the weaker, fuzzier signals:

- **Genre match — 65 pts exact, 32.5 pts (50%) related:** the strongest, most explicit taste signal. If `song.genre == favorite_genre`, the song gets the full 65 points. If it doesn't match exactly but falls in the same genre family (e.g. `pop` / `indie pop` / `k-pop` / `synthwave`, or `lofi` / `ambient` / `jazz` / `folk` / `classical`), it gets half credit instead of zero. Genres with no relation get 0.
- **Mood match — 20 pts (binary):** a real signal, but moods blur together more than genres do (e.g. "chill" vs "relaxed"), so it's weighted lower.
- **Energy closeness — 10 pts (distance-based):** scored as `10 * (1 - |song.energy - target_energy|)`, since energy is a target to get close to, not a pass/fail rule.
- **Acousticness fit — 5 pts (distance-based):** scored proportional to `acousticness` (or its inverse) depending on `likes_acoustic`, treated as a soft secondary preference.

Because an exact genre match (65) outweighs the maximum combined score of every other feature (35), the system always prioritizes an exact genre match over songs that "feel similar" in mood, energy, or acousticness. A related-genre match (32.5) still outscores mood/energy/acousticness on their own, but can be overtaken by a song that matches several of those at once, giving related genres a meaningful boost without letting them override an exact match. Each song's score also comes with a list of plain-language reasons (e.g. "Matches your favorite genre (pop)" or "Genre (synthwave) is related to your favorite (pop)") used to build the explanation shown to the user.

### Potential Biases

- **Genre dominance can bury good fits:** because genre carries almost 2/3 of the total score, a song in the "right" genre but a poor mood/energy fit will usually still outrank a song in a different genre that matches everything else — this could make the system feel repetitive or overly genre-loyal.
- **Catalog bias:** with only 18 songs and a handful of genres/moods represented, some user profiles have no strong matches available at all, which will systematically under-recommend to those tastes regardless of how good the scoring logic is.
- **No personalization over time:** the scoring is static per request — it doesn't learn from skips, replays, or listening history, so it can't correct for blind spots the initial weighting introduces.

You can include a simple diagram or bullet list if helpful.

There are two types of filtering, collaborative and content-based. Collaborative focuses on looking at other users who agree with the people you agree with to make recommendations. It's helpful because it relies on behavioral patterns rather than what the content features. However, the trade-off is it has a problem for new users who don't have any data to base off. Content-based filtering focuses on if a user likes something with specific traits, they'll like other content with similar traits. This is useful for users with niche tastes or when users are new. However, it limits the algorithim into a filter bubble by recommending more of the same content. Many platforms, including mine for this project, will utilize a hybrid of these two frameworks. Collaborative will highlight a wide net based on behavior, while content-based filtering will fill gaps. Using a deep learning model that reads number of skips, session length, and time of day will reinforce this model. Lastly, optimizing reinforcement learning will keep recommendations up-to-date based on whether the song was skipped, replayed, or listened until the end.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

One experiment I tried was creating a taste profile with pop and chill as the preferred genre/mood. This was interesting because no song co exists with both so three non-pop lofi songs outranked both pop songs since they fulfilled three criteria strongly vs the one.
---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



