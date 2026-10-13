# Hypha launch simulation (MiroFish)

Runs [MiroFish](https://github.com/666ghj/MiroFish) on the Hypha app onboarding built in Kinflo. MiroFish creates AI personas from the seed document, simulates them posting and reacting on simulated X-style and Reddit-style platforms, and writes a prediction report.

- `seed/hypha-app-launch.md`: the launch as MiroFish sees it. It covers the brand, product, pricing, all five onboarding routes with their copy, the paywalls and the open issues. It was pulled from the Kinflo onboarding session of 7–8 Oct 2026.
- `question.txt`: what the simulation should predict.
- `mirofish-claude.patch`: lets MiroFish run on Claude through Anthropic's OpenAI-compatible endpoint. It stops sending `temperature`, which current Claude models reject below 1, and gives `max_tokens` a default. It also tolerates a lead-in before JSON replies, and skips tiktoken's encoding download for Claude agents.
- `run.sh`: sets everything up, checks the keys and network, runs the pipeline and saves the report to `out/`. MiroFish is pinned to commit `7657031`.
- `run_mirofish.py`: the pipeline driver that `run.sh` calls.

## Before it can run

In the cloud environment settings:

1. **Network access:** add `api.getzep.com` under Allowed domains. `api.anthropic.com` is already reachable.
2. **Environment variables:**
   ```
   LLM_API_KEY=<Anthropic API key from platform.claude.com/settings/keys>
   LLM_BASE_URL=https://api.anthropic.com/v1/
   LLM_MODEL_NAME=claude-opus-5-5
   ZEP_API_KEY=<key from app.getzep.com>
   ```

Then start a new session so it picks the settings up.

## Run

```bash
bash launch-sim/run.sh --rounds 30
```

This takes a while: the persona simulation alone can run for an hour or more. The report lands in `launch-sim/out/report.md`.
