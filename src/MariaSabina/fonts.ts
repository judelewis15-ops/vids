import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

const cache = new Map<string, Promise<FontFace>>();
const load = (family: string, file: string) => {
  const key = `${family}:${file}`;
  if (!cache.has(key)) {
    const face = new FontFace(family, `url(${staticFile(file)})`);
    cache.set(key, face.load().then((f) => { document.fonts.add(f); return f; }));
  }
  return cache.get(key)!;
};

// Bebas Neue and JetBrains Mono live in public/fonts (both OFL).
export const useBrandFonts = () => {
  const [handle] = useState(() => delayRender("brand fonts"));
  useEffect(() => {
    Promise.all([
      load("Bebas Neue", "fonts/BebasNeue-Regular.ttf"),
      load("JetBrains Mono", "fonts/JetBrainsMono-VF.ttf"),
    ]).then(() => continueRender(handle), () => continueRender(handle));
  }, [handle]);
};
