import React from "react";
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ---- edit.json shape (written by pipeline/cut.py) -----------------------------
export type Word = { w: string; s: number; e: number };
export type Segment = {
  id: number;
  start: number; // seconds in source proxy
  end: number;
  t0?: number;
  line?: number | null;
  text?: string;
  words?: Word[];
};
export type Broll = {
  src: string; // path under public/ or an https URL
  segment: number; // take id it sits on
  offset: number; // seconds into that take
  duration: number;
  mode?: "cutaway" | "split";
  kind?: "video" | "image";
  label?: string;
};
export type Edit = {
  fps: number;
  width: number;
  height: number;
  source: string;
  focus?: { x: number; y: number };
  punchIn?: number;
  captions?: boolean;
  segments: Segment[];
  broll: Broll[];
};

export const emptyEdit: Edit = {
  fps: 30,
  width: 1080,
  height: 1920,
  source: "",
  segments: [],
  broll: [],
};

export const segmentFrames = (seg: Segment, fps: number) =>
  Math.max(1, Math.round((seg.end - seg.start) * fps));

export const editDurationInFrames = (edit: Edit, fps: number) =>
  edit.segments.length
    ? edit.segments.reduce((n, s) => n + segmentFrames(s, fps), 0)
    : Math.round(3 * fps);

export const loadEdit = async (): Promise<Edit> => {
  try {
    const res = await fetch(staticFile("edit/edit.json"));
    if (!res.ok) return emptyEdit;
    return (await res.json()) as Edit;
  } catch {
    return emptyEdit;
  }
};

const resolveSrc = (src: string) =>
  /^https?:\/\//.test(src) ? src : staticFile(src);

type Placed = { seg: Segment; from: number; dur: number; index: number };

const placeSegments = (edit: Edit, fps: number): Placed[] => {
  let cursor = 0;
  return edit.segments.map((seg, index) => {
    const dur = segmentFrames(seg, fps);
    const p = { seg, from: cursor, dur, index };
    cursor += dur;
    return p;
  });
};

const cover: React.CSSProperties = {
  width: "100%",
  height: "100%",
  objectFit: "cover",
};

// ---- layers --------------------------------------------------------------------
const TalkingHead: React.FC<{
  src: string;
  startFrom: number;
  focus: { x: number; y: number };
  zoom: number;
  muted?: boolean;
}> = ({ src, startFrom, focus, zoom, muted }) => (
  <OffthreadVideo
    src={src}
    startFrom={startFrom}
    muted={muted}
    style={{
      ...cover,
      objectPosition: `${focus.x}% ${focus.y}%`,
      transform: `scale(${zoom})`,
      transformOrigin: `${focus.x}% ${focus.y}%`,
    }}
  />
);

const BrollLayer: React.FC<{
  b: Broll;
  thSrc: string;
  thStartFrom: number;
  focus: { x: number; y: number };
}> = ({ b, thSrc, thStartFrom, focus }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = Math.min(6, Math.floor(durationInFrames / 3));
  const opacity = interpolate(
    frame,
    [0, fade, durationInFrames - fade, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const media =
    b.kind === "image" ? (
      <Img src={resolveSrc(b.src)} style={cover} />
    ) : (
      <OffthreadVideo src={resolveSrc(b.src)} muted style={cover} />
    );
  if (b.mode === "split") {
    return (
      <AbsoluteFill style={{ opacity, backgroundColor: "#1A0B2E" }}>
        <div style={{ position: "absolute", left: 0, top: 0, width: "100%", height: "56%", overflow: "hidden" }}>
          {media}
        </div>
        <div style={{ position: "absolute", left: 0, top: "56%", width: "100%", height: "44%", overflow: "hidden" }}>
          <TalkingHead src={thSrc} startFrom={thStartFrom} focus={focus} zoom={1} muted />
        </div>
      </AbsoluteFill>
    );
  }
  return <AbsoluteFill style={{ opacity, backgroundColor: "#1A0B2E" }}>{media}</AbsoluteFill>;
};

// ---- captions (word-timed, kept inside the Reels safe zone) --------------------
type CWord = { w: string; from: number; to: number };
type Chunk = { from: number; to: number; words: CWord[] };

const buildChunks = (placed: Placed[], fps: number): Chunk[] => {
  const chunks: Chunk[] = [];
  for (const p of placed) {
    const ws: CWord[] = (p.seg.words ?? [])
      .map((w) => ({
        w: w.w,
        from: p.from + Math.round((w.s - p.seg.start) * fps),
        to: p.from + Math.round((w.e - p.seg.start) * fps),
      }))
      .filter((w) => w.to > p.from && w.from < p.from + p.dur)
      .map((w) => ({ ...w, from: Math.max(w.from, p.from), to: Math.min(w.to, p.from + p.dur) }));
    let cur: Chunk | null = null;
    for (const w of ws) {
      const gap = cur ? w.from - cur.to > 0.6 * fps : false;
      const full = cur ? cur.words.length >= 3 || w.to - cur.from > 1.6 * fps : false;
      if (!cur || gap || full) {
        if (cur) chunks.push(cur);
        cur = { from: w.from, to: w.to, words: [w] };
      } else {
        cur.words.push(w);
        cur.to = w.to;
      }
    }
    if (cur) chunks.push(cur);
  }
  for (let i = 0; i < chunks.length; i++) {
    const next = chunks[i + 1];
    const limit = chunks[i].to + Math.round(0.5 * fps);
    chunks[i].to = next ? Math.min(next.from, limit) : limit;
  }
  return chunks;
};

const Captions: React.FC<{ chunks: Chunk[] }> = ({ chunks }) => {
  const frame = useCurrentFrame();
  const chunk = chunks.find((c) => frame >= c.from && frame < c.to);
  if (!chunk) return null;
  let active = -1;
  chunk.words.forEach((w, i) => {
    if (frame >= w.from) active = i;
  });
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top: 1340,
        textAlign: "center",
        fontFamily: "Inter, Arial, Helvetica, sans-serif",
        fontSize: 68,
        fontWeight: 800,
        lineHeight: 1.15,
        color: "#FAF7F2",
        WebkitTextStroke: "10px #000",
        paintOrder: "stroke fill",
        textShadow: "0 4px 12px rgba(0,0,0,0.6)",
      }}
    >
      {chunk.words.map((w, i) => (
        <span key={i} style={{ color: i === active ? "#B79CF5" : "#FAF7F2", marginRight: 18 }}>
          {w.w}
        </span>
      ))}
    </div>
  );
};

const Placeholder: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: "#1A0B2E",
      color: "#FAF7F2",
      justifyContent: "center",
      alignItems: "center",
      fontFamily: "Inter, Arial, Helvetica, sans-serif",
      fontSize: 48,
      padding: 80,
      textAlign: "center",
    }}
  >
    No public/edit/edit.json yet. Run pipeline/cut.py on your footage.
  </AbsoluteFill>
);

// ---- composition ---------------------------------------------------------------
export const Reel: React.FC<{ edit: Edit }> = ({ edit }) => {
  const { fps } = useVideoConfig();
  const focus = edit.focus ?? { x: 50, y: 40 };
  const placed = placeSegments(edit, fps);
  if (!edit.source || placed.length === 0) return <Placeholder />;
  const src = resolveSrc(edit.source);
  const chunks = edit.captions === false ? [] : buildChunks(placed, fps);
  const punch = edit.punchIn ?? 0.08;
  return (
    <AbsoluteFill style={{ backgroundColor: "#1A0B2E" }}>
      {placed.map((p) => (
        <Sequence key={p.seg.id} from={p.from} durationInFrames={p.dur} name={`take ${p.seg.id}`}>
          <TalkingHead
            src={src}
            startFrom={Math.round(p.seg.start * fps)}
            focus={focus}
            zoom={1 + (p.index % 2) * punch}
          />
        </Sequence>
      ))}
      {edit.broll.map((b, k) => {
        const p = placed.find((x) => x.seg.id === b.segment);
        if (!p) return null;
        const off = Math.round(b.offset * fps);
        const dur = Math.min(Math.round(b.duration * fps), p.dur - off);
        if (dur <= 0) return null;
        return (
          <Sequence key={`broll-${k}`} from={p.from + off} durationInFrames={dur} name={b.label || b.src}>
            <BrollLayer b={b} thSrc={src} thStartFrom={Math.round(p.seg.start * fps) + off} focus={focus} />
          </Sequence>
        );
      })}
      {chunks.length > 0 && <Captions chunks={chunks} />}
    </AbsoluteFill>
  );
};
