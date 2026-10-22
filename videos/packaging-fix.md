# Packaging fix: the two live videos

Goal: make the existing videos findable, before making a third.
Written 2026-10-22. Baseline on that date: video 1 = 95 views, video 2 = 75 views.

## The diagnosis

At under ~1,000 subscribers YouTube sends almost no browse or suggested traffic.
Search is the only door open. Both current titles are **browse-style titles** — they
work when an audience already knows you, and do nothing when nobody does.

| Video | Current title | Why it gets no impressions |
|---|---|---|
| 1 (7:41) | I Wish I Knew This on Day 1 at the Gym (8 Exercises That Start Your Engine) | "I Wish I Knew This" is a curiosity frame, not a query. "Start Your Engine" is a metaphor nobody types. The searchable phrase, *beginner gym exercises*, is buried in a bracket. |
| 2 (9:59) | Your Calorie Deficit Isn't Broken. Your Numbers Are. | Clever, and completely unsearchable. No beginner types "calorie deficit isn't broken". They type "why am I not losing weight". |

Rule for the next 12 months: **the first 3-4 words of every title are the phrase a
beginner would type.** Cleverness goes after the colon, or nowhere.

---

## Video 1 — re-title

**Use this:**
```
Beginner Gym Workout: The Only 8 Exercises You Need (Full Body Plan)
```

Backups, in order:
1. `First Day at the Gym? Do These 8 Exercises (Beginner Full Body Workout)`
2. `8 Best Gym Exercises for Beginners (With Form + Weekly Plan)`

Why: "beginner gym workout" and "first day at the gym" are the two phrases with
million-view proof in this niche in the last 12 months (Yatinder Singh's *First Month
At Gym*, 2.13M, Oct 2025; Badri Fitness's Hindi first-day video, 16.9M). "The Only
8 Exercises You Need" keeps a curiosity hook without costing the keyword.

**Description — change the first two lines to:**
```
A complete beginner gym workout: the 8 exercises that matter, how to do each one,
and the 3-day weekly plan. No machines you can't find, no 2-hour sessions.
```
Keep everything below that as-is. The current opening ("Your body has an engine")
is a good hook for a viewer who already clicked, but search reads the first line too.

---

## Video 2 — re-title

**Use this:**
```
Why You're Not Losing Weight in a Calorie Deficit (Doctor Explains)
```

Backups:
1. `Calorie Deficit Not Working? Here's What You're Getting Wrong`
2. `You're Eating More Than You Think — The Calorie Deficit Mistake`

Why: "why am I not losing weight" is a question people type in full. "(Doctor
Explains)" is your only unfair advantage on this topic and it is currently nowhere in
your packaging — put it in the title of every video where it is true.

---

## Thumbnails

Both should be rebuilt to the `red-ink-explainer` signature already in
`styles/red-ink-explainer.yaml`, so the channel reads as one body of work.

Rules that apply to both:
- **Three or four words maximum**, readable at 120px wide. Test it by shrinking it.
- Red keyword box on one word only, matching the in-video caption style.
- Owner's face on one side, looking at the text, not at the camera.
- No full sentence. No exercise collage. No arrows.

**Video 1:** owner's back photo already used at 0:00, left third. Right side, stacked:
`8 EXERCISES` / `DAY 1` — with the red box on `DAY 1`.

**Video 2:** owner's face left, concerned expression. Right side: `NOT LOSING` /
`WEIGHT?` — red box on `WEIGHT?`. A plate or a scale in the lower corner, dim,
no text on it.

---

## Also fix, same sitting

1. **Chapters on video 2.** Video 1 has them; video 2 appears not to. Chapters raise
   average view duration because people re-enter at the part they want.
2. **End screen on video 1 points at nothing.** The render leaves two empty end-screen
   frames (see `videos/beginner-gym-engine/README.md`). Point one at video 2 and one
   at "most recent upload" — that is free watch time from people already watching.
3. **Pin the comment on both.** Video 1's is written; video 2 needs one.

---

## How to read the result

Change the titles and thumbnails, then **leave them alone for 14 days.** In YouTube
Studio, look at one number per video: **impressions**, not views.

- Impressions climb → packaging was the problem, repeat this on every future video.
- Impressions stay flat → the topic has no search demand for a channel this size,
  and the next video should be chosen from the proven-demand list, not from interest.

Do not change both the title and the thumbnail again inside those 14 days, or the
result tells you nothing.

---

## The bigger question, not answered here

Your script is in English, your voice is Hindi with a Haryanvi accent, and every
million-view video in the research set was Hindi or Hinglish. English fitness is the
most crowded category on YouTube; Hinglish beginner fitness, from an actual doctor,
is not. Worth deciding before video 3 — it changes the script, not just the title.

---

# Do this now — ordered checklist

Order matters: title first (biggest lever, costs nothing), thumbnail second,
everything else third. Do all of it in one sitting, then do not touch it for 14 days.

## Video 1 — "Start Your Engine" (7:41)

- [ ] **Title** → `Beginner Gym Workout: The Only 8 Exercises You Need (Full Body Plan)`
- [ ] **Description first line** → replace with the two lines in the section above.
- [ ] **Thumbnail** → `8 EXERCISES` / `DAY 1`, red box on `DAY 1`.
- [ ] **End screen** → fill both empty frames: one on video 2, one on "most recent upload".
- [ ] **Pinned comment** → already written in `shorts_captions.md`, just pin it.
- [ ] **Tags** → already good, leave them.

## Video 2 — "Your Calorie Deficit Isn't Broken" (9:59)

- [ ] **Title** → `Why You're Not Losing Weight in a Calorie Deficit (Doctor Explains)`
- [ ] **Thumbnail** → `NOT LOSING` / `WEIGHT?`, red box on `WEIGHT?`, concerned face left.
- [ ] **Description** → paste the block below.
- [ ] **Chapters** → add them. Timestamps must be filled in from the actual video;
      the first one must be `0:00`.
- [ ] **End screen** → one frame on video 1, one on "most recent upload".
- [ ] **Pinned comment** → paste the line below.

### Video 2 description (fill the chapter times from the video)

```
You're eating in a deficit and the scale won't move. Here's what's actually
happening — and the three numbers almost everyone gets wrong.

📌 Save this and re-check your numbers before you cut calories again.

⏱ CHAPTERS
0:00 [opening — the problem]
[time] [what a deficit actually is]
[time] [mistake 1]
[time] [mistake 2]
[time] [mistake 3]
[time] [how to fix your numbers]
[time] What to do this week

📲 Instagram: @drmak_fitness
🔔 Subscribe for science-backed training: @drmakfitness

⚠️ Educational content, not medical advice. If you have a medical condition,
check with your doctor first.

#caloriedeficit #weightloss #fatloss #fitnessscience #drmakfitness
```

### Video 2 pinned comment

```
What's your current daily calorie target? Drop the number 👇
I'll tell you if it's realistic — I reply to every comment.
```

## Both videos — the three free wins

1. **Playlist.** Make one playlist, "Start Here: Gym for Beginners", put both videos
   in it in order. Playlists feed autoplay, and autoplay is watch hours you do not
   have to earn twice.
2. **Cards.** Put a card in each video pointing at the other, placed at the moment
   the topic is mentioned, not at the end.
3. **Each video's comment.** Reply to every single comment for the first 48 hours.
   At this channel size it is the only engagement signal you can manufacture honestly.

## What NOT to do

- Do not buy views or run ads to the video. Purchased watch time does not count
  toward the 4,000 hours and risks the channel.
- Do not re-upload either video. You lose the existing views and the watch time.
- Do not change the titles again inside 14 days — the test stops meaning anything.
