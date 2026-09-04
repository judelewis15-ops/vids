# Remotion video

<p align="center">
  <a href="https://github.com/remotion-dev/logo">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-dark.apng">
      <img alt="Animated Remotion Logo" src="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-light.gif">
    </picture>
  </a>
</p>

Welcome to your Remotion project!

## Commands

**Install Dependencies**

```console
npm i
```

**Start Preview**

```console
npm run dev
```

**Render video**

```console
npx remotion render
```

**Upgrade Remotion**

```console
npx remotion upgrade
```

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).

## Help

We provide help on our [Discord server](https://discord.gg/6VzzNDwUwV).

## Issues

Found an issue with Remotion? [File an issue here](https://github.com/remotion-dev/remotion/issues/new).

## License

Note that for some entities a company license is needed. [Read the terms here](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).

## Reel edit pipeline

Raw talking-head footage in, Instagram reel out. See `.claude/skills/edit-reel/SKILL.md` for the full flow.

```console
pip install imageio-ffmpeg faster-whisper     # ffmpeg binary + optional speech-to-text
python3 pipeline/fetch_broll.py scripts/02-ochra/broll.json
python3 pipeline/cut.py raw/C0011.MP4 --script scripts/02-ochra/script.txt --broll scripts/02-ochra/broll.json --whisper small
cat public/edit/takes.md                       # review the picks, edit public/edit/edit.json to override
npx remotion render src/index.ts Reel out/ochra.mp4 --codec=h264 --crf=18
```

`pipeline/cut.py` transcodes a proxy, splits on silence, matches takes to the script and keeps the
cleanest take per beat (later take wins ties), places b-roll on the matching beat, and writes
`public/edit/edit.json`. The `Reel` composition in `src/Reel.tsx` renders it at 1080x1920 with
cutaway or split b-roll, word captions in the Reels safe zone and a punch-in on alternate cuts.
Test without real footage: `bash pipeline/make_test_fixture.sh`.
