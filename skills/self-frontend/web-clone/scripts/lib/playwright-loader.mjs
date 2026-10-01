import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

export function loadPlaywright() {
  try {
    return require("playwright");
  } catch {
    throw new Error(
      "Playwright not found. In the clone project run: npm install -D playwright"
    );
  }
}

export async function launchChromium(chromium) {
  try {
    return await chromium.launch({ headless: true });
  } catch (firstError) {
    try {
      return await chromium.launch({ headless: true, channel: "chrome" });
    } catch {
      throw firstError;
    }
  }
}
