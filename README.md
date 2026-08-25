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

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).

## Help

We provide help on our [Discord server](https://discord.gg/6VzzNDwUwV).

## Issues

Found an issue with Remotion? [File an issue here](https://github.com/remotion-dev/remotion/issues/new).

## License

Note that for some entities a company license is needed. [Read the terms here](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).
