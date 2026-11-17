# ACE! — player sequence (S3–S5), external production

Drop here, when produced:
- `serve.mp4` — H.264, 1080 x 1920, 30 or 60 fps, no audio needed (sounds are played by the game);
- `serve.json` — the timing manifest (see `src/render/aceCinematic.ts`, interface `ServeClip`):

```json
{ "src": "serve.mp4", "width": 1080, "height": 1920,
  "handoffAt": 0.0, "ball": { "x": 0.62, "y": 0.86, "d": 0.085 },
  "contactAt": 4.10, "occludedAt": 5.30 }
```

Without these two files the game plays the HTML5 version (logo, ball, fall,
bounces, camera push into the ball, real reels) — no stand-in character.
Full brief: docs/ACE_CINEMATIC.md.
