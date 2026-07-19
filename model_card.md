# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

JimmyRecs 1.0

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This is intended to generate recommendations that align with users' preferences based on four stated taste signals: favorite genre, favorite mood, a target energy level, and whether they like acoustic-sounding music. It ranks the song catalog by how closely each song matches those four signals and gives a plain-language explanation for every recommendation.

It assumes the user can state one fixed set of preferences up front, rather than needing the system to learn from listening history or feedback over time, and that genre/mood labels like "pop" or "chill" are a good enough proxy for someone's actual taste. This is a classroom exploration project built around an 18-song sample catalog, not a system meant to serve real listeners — the goal is to practice and test recommendation-scoring logic, not to ship a production recommender.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

JimmyRecs compares each song's genre, mood, energy, and how acoustic it sounds against what the listener said they like, awarding the most points for a genre match, a solid chunk for mood, and smaller amounts the closer the song's energy and acoustic feel are to their target. The biggest changes from the starter version were making energy count twice as much as it used to (at genre's expense) and rebuilding the "related genres" list so it's fair in both directions instead of favoring some genres with far more similar songs than others.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

There 18 songs in the catalog that represent the genres rock, ambient, jazz, synthwave, indie pop, indie pop, r&b, country, metal, folk, k-pop, hip-hop, classical, and rage. The moods include happy, chill (×3), intense (×2), relaxed, moody, focused, romantic, nostalgic, angry, melancholic, uplifting, playful, sad, carefree.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

Chill Lofi and High-Energy Pop profiles get the most reasonable results, since their genre lives in a larger family cluster (5-7 credit-eligible songs) and their exact-genre picks also happen to land close on mood and energy — matching intuition that "clear, well-represented tastes get well-rounded recommendations.
---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

One weakness we found through testing is that genre-match credit is not evenly available across the catalog, because `GENRE_FAMILIES` groups genres into clusters of very different sizes. A rock or metal fan is only ever eligible for genre points on 3 of the 18 songs (17%), while a folk or country fan is eligible on 8-9 songs (44-50%), simply because those clusters happen to contain more catalog entries. Since genre is our most heavily weighted signal, this means two users with equally specific, equally strong genre preferences get very different amounts of personalization: the rock/metal fan's rankings end up decided almost entirely by mood, energy, and acousticness, while the folk/country fan gets a much richer genre-driven ranking. Mood matching compounds this unevenly too — only "chill" and "intense" are shared by more than one song in the catalog, so most other mood preferences (sad, romantic, playful, etc.) can only ever earn credit from a single song. This shows the bias comes less from the scoring formula itself and more from how unevenly genres and moods are represented in the 18-song catalog — the algorithm doesn't invent the imbalance, but it passes it through silently, with no signal to the user that their low score reflects thin catalog coverage rather than a genuine mismatch in taste.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

We evaluated the recommender with two sets of profiles: the three baseline "taste profiles" already in `main.py` (High-Energy Pop, Chill Lofi, Deep Intense Rock), and nine adversarial edge-case profiles we added specifically to try to break the scoring. These included a "Contradictory Metal Fan" (metal genre paired with a relaxed mood, low target energy, and `likes_acoustic=True`), an "Energetic Sadness" profile (classical genre, sad mood, energy target 0.9), a genre-family asymmetry probe (folk vs. country), an unknown genre, an empty genre/mood, a case-mismatched genre, energy values at the 0/1 boundaries and outside the valid range, and a non-boolean `likes_acoustic` value. For each profile we checked three things: whether `score_song` crashed or returned an out-of-range score, whether the top-ranked song and its explanation text made intuitive sense given the stated weights, and whether the ranking revealed any structural bias in `GENRE_FAMILIES` or the energy-distance formula.

Several results surprised us. The `likes_acoustic="False"` profile confirmed that a non-empty string is truthy in Python, so it was silently treated as `True` — the dict-based API doesn't validate input types. The genre-family probe caught a real bug: a folk fan got partial credit for a country song, but a country fan got zero credit for a jazz song, even though a folk fan would have gotten credit for that same jazz song (since fixed — see Section 6 and the `test_genre_families_are_symmetric` regression test). Sorting all 18 songs' energy values also exposed a 0.15-wide gap between 0.55 and 0.70 with no songs at all, meaning a "moderate energy" listener is structurally capped below users whose target sits near the extremes, regardless of how well the rest of their profile matches.

We captured these cases as automated tests in `tests/test_recommender.py`, growing the suite from 3 tests to 14, including a regression test that checks `GENRE_FAMILIES` stays symmetric for every genre pair so that specific bug can't silently reappear. All 14 tests pass against the current weights (genre 32.5 exact / 16.25 related, mood 20, energy 20, acousticness 5, max score 77.5).

### Comparing the three baseline profiles

**High-Energy Pop vs. Chill Lofi.** Chill Lofi's top pick ("Library Rain," 76.80/77.5) actually scores *higher* than High-Energy Pop's top pick ("Sunrise City," 75.00/77.5), even though "high energy" sounds like the more demanding ask. That makes sense once you look at the energy numbers: Library Rain's energy (0.35) exactly matches Chill Lofi's target (0.35), while the closest song to High-Energy Pop's target of 0.9 is Sunrise City at 0.82 — an 0.08 gap that costs real points. In plain terms, it doesn't matter whether a listener wants calm or intense music; what matters is whether the catalog happens to have a song sitting exactly on their target.

**High-Energy Pop vs. Deep Intense Rock.** Both profiles want energy around 0.9, but their lists fall apart at very different rates. High-Energy Pop's score only drops from 75.00 to 56.70 between rank 1 and 2 (an 18-point gap), while Deep Intense Rock's drops from 76.80 to 44.15 (a 32-point cliff). This makes sense given genre-cluster size: pop's family has 5 credit-eligible songs in the catalog, so the runner-up ("Rooftop Lights") still picks up partial genre credit; rock's family only has 3, so once you leave the one near-perfect match ("Storm Runner"), the next-best song ("Gym Hero") gets zero genre credit at all. A small genre cluster doesn't hurt the #1 recommendation, but it makes the rest of the list noticeably weaker.

**Chill Lofi vs. Deep Intense Rock.** These are near-opposite tastes (calm/acoustic vs. loud/produced), and their top picks score almost identically (76.80 for both), but the shape of their top-5 lists is very different: Chill Lofi's scores taper off gently (76.80 → 74.65 → 59.45 → 55.40 → 40.30), while Deep Intense Rock's collapse fast (76.80 → 44.15 → 39.70 → 29.45 → 24.20). This lines up with genre-family size again — lofi's family spans 7 songs (lofi, ambient, jazz, classical, folk, country), so there are several similar songs to fall back on, while rock's family only spans 3. A Chill Lofi listener gets a genuinely rich top-5; a Deep Intense Rock listener gets one great match and four increasingly weak ones, purely because their genre has less company in this catalog.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

I would include a more comprehensive recommendation that displays to the user why each song was chosen and what each compenent means. Then, the user would be able to select their preference for what should be ranked higher based on what's more important to them.
---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned a lot about how to integrate data sets into a program and understanding how one function impacts another. It really helped me differentiate the purpose of the main.py file, tests, and the recommender.