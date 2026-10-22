# Packaging fix: the two live videos

Applied in YouTube Studio on **22 Oct 2026**. Baseline that day: video 1 = 95 views,
video 2 = 75 views. Read the result on **5 Nov 2026** (see *How to read the result*).

## Why this was needed

Under ~1,000 subscribers YouTube sends almost no browse or suggested traffic. Search
is the only door open, and both videos had **browse-style titles** — the kind that
work when an audience already knows you, and do nothing when nobody does.

| Video | Old title | Why it got no impressions |
|---|---|---|
| 1 (7:41) | I Wish I Knew This on Day 1 at the Gym (8 Exercises That Start Your Engine) | "I Wish I Knew This" is a curiosity frame, not a query. "Start Your Engine" is a metaphor nobody types. The searchable phrase was buried in a bracket. |
| 2 (9:59) | Your Calorie Deficit Isn't Broken. Your Numbers Are. | Clever and unsearchable. Nobody types "calorie deficit isn't broken" — they type "weight nahi ghat raha". Worse, the title was English over Hinglish audio. |

**The rule going forward: the first 3-4 words of every title are the phrase a viewer
would actually type, in the language the video is spoken in.** Cleverness goes after
the colon, or nowhere.

---

## What was changed

### Video 1 — beginner gym workout (7:41)

**Title**
```
Beginner Gym Workout: The Only 8 Exercises You Need (Full Body Plan)
```
Backups if this one tests flat: `First Day at the Gym? Do These 8 Exercises (Beginner
Full Body Workout)` · `8 Best Gym Exercises for Beginners (With Form + Weekly Plan)`

**Description opening** (rest of the description unchanged)
```
A complete beginner gym workout: the 8 exercises that matter, how to do each one,
and the 3-day weekly plan. No machines you can't find, no 2-hour sessions.
```

**Thumbnail** — `8 EXERCISES` / `DAY 1` in the red box, physique photo right.
Rendered by `render/thumb.html?v=1`.

> **Open question:** this title is English. If video 1's voice-over is Hinglish like
> video 2, it needs the same language switch — e.g. `Gym Ka Pehla Din? Ye 8 Exercises
> Karo`. Check before the next change.

### Video 2 — calorie deficit (9:59, Hinglish)

**Title**
```
Weight Nahi Ghat Raha? Calorie Deficit Ki 6 Galtiyan
```
Backup: `Calorie Deficit Mein Ho Phir Bhi Weight Nahi Ghat Raha? (6 Wajah)`

**Description**
```
Calorie deficit mein ho, phir bhi weight nahi ghat raha? Problem aapki willpower
nahi hai — problem ye hai ki aapka deficit real hai hi nahi.

Ek chamach oil = ~120 calories, aur wo kabhi count hi nahi hoti. Is video mein
6 wajah, aur har ek ka fix.

📌 Save karo aur calories kam karne se pehle apne numbers dobara check karo.

⏱ CHAPTERS
0:00 Aapka deficit real kyun nahi hai
0:58 1. Maintenance ek guess hai
2:19 2. Aap zyada khaate ho (oil, ghee, tadka)
3:56 3. Smartwatch calories jhooth bolti hai
5:10 4. Zyada exercise = zyada burn nahi
6:30 5. Scale paani dikhata hai, fat nahi
7:56 6. Weekend poora hafta mita deta hai
9:12 Recap

📲 Instagram: @drmak_fitness
🔔 Subscribe for science-backed fitness: @drmakfitness

⚠️ Educational content, not medical advice. Koi medical condition hai toh pehle
apne doctor se baat karein.
```

**Tags**
```
calorie deficit, weight nahi ghat raha, calorie deficit in hindi, weight loss
hindi, fat loss hindi, calorie counting mistakes, hidden calories, oil calories,
weight loss plateau, maintenance calories, tdee, smartwatch calories accurate,
weight loss tips hindi, dr mak fitness
```

**Pinned comment**
```
In 6 mein se kaunsi galti aap kar rahe ho? Number drop karo 👇 (1-6)
Main har comment ka reply karta hoon.
```

**Thumbnail** — `WEIGHT NAHI` / `GHAT RAHA?` in the green box, scrubs photo right,
graded to the video's own palette (bg `#060606`, accent `#23C55E`, pill `#E54746`,
sampled from the video). Rendered by `render/thumb.html?v=2`.

---

## Thumbnail rules (for every future video)

- **Three or four words maximum**, readable at 120px wide. Shrink it to check.
- One accent box on one phrase, in the colour the video itself uses — a thumbnail
  graded to a different palette than its video is a mismatch the viewer feels on click.
- Owner on one side, text on the other. Face to camera for problem/answer videos;
  physique for training videos.
- No full sentences, no collages, no arrows.

Both variants live in `videos/beginner-gym-engine/render/thumb.html`. Add video 3 as a
new entry in the `V` object, then `node shot.mjs 3 out.png`. The owner's photos go in
`assets/user/` and are gitignored — they are never committed.

---

## Still to do

- [ ] **Playlist** "Start Here: Gym for Beginners", both videos in order. Playlists
      feed autoplay, and autoplay is watch time you don't earn twice.
- [ ] **Cards** in each video pointing at the other, placed where the topic comes up,
      not at the end.
- [ ] **End screens.** Video 1's render leaves two empty frames (see
      `beginner-gym-engine/README.md`). One on video 2, one on "most recent upload".
- [ ] **Replace the scrubs photo** if the original file exists — the current one is a
      photo of a screen, so it carries moiré and grain. Drop it at
      `assets/user/face.jpg` and re-run `node shot.mjs 2`.
- [ ] **Reply to every comment** for the first 48 hours after any change.

---

## How to read the result

Read it on **5 Nov 2026**, not before. In YouTube Studio look at **impressions** per
video, not views.

- Impressions climb → packaging was the bottleneck. Apply this to every upload.
- Impressions flat → the topic has no search demand at this channel size. Pick video 3
  from a proven-demand topic instead of an interesting one.

Changing a title's language resets who YouTube tests the video on, so impressions may
dip for a few days first. That is expected, not failure.

**Do not** change a title or thumbnail again inside the 14 days, or the test tells you
nothing. **Do not** buy views or run ads — purchased watch time doesn't count toward
the 4,000 hours and risks the channel. **Do not** re-upload either video; you lose the
views and watch time already banked.

---

## Language rule

Video 2 was published in English over Hinglish audio. That is the worst of both:
English speakers click and bounce when the audio is Hindi, and the Hinglish audience
the video is made for never finds it, because they search in Hinglish.

**Match the title, description and thumbnail language to the audio language.** No
million-view Indian fitness video in the last 12 months of research carried an English
title over Hindi audio.

This is still an open decision for the channel as a whole: the repo's scripts,
captions and shorts copy are all written in English, while the voice is Hindi with a
Haryanvi accent. English fitness is the most crowded category on YouTube. Hinglish
beginner fitness from an actual doctor is not. Settle it before video 3 — it changes
the script, not just the packaging.
