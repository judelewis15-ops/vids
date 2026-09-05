import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { COLORS, FONTS, REELS } from "./theme";
import { useBrandFonts } from "./fonts";

export const eyebrowSchema = z.object({ text: z.string(), fadeInAt: z.number() });

// Shot 01 overlay. Transparent background: renders as ProRes 4444 with alpha
// and sits over the portrait. Mono eyebrow top left, fades in at 0:01.
export const Eyebrow: React.FC<z.infer<typeof eyebrowSchema>> = ({ text, fadeInAt }) => {
  useBrandFonts();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const o = interpolate(frame, [fadeInAt * fps, (fadeInAt + 0.6) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const rise = interpolate(o, [0, 1], [10, 0]);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: REELS.safeSide, top: REELS.safeTop, opacity: o, transform: `translateY(${rise}px)`,
                    display: "flex", alignItems: "center", gap: 18 }}>
        <div style={{ width: 28, height: 3, background: COLORS.violet }} />
        <div style={{ fontFamily: FONTS.mono, fontWeight: 500, fontSize: 30, letterSpacing: "0.22em", color: COLORS.cream,
                      textShadow: "0 1px 12px rgba(26,11,46,0.6)" }}>{text}</div>
      </div>
    </AbsoluteFill>
  );
};
