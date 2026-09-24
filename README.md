# Cura-DraftShieldSpeed

A Cura 5.13 post-processing script that lets the **Draft Shield** use a
different speed from the skirt/brim.

## Why?

Cura normally ties draft-shield speed to skirt/brim behaviour. That is useful
for first-layer adhesion, but it can make the draft shield needlessly slow.

This script keeps the first layer exactly as Cura generated it and changes the
speed of the later draft-shield extrusion only.

## Behaviour

- Layer 0 is untouched, so skirt/brim first-layer speed is preserved.
- From `LAYER:1` onward, Cura's `TYPE:SKIRT` sections are treated as the
  draft shield.
- Only XY extrusion moves in those sections are changed.
- Travel moves and retractions are left untouched.
- The previous print feed rate is restored when leaving the draft shield.

## Settings

**Draft Shield Speed Source**

- **Print Speed** — default; use the profile's main Print Speed.
- **Custom** — specify a dedicated Draft Shield Speed in mm/s.

## Installation

Copy `DraftShieldSpeed.py` to Cura's user scripts directory.

For Cura 5.13 on Linux this is typically:

```text
~/.local/share/cura/5.13/scripts/
```

Restart Cura, then open:

**Extensions → Post Processing → Modify G-Code → Add a script → Draft Shield Speed**

## Tested behaviour

Tested with Cura 5.13:

- brim / layer 0 remained at 30 mm/s;
- later draft shield ran at 60 mm/s;
- travel and retraction moves remained unchanged.

## Compatibility

Currently validated only with Cura 5.13.

The script relies on Cura identifying the draft shield as `TYPE:SKIRT` after
layer 0. If Cura changes that G-code convention in a future release, the
script may need updating.

## License

MIT.
