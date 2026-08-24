# The film

12 seconds, 1080x1920, H.264, 30fps. Built from CSS and Playwright frame capture,
then encoded with ffmpeg. No AI generation and no video editor.

    node render.cjs                    # 360 frames into frames/
    ffmpeg -framerate 30 -i frames/f%04d.jpg -c:v libx264 -pix_fmt yuv420p \
      -profile:v high -crf 18 -movflags +faststart -r 30 hypha-promo.mp4

`film.html` exposes `window.setTime(t)`, which positions every element for a given
second. render.cjs steps it 1/30s at a time and screenshots. Animation is a pure
function of time, so any frame can be reproduced without replaying the timeline.

Playwright ships a stripped ffmpeg that only encodes VP8, so the repo depends on
`ffmpeg-static` for an H.264 build.

## Beats

| Time | Screen | Caption |
|---|---|---|
| 0-3s | Courses | Cultivation courses. Beginner to expert. |
| 3-6s | Profile | Expert cultivators. Available 24/7. |
| 6-9s | Feed | A feed for questions and community. |
| 9-12s | Logo | Free grow kit for the first 500 on annual. Grows 1kg. |

Screens cross-dissolve over 0.5s. The device pushes in from 0.95 to 1.03 and turns
7 degrees across the first nine seconds, then lifts out for the end card.

## Still missing

- The profile post image is an empty placeholder, and the two feed post images are
  flat gradients. All three want real cultivation photography.
- The closing beat names a grow kit without showing one.
- Silent. Instagram will loop it fine, but audio would carry it further.

Filling those needs either photographs or Higgsfield generation, which is blocked
while the account is on a freemium trial.
