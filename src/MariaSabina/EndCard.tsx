import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { COLORS, FONTS } from "./theme";
import { useBrandFonts } from "./fonts";
import { Grain } from "./Grain";

export const endCardSchema = z.object({ line1: z.string(), line2: z.string() });

// Shot 18. Violet on aubergine. Cuts in from black, settles, holds.
export const EndCard: React.FC<z.infer<typeof endCardSchema>> = ({ line1, line2 }) => {
  useBrandFonts();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = interpolate(frame, [0, 0.35 * fps], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  const spacing = interpolate(p, [0, 1], [0.24, 0.07]);
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.aubergine, justifyContent: "center", alignItems: "center" }}>
      <div style={{ textAlign: "center", color: COLORS.violet, fontFamily: FONTS.heading, lineHeight: 0.9, transform: `scale(${1.03 - 0.03 * p})` }}>
        <div style={{ fontSize: 250, letterSpacing: `${spacing}em`, paddingLeft: `${spacing}em` }}>{line1}</div>
        <div style={{ fontSize: 250, letterSpacing: `${spacing}em`, paddingLeft: `${spacing}em` }}>{line2}</div>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};
