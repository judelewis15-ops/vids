// See all configuration options: https://remotion.dev/docs/config
// Each option also is available as a CLI flag: https://remotion.dev/docs/cli

// Note: When using the Node.JS APIs, the config file doesn't apply. Instead, pass options directly to the APIs

import { Config } from "@remotion/cli/config";
import { enableTailwind } from "@remotion/tailwind-v4";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.overrideWebpackConfig((current) => {
  const withTailwind = enableTailwind(current);
  // webpack's wasm md4 hash crashes intermittently on Node 22 ("reading 'length'");
  // a Node-crypto hash sidesteps it.
  return { ...withTailwind, output: { ...(withTailwind.output ?? {}), hashFunction: "sha256" } };
});
