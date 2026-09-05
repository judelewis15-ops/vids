# HO01 María Sabina · Cost gate report

Date: 05 Sep 2026. Account: Pro, balance 7330 credits at session start. Nothing generated. Zero credits spent.

## Blockers that stop generation

1. **BUDGET_TOTAL is not set.** Section 7 says Jude sets it at the start of the session. It is not in the brief, the repo, or the environment. Without it the 80 percent stop cannot be tracked.
2. **The per-job cap of 120 credits is below the quoted price of 14 of the 35 planned jobs** as the brief writes them. Resolution and duration are fixed by the brief, so section 7's only permitted remedies (reduce duration or resolution) are not available. See the table.
3. **cdn.openart.ai is denied by this session's egress policy** (403 on CONNECT, recorded in the proxy status). No generated PNG or MP4 can be saved into the repo from this environment. Generation itself works, because the OpenArt MCP calls go through the allowed Anthropic proxy and reference OpenArt-hosted URLs. Files would have to be pulled down by Jude, or the policy amended to allow cdn.openart.ai.

## Reference clip

The brief's `IDbmkGjjxF87lxxCQFgl` is the clip's OpenArt item id. Its historyId is `FfAwxUXkfa5CQV3uMYsi`. It is the only South Africa paper-cutout map clip in the account history (100 most recent items scanned, two pages). Its prompt is saved verbatim in `style/ref_map_sa_prompt.txt`. Its end frame, `Uvb2zjC5DftohFtJwGwi`, is the frame the clip was locked to end on and is usable directly as a visualReference. Hosted URLs are in `style/ref_map_sa_source.json`.

Note the reference clip is 6.04 s at 720x1280 and its prompt renders the labels. Our version is 5 s and renders no labels, as the brief specifies.

## Quotes

All quotes from `openart_model_cost` with the exact params. 9:16, videoCount 1, no audio, 720p or std unless stated.

| Model + mode | Per unit | Quoted configurations |
|---|---|---|
| nano-banana-pro image2image 2K | 40 per image | imageCount 1 = 40, 3 = 120, 4 = 160 |
| gpt-image-2 image2image 2k medium | 47 per image | imageCount 1 = 47 |
| wan2-7 image2video 720p | 25 per second | 2s 50, 3s 75, 4s 100, 5s 125, 6s 150, 7s 175 |
| kling-3-omni image2video std, sound off | 25 per second | 3s 75, 4s 100, 5s 125 |
| kling-3-omni element2video std, sound off | 25 per second | 3s 75, 5s 125, 7s 175 |
| gemini-omni-1-1-flash element2video 720p | 50 per second | 3s 150, 4s 200, 5s 250, 7s 350 |
| byte-plus-seedance-2 image2video 720p, audio off | | 4s 320, 5s 400, 5s fast mode 350 |
| byte-plus-seedance-2 image2video 1080p, audio off | | 5s 1000 (the one permitted map rerun) |

Duration floors: Wan 2s, Kling 3s, Gemini Omni 3s, Seedance 4s. Shot 12 is written as 2s on Gemini Omni, which cannot run below 3s.

## Projected clean run, no rejects, brief's first-call models as written

| Block | Jobs | Credits |
|---|---|---|
| Style set, imageCount 4 | 1 | 160 |
| Character sheets, 4 sheets x imageCount 4 | 4 | 640 |
| Map end frame, imageCount 4 | 1 | 160 |
| Shot keyframes, 17 x imageCount 1 | 17 | 680 |
| Keyframes subtotal | 23 | 1640 |
| Map video, Seedance 5s | 1 | 400 |
| Gemini Omni shots 01 (7s), 06 (4s), 11 (5s), 12 (3s floor), 13C (3s) | 5 | 1100 |
| Wan shots 04, 05, 07, 08, 09, 10, 13A, 13B, 14, 15, 16, 17 | 12 | 975 |
| Videos subtotal | 18 | 2475 |
| **Total** | **41 jobs (35 as the brief counts them)** | **4115** |

Applying section 4's quote-both rule on the five multi-character shots, Kling std is cheaper than Gemini Omni at every duration (half the price). With Kling on those five shots the videos subtotal is 1925 and the **total is 3565**.

Either total fits inside the 7330 balance. 80 percent of that balance is 5864.

## Per-job cap breaches at 120

As written: style set 160, each character sheet 160, map end frame 160, map video 400, shot 01 350, shot 05 150, shot 06 200, shot 11 250, shot 12 150, shot 13C 150, shot 14 125. Fourteen jobs.

Remedies that stay inside the brief's fixed resolution and durations:
- Run the imageCount 4 jobs as four separate imageCount 1 jobs at 40 each. Same total, same four candidates, every job under cap. Removes six breaches.
- Take Kling over Gemini Omni on the multi-character shots, per the quote-both rule. Removes 06 (100), 12 (75), 13C (75).

Still over cap after both: map 400 (or 320 at Seedance's 4s floor), shot 01 at 175 on Kling, shot 05 at 150, shot 11 at 125, shot 14 at 125. These five need a decision from Jude: raise the cap, or allow the durations to be cut.

## Decisions needed from Jude

1. BUDGET_TOTAL figure.
2. The per-job cap. The map alone cannot run under 320 on Seedance. Suggest raising the cap to 400 for the map only and 175 elsewhere, or agreeing a different figure.
3. Shot 12 at 2s. Suggest running it on Wan image2video at 2s from the keyframe, since it is one figure raising a hand, which is a Wan job on the ladder anyway. Otherwise 3s on Kling and trim in Premiere.
4. Confirm the imageCount split and Kling-first on multi-character shots.
5. cdn.openart.ai egress. Either allow the host for this environment or accept that generated files are logged by historyId and URL and downloaded by Jude.

## Model form notes, for the generation session

- nano-banana-pro image2image: required prompt and visualReferences (type, id, url, label). `autoEnhancePrompt` default false. resolution enum 1K, 2K, 4K.
- wan2-7 image2video: required startFrame. No aspectRatio field, it follows the start frame. `enablePromptExpansion` defaults true, set false to keep prompts literal. resolution 720p or 1080p. duration 2 to 15.
- kling-3-omni image2video: required startFrame and prompt, `generateSound` defaults true so set false, resolution std, `multiShot` false, `shotType` customize. duration 3 to 15.
- kling-3-omni element2video: required visualReferences (max 7) and prompt, `creationMode` "element", aspectRatio 9:16, `generateSound` false.
- gemini-omni-1-1-flash element2video: required visualReferences (max 13), `creationMode` "element", aspectRatio 9:16, resolution 720p, duration 3 to 10. No audio flag on this form.
- byte-plus-seedance-2 image2video: required startFrame, optional endFrame, `generateAudio` defaults true so set false, `mode` normal or fast, `seed` for the up-to-three seed rounds on the map. duration 4 to 15.
- gpt-image-2 image2image: `resolutionTier` 2k, `quality` medium, aspectRatio 9:16.
