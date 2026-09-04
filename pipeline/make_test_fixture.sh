#!/usr/bin/env bash
# Builds synthetic footage + transcript so the pipeline can be tested without real video.
# Usage: bash pipeline/make_test_fixture.sh && python3 pipeline/cut.py raw/test.mp4 \
#   --script scripts/_test/script.txt --transcript scripts/_test/words.json --broll scripts/_test/broll.json
# then: npx remotion render src/index.ts Reel out/test.mp4 --chrome-mode=chrome-for-testing \
#   --browser-executable=/opt/pw-browsers/chromium   (browser flags only needed in the web sandbox)
set -e
cd "$(dirname "$0")/.."
FF=$(command -v ffmpeg || python3 -c "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())")
mkdir -p raw public/broll/test out
# 14 s landscape source: three tone "takes" at 0-2.5, 4-7.5, 9-12 s with silence between
$FF -y -hide_banner -loglevel error -f lavfi -i "testsrc2=size=1920x1080:rate=30" \
  -f lavfi -i "aevalsrc=exprs='if(lt(t,2.5),0.5*sin(440*2*PI*t),if(lt(t,4),0,if(lt(t,7.5),0.5*sin(550*2*PI*t),if(lt(t,9),0,if(lt(t,12),0.5*sin(660*2*PI*t),0)))))':s=48000:d=14" \
  -t 14 -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k raw/test.mp4
$FF -y -hide_banner -loglevel error -f lavfi -i "testsrc2=size=720x1280:rate=30" -t 5 -c:v libx264 -preset veryfast -pix_fmt yuv420p public/broll/test/a.mp4
$FF -y -hide_banner -loglevel error -f lavfi -i "smptehdbars=size=720x1280:rate=30" -t 5 -c:v libx264 -preset veryfast -pix_fmt yuv420p public/broll/test/b.mp4
echo "fixture ready: raw/test.mp4, public/broll/test/{a,b}.mp4, scripts/_test/*"
