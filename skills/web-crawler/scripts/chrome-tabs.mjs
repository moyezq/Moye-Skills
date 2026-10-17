#!/usr/bin/env node
/**
 * 一条 CDP WebSocket：列用户 Chrome/Edge 的 page 标签并取当前页。
 * 用法：node chrome-tabs.mjs <url-substring>
 * 环境：CHROME_USER_DATA_DIR 覆盖用户数据目录。
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const NEEDLE = process.argv[2];
if (!NEEDLE) {
  console.error("usage: node chrome-tabs.mjs <url-substring>");
  process.exit(2);
}

const HARD_MS = 60000;
const t0 = Date.now();
const userData =
  process.env.CHROME_USER_DATA_DIR ||
  path.join(os.homedir(), "AppData", "Local", "Google", "Chrome", "User Data");
const portFile = path.join(userData, "DevToolsActivePort");

const lines = fs.readFileSync(portFile, "utf8").split(/\r?\n/).filter(Boolean);
if (lines.length < 2) {
  throw new Error("DevToolsActivePort needs two lines: port and WS path");
}
const wsUrl = `ws://127.0.0.1:${lines[0].trim()}${lines[1].trim()}`;

const ws = new WebSocket(wsUrl);
let nextId = 1;
const pending = new Map();

ws.addEventListener("message", (ev) => {
  let msg;
  try {
    msg = JSON.parse(String(ev.data));
  } catch {
    return;
  }
  if (msg.id && pending.has(msg.id)) {
    const { resolve, timer } = pending.get(msg.id);
    pending.delete(msg.id);
    clearTimeout(timer);
    resolve(msg);
  }
});

function send(method, params = {}, sessionId) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    const budget = HARD_MS - (Date.now() - t0);
    if (budget <= 0) {
      reject(new Error("hard 60s deadline before " + method));
      return;
    }
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error("timeout waiting for " + method));
    }, budget);
    pending.set(id, { resolve, timer });
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    ws.send(JSON.stringify(payload));
  });
}

const out = { ws: wsUrl, userData, targets: [], chosen: null, page: null, error: null };

try {
  await new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("WS handshake timeout 60s")), HARD_MS);
    ws.addEventListener("open", () => {
      clearTimeout(t);
      resolve();
    });
    ws.addEventListener("error", () => {
      clearTimeout(t);
      reject(new Error("WS handshake failed"));
    });
  });

  const tg = await send("Target.getTargets");
  if (tg.error) throw new Error(JSON.stringify(tg.error));
  const infos = tg.result.targetInfos || [];
  out.targets = infos.map((t) => ({
    type: t.type,
    url: t.url,
    title: t.title,
    targetId: t.targetId,
  }));

  const pages = infos.filter((t) => t.type === "page" && String(t.url).includes(NEEDLE));
  if (!pages.length) throw new Error("no page target matching " + NEEDLE);
  const page = pages[0];
  out.chosen = { url: page.url, title: page.title, targetId: page.targetId };

  const at = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
  if (at.error) throw new Error(JSON.stringify(at.error));
  const sessionId = at.result.sessionId;

  const ev = await send(
    "Runtime.evaluate",
    {
      expression: `({
        href: location.href,
        title: document.title,
        readyState: document.readyState,
        bodyText: (document.body ? document.body.innerText : "").trim()
      })`,
      returnByValue: true,
    },
    sessionId,
  );
  if (ev.error) throw new Error(JSON.stringify(ev.error));
  out.page = ev.result.result.value;
  await send("Target.detachFromTarget", { sessionId });
} catch (e) {
  out.error = String(e.message || e);
  process.exitCode = 1;
} finally {
  try {
    ws.close();
  } catch {
    /* ignore */
  }
  out.elapsedMs = Date.now() - t0;
  console.log(JSON.stringify(out, null, 2));
}
