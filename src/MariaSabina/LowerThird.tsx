import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { COLORS, FONTS, REELS } from "./theme";
import { useBrandFonts } from "./fonts";

export const lowerThirdSchema = z.object({ text: z.string(), inAt: z.number() });

// Shot 17 overlay. Transparent background. Mono lower third with a violet rule
// that draws in; appears at `inAt` seconds into the shot (0:57 = 2 s in).
export const LowerThird: React.FC<z.infer<typeof lowerThirdSchema>> = ({ text, inAt }) => {
  useBrandFonts();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = interpolate(frame, [inAt * fps, (inAt + 0.5) * fps], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: REELS.safeSide, bottom: REELS.safeBottom + 60 }}>
        <div style={{ width: 220 * p, height: 3, background: COLORS.violet, marginBottom: 18 }} />
        <div style={{ opacity: p, transform: `translateY(${(1 - p) * 12}px)`, fontFamily: FONTS.mono, fontWeight: 500,
                      fontSize: 40, letterSpacing: "0.28em", color: COLORS.cream, textShadow: "0 1px 12px rgba(26,11,46,0.6)" }}>{text}</div>
      </div>
    </AbsoluteFill>
  );
};
