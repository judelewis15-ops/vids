import { Composition } from "remotion";
import { REELS } from "./theme";
import { DateCard, dateCardSchema } from "./DateCard";
import { EndCard, endCardSchema } from "./EndCard";
import { Eyebrow, eyebrowSchema } from "./Eyebrow";
import { LowerThird, lowerThirdSchema } from "./LowerThird";

const base = { width: REELS.width, height: REELS.height, fps: REELS.fps };
const secs = (s: number) => Math.round(s * REELS.fps);

// HYPHA ORIGINS · 01 — text assets, all 1080x1920 at 60 fps.
export const MariaSabinaCompositions: React.FC = () => (
  <>
    <Composition id="HO01-01-TXT-eyebrow" component={Eyebrow} schema={eyebrowSchema} {...base}
      durationInFrames={secs(7)} defaultProps={{ text: "HYPHA ORIGINS · 01", fadeInAt: 1 }} />
    <Composition id="HO01-08-TXT-date-card" component={DateCard} schema={dateCardSchema} {...base}
      durationInFrames={secs(2)} defaultProps={{ line1: "13 MAY", line2: "1957" }} />
    <Composition id="HO01-17-TXT-lower-third" component={LowerThird} schema={lowerThirdSchema} {...base}
      durationInFrames={secs(5)} defaultProps={{ text: "MAZATECA", inAt: 2 }} />
    <Composition id="HO01-18-TXT-end-card" component={EndCard} schema={endCardSchema} {...base}
      durationInFrames={secs(2)} defaultProps={{ line1: "HYPHA", line2: "ORIGINS" }} />
  </>
);
