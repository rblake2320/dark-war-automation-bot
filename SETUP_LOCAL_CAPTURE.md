# Local iPhone capture setup

This branch is a read-only evidence pipeline for iPhone Mirroring. It is deliberately separate from the game-action runtime so a local model can inspect screenshots without being permitted to click blindly.

## Capture loop

1. Ensure iPhone Mirroring is connected and Dark War is visible.
2. Take a screenshot before navigation and after each single navigation action.
3. Save names that describe only verified states, such as `base.jpg`, `hero-list.jpg`, or `training-center.jpg`. Use `connection-paused.jpg` for diagnostics; do not label it as a game screen. The audit detects JPEG/PNG from the actual bytes rather than trusting an extension.
4. Run the local audit:

```bash
python3 capture_audit.py captures --output captures/manifest.json
python3 -m unittest discover -s tests -v
```

The manifest records hashes and dimensions so subsequent model runs can reference exact evidence. It performs no OCR and no device control.

## Local-model handoff

Give the model the screenshot plus its corresponding manifest entry, then require a structured response with:

```text
screen_type, visible_labels, red_dots, queues, timers, resources,
recommended_next_action, confidence, unsafe_or_ambiguous
```

Only a separate verified controller may act, and only when confidence is at least 0.80, the proposed action is allowlisted, and a visual postcondition is supplied. A purchase/premium/terms/account/alliance/PvP dialog is an automatic stop.

## Resuming after iPhone disconnects

When Mirroring says `iPhone in Use`, lock the iPhone and reconnect. Capture a fresh screen after connection returns; never reuse the coordinates from the prior session.
