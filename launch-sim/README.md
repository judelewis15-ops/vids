# Hypha launch simulation (MiroFish)

Runs [MiroFish](https://github.com/666ghj/MiroFish) on the Hypha app onboarding built in Kinflo. MiroFish creates AI personas from the seed document, simulates them posting and reacting on simulated X-style and Reddit-style platforms, and writes a prediction report.

- `seed/hypha-app-launch.md`: the launch as MiroFish sees it. It covers the brand, product, pricing, all five onboarding routes with their copy, the paywalls and the open issues. It was pulled from the Kinflo onboarding session of 7–8 Oct 2026.
- `question.txt`: what the simulation should predict.
- `run_mirofish.py`: runs the whole pipeline against a local MiroFish backend and saves the report to `out/`.

## Before it can run

The cloud environment needs:

1. **Network access** to `api.getzep.com` and to your model provider's API host. Add these under Allowed domains in the environment settings.
2. **Environment variables:**
   - `LLM_API_KEY`
   - `LLM_BASE_URL`, for example `https://api.openai.com/v1`
   - `LLM_MODEL_NAME`, for example `gpt-4o-mini`
   - `ZEP_API_KEY`, from https://app.getzep.com (the free tier is enough)

MiroFish reads these straight from the environment, so no `.env` file is needed.

## Run

```bash
git clone --depth 1 https://github.com/666ghj/MiroFish ~/mirofish
cd ~/mirofish/backend && uv sync --python 3.12
uv run python run.py &          # backend on :5001
cd -                            # back to this repo
python3 launch-sim/run_mirofish.py \
  --seed launch-sim/seed/hypha-app-launch.md \
  --question launch-sim/question.txt \
  --rounds 30
```

Start with 30 rounds or fewer, because MiroFish makes a lot of model calls.
