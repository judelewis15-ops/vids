import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { COLORS, FONTS } from "./theme";
import { useBrandFonts } from "./fonts";
import { Grain } from "./Grain";

export const dateCardSchema = z.object({ line1: z.string(), line2: z.string() });

// Shot 08. Hard cut in from the cover slam: the date lands with a fast tracking
// tighten and a scale settle, the violet rule wipes in, then it holds.
export const DateCard: React.FC<z.infer<typeof dateCardSchema>> = ({ line1, line2 }) => {
  useBrandFonts();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = interpolate(frame, [0, 0.3 * fps], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  const spacing = interpolate(p, [0, 1], [0.34, 0.08]);
  const scale = interpolate(p, [0, 1], [1.05, 1]);
  const rule = interpolate(frame, [0.12 * fps, 0.55 * fps], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.aubergine, justifyContent: "center", alignItems: "center" }}>
      <div style={{ transform: `scale(${scale})`, textAlign: "center", color: COLORS.cream, fontFamily: FONTS.heading, lineHeight: 0.9 }}>
        <div style={{ fontSize: 230, letterSpacing: `${spacing}em`, paddingLeft: `${spacing}em` }}>{line1}</div>
        <div style={{ fontSize: 360, letterSpacing: `${spacing * 0.9}em`, paddingLeft: `${spacing * 0.9}em`, marginTop: 8 }}>{line2}</div>
      </div>
      <div style={{ width: 140 * rule, height: 5, background: COLORS.violet, marginTop: 48 }} />
      <Grain />
    </AbsoluteFill>
  );
};
