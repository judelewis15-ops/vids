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

## Media tooling

This project uses a few tools outside of npm for grabbing and inspecting video:

| Tool | Used for |
| --- | --- |
| [Playwright](https://playwright.dev/python/) | browser automation / page capture |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | downloading source video |
| [ffmpeg](https://ffmpeg.org/) | frame extraction and transcoding |

Install them with:

```console
./scripts/setup-tools.sh
```

The script is idempotent and covers both Homebrew (macOS) and apt + pip (Linux).
It also runs automatically at the start of every Claude Code session via the
`SessionStart` hook in `.claude/settings.json`.

Where a sandbox image already ships Chromium under `PLAYWRIGHT_BROWSERS_PATH`,
the script pins the Playwright release whose bundled Chromium revision matches
what is on disk rather than downloading a second copy.

## Watching video

Claude has no video input on its own. The [`/watch` skill](https://github.com/bradautomates/claude-video)
gives it one: `yt-dlp` fetches the video, `ffmpeg` samples scene-aware frames, and Claude reads each
frame as an image alongside a timestamped transcript.

Install it once:

```console
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
```

Then point it at a video and ask a question:

```console
/watch path/to/reel.mp4 what hook does this open with?
```

`scripts/setup-tools.sh` already installs the `yt-dlp` and `ffmpeg` binaries the skill depends on, so
its setup preflight comes back with nothing missing.

### Network requirements

In a Claude Code web session, egress is limited to the hosts allowed by the environment's
[network policy](https://code.claude.com/docs/en/claude-code-on-the-web). Watching a **local video
file** works with no policy changes. Watching from a **URL** needs the source host allowed:

| To watch | Allow |
| --- | --- |
| Instagram | `instagram.com`, `*.cdninstagram.com`, `*.fbcdn.net` |
| YouTube | `youtube.com`, `*.googlevideo.com` |
| Whisper transcription | `api.groq.com` or `api.openai.com` |

Without the Whisper hosts, transcripts come only from the source's own captions; frame extraction is
unaffected and works offline.

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).

## Help

We provide help on our [Discord server](https://discord.gg/6VzzNDwUwV).

## Issues

Found an issue with Remotion? [File an issue here](https://github.com/remotion-dev/remotion/issues/new).

## License

Note that for some entities a company license is needed. [Read the terms here](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).
