# ACE! — player sequence (S3–S5), external production

Drop here, when produced (no code change needed):
- `serve.mp4` — H.264, 1080 x 1920, 30 or 60 fps, no audio track (sounds are played by the game);
- `serve.json` — the timing manifest (interface `ServeClip` in `src/render/aceCinematic.ts`):

```json
{ "src": "serve.mp4", "width": 1080, "height": 1920,
  "handoffAt": 0.0, "ball": { "x": 0.60, "y": 0.84, "d": 0.115 },
  "cues": [{ "t": 2.10, "sound": "bounce", "volume": 0.5 }],
  "contactAt": 5.20,
  "exit": { "at": 5.30, "x": 0.52, "y": 0.42, "d": 0.06, "ms": 320 },
  "occludedAt": 5.60 }
```

Frame 0 of the clip must be identical to `docs/ace_handoff/handoff_frame.png`
(the exact frame where the HTML5 ball comes to rest; `handoff_plate.png` is the
same framing without the ball).  Without these files the game plays the HTML5
version (logo, fall, bounces, ball at rest, camera push, real reels) — no
stand-in character.  Full brief: docs/ACE_CINEMATIC.md §4.
