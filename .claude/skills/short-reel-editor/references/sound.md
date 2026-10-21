# Sound design

## Music
- **Pick a track with no breakdowns.**
  - Run `scripts/beat.py energy <file>` on candidates: one character per second, and any space means near-silence. Reject tracks that go quiet or dip around 12 dB mid-way.
  - Epidemic search: `python -I scripts/epidemic.py search "upbeat tech groove" 100 128`. Download with `epidemic.py music <id> out.wav`.
- **Beat grid.**
  - `scripts/beat.py phase <file> <bpm>` finds where the beats fall.
  - In `mix.py`, set `bpm` and `beat_word`: the reel time of the word that must land on a beat, e.g. "beat" in "transitions hit on the beat". `music_offset` is then computed so a beat hits that word. Put graphic transitions on that same 0.5s grid.
- **Levels.**
  - Base gain about 0.32.
  - Sidechain duck under the voice: threshold 0.03, ratio 8, attack 15, release 350.
  - Fade in 0.08s and out over the last 1.4s.
  - The music must **never drop out**. Re-run `beat.py energy` on `bus/music.wav`: no spaces allowed.
- **Mid pocket:** EQ the music −3 dB at 1.2 kHz, −6 dB at 2.6 kHz and −4 dB at 4.8 kHz. EQ the SFX −2.5 dB at 1.5 kHz and −4 dB at 3.2 kHz.
- **Dips:** add short local music dips (0.4 depth) under words the intelligibility check flags. Keep them shallow so dip plus duck never hits silence.

## Voice chain
Default chain (in `mix.py`):
1. high-pass at 80 Hz
2. de-esser
3. gentle presence lift
4. compressor (threshold 0.09, ratio 3)

**User preset:** if the user shares their Premiere/Audition settings, copy them into the `vocal` block of the mix config. Example (a lav-mic preset):
- Parametric EQ:
  - HP 80 Hz at 24 dB/oct
  - low shelf 118 Hz, +6
  - 316 Hz −3 (width 210 Hz)
  - 2796 Hz +2.2 (width 1398 Hz)
  - high shelf 18.6 kHz, +5.1
- DeNoise: light, about 32% (`afftdn=nr=8`)
- Multiband compressor:
  - crossovers at 80, 250 and 10k
  - band 1: −24 dB, 2.5:1, +7 dB
  - band 2: −18 dB, 2:1, +6 dB
  - bands 3–4: unity
  - limiter at 0 dB, 4/500 ms
- Then the de-esser and leveller.

## SFX placement
Library files: click, error, impact, notif, pop, riser, shutter, success, thud, tick, typing, whoosh, whoosh2.

**Peak offsets** (so the hit lands on the cue time): whoosh 0.62, whoosh2 0.80, thud 0.17, impact 0.17, riser 2.51.

| Cue | Sound | Level |
|---|---|---|
| Layout change | whoosh | −10 |
| Into or out of full face | whoosh2 | −12 |
| Big C keyword | thud | −13 |
| Card or chip appears | pop | −9 to −12, trimmed to 0.22s |
| Counters and checkmarks | ticks | −12 to −15 |
| Cursor | click | −6 |
| Strike-through | error | −8 |
| Clip being cut | shutter | |
| Win or connect | success | −6 to −9 |
| Beat transitions | impact | −15, trimmed to 0.45s |

- **Never put a pop or chime on top of the word it illustrates.** Place it on the word's end or in the gap, otherwise it masks the word.
- **Check whoosh build-ups:** a whoosh peaks about 0.6s after it starts, so it can cover the word before a layout change.

## Checks (all in `scripts/check.py`)
- Loudness: −14 ±0.5 LUFS integrated, true peak ≤ −1.5 dBTP (`loudnorm` in the final pass).
- **Intelligibility:**
  - Transcribe the voice-only bus and the full mix, and compare both to `words_cut.json`.
  - The mix should score within about 1 point of the voice alone.
  - For any word that drops out only in the mix, solo-test voice+music against voice+SFX to find the culprit, then move or soften it.
- Small-model snippet transcriptions are noisy. Confirm a suspect word with `medium.en` on a short window before acting.

## Deliver the audio first
Send three files: `audio_vN.m4a`, `audio_vN.wav`, and `audio_vN_with_cut.mp4` (the mix over the approved cut). Render the final only after the user approves the audio.
