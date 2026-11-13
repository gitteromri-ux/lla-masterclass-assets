# Julie Masterclass: Video and Complete Editing Handoff

## Current video

[Open or download the 90-second MP4](https://raw.githubusercontent.com/gitteromri-ux/lla-masterclass-assets/main/nov14-reference-edit/Julie-Masterclass-90s-Reference-Card-Edit.mp4)

1920 × 1080, 30 fps, H.264/AAC, exactly 90 seconds. This is a new cut from the 136.63-second masterclass film, not a recovered copy of the previously requested existing 90-second source.

The video retains the opening through 01:02.800 and adds reference-led ending cards. The original later slow-aging card and outdated event cards are omitted. The new cards show Nov 14th at 12 PM ET, VIP duration wording, and an enrollment finish.

**Music limitation:** the soundtrack uses crossfaded repeated instrumental sections from the original film, followed by its closing tail and a fade. It is not a continuous single-pass retiming. Review the musical repetition before publication.

## Editable projects

- [Current editable project, including source film](editable/Julie-Masterclass-Editable-Final.zip): Python card renderer, FFmpeg assembly script, original images, fonts, lossless 1080p cards, measured text bounds, and the long masterclass source.
- [Earlier animated ending project](editable/Earlier-Animated-Ending-Project.zip): the prior layered artwork and GSAP/HyperFrames project. Its assembly instructions refer to the earlier, rejected base; do not use that assembly as the current edit.
- [Current full-resolution cards](cards/): five PNG cards and a contact sheet.
- [User-supplied visual references](references/): the five reference images supplied for the final style direction.

## Source footage

- [Original full film, 16:9](source-videos/julie-film-16x9-1080p-original.mp4)
- [Original full film, 4:5](source-videos/julie-film-4x5-1080x1350.mp4)
- [Existing “75-second” masterclass cut](source-videos/Existing-Masterclass-75s-Cut.mp4): actual runtime approximately 71.93 seconds; contains older event details.
- The 136.63-second long masterclass edit is included in the current editable ZIP as `source/masterclass-source.mp4`.
- [Upstream masterclass gallery](https://gitteromri-ux.github.io/lla-masterclass-assets/julie-film-v4/)

## Superseded work

These files are retained for handoff completeness, not recommended for publication.

- [Rejected Ad#11 review cut](superseded/REJECTED-Ad11-Review-Cut.mp4): wrong base footage; do not confuse with the current masterclass cut.
- [Earlier silent ending animation](superseded/Earlier-Silent-Ending-Animation.mp4)
- [Card-design history](superseded/Card-Design-History.zip): previous card versions, original clock/logo assets, image layers, and card-rendering scripts. Earlier designs and copy may be outdated or rejected.

## Rebuild and verification

Extract the current editable ZIP, install Python with Pillow and NumPy, and install FFmpeg. Run `bash render.sh` from the extracted folder. The bundled source directory provides the film, fonts, and image assets.

The current MP4 was fully decoded without reported FFmpeg errors. Both video and audio streams measure 90.000 seconds. Text bounds and rendered 390-pixel-wide proofs were checked for cropping. The public MP4 was downloaded without authentication and its SHA-256 matched the delivered local file:

`bae240992790a19558b24fff84af2dc95896582cf05430e0499f797754b4c614`

These checks do not constitute user approval. GitHub publication was requested for download and handoff; no Facebook post, ad, or production website was changed.
