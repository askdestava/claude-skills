#!/usr/bin/env node
// Render a one-clock HTML film, frame by frame, with headless Chrome.
//
//   node render.js <page.html> stills 0.5,3.2,7      → <page dir>/stills/t_<s>.png
//   node render.js <page.html> video out.mp4         → H.264 MP4 at --fps (default 60), piped into ffmpeg
//   node render.js <page.html> timeline [out.json]   → window.TIMELINE (+ DURATION) as JSON, for splice/mix cue maths
//   node render.js <page.html> png out.png [--at 0]  → one frame with a transparent background (captions, overlays)
//
// Options: --size 1920x1080 (output pixels)  --scale 2 (CSS px = output / scale, so 960×540 CSS at the default)
//          --fps 60  --query "line=Hello&x=1" (appended to the page URL)  --crf 16
//
// Page contract: window.DURATION in seconds (needed for `video`); optional window.TIMELINE (an object of cue
// times); optional window.__setup() (sync or async, runs once after fonts load); optional window.seek(ms).
// Without window.seek, every document animation (CSS animations and transitions, element.animate()) is paused
// and set to currentTime = ms, so anything scheduled with a delay on the page's one clock lands exactly.
const puppeteer = require('puppeteer-core');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf('--' + name);
  if (i === -1) return fallback;
  const v = args[i + 1]; args.splice(i, 2); return v;
};
const [W, H] = opt('size', '1920x1080').split('x').map(Number);
const SCALE = Number(opt('scale', '2'));
const FPS = Number(opt('fps', '60'));
const QUERY = opt('query', '');
const CRF = opt('crf', '16');
const AT = Number(opt('at', '0'));
const [page, mode, arg] = args;
if (!page || !['stills', 'video', 'timeline', 'png'].includes(mode)) {
  console.error('usage: node render.js <page.html> stills|video|timeline|png [arg] [--size WxH --scale N --fps N --query q --at s]');
  process.exit(2);
}

function chrome() {
  const candidates = [process.env.CHROME_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'];
  const found = candidates.find((p) => p && fs.existsSync(p));
  if (!found) throw new Error('no Chrome found: set CHROME_PATH to a Chrome or Chromium binary');
  return found;
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: chrome(), headless: true,
    args: ['--hide-scrollbars', '--force-color-profile=srgb', '--font-render-hinting=none'],
  });
  const tab = await browser.newPage();
  await tab.setViewport({ width: Math.round(W / SCALE), height: Math.round(H / SCALE), deviceScaleFactor: SCALE });
  const file = path.resolve(page);
  await tab.goto('file://' + file + (QUERY ? '?' + QUERY : ''), { waitUntil: 'networkidle0' });

  // Load every declared font face now. Text that first appears late in the film would otherwise load its font
  // mid-render and the first frames would show a fallback face.
  const fonts = await tab.evaluate(async () => {
    await Promise.all([...document.fonts].map((f) => f.load().catch(() => null)));
    await document.fonts.ready;
    return [...new Set([...document.fonts].filter((f) => f.status !== 'loaded').map((f) => f.family))];
  });
  if (fonts.length) console.error('warning: fonts not loaded (offline?):', fonts.join(', '));
  await tab.evaluate(async () => { if (typeof window.__setup === 'function') await window.__setup(); });

  const shoot = async (t, transparent = false) => {
    await tab.evaluate((ms) => {
      if (typeof window.seek === 'function') return window.seek(ms);
      document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; });
    }, t * 1000);
    await tab.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    return tab.screenshot({ type: 'png', omitBackground: transparent });
  };

  if (mode === 'timeline') {
    const tl = await tab.evaluate(() => ({ ...(window.TIMELINE || {}), DURATION: window.DURATION }));
    const out = arg || path.join(path.dirname(file), 'timeline.json');
    fs.writeFileSync(out, JSON.stringify(tl, null, 1) + '\n');
    console.error('wrote', out, JSON.stringify(tl));
  } else if (mode === 'stills') {
    const dir = path.join(path.dirname(file), 'stills');
    fs.mkdirSync(dir, { recursive: true });
    for (const t of (arg || '0').split(',').map(Number)) {
      const out = path.join(dir, `t_${t.toFixed(2)}.png`);
      fs.writeFileSync(out, await shoot(t));
      console.error('wrote', out);
    }
  } else if (mode === 'png') {
    const out = arg || path.join(path.dirname(file), path.basename(file, '.html') + '.png');
    fs.writeFileSync(out, await shoot(AT, true));
    console.error('wrote', out);
  } else {
    const DURATION = await tab.evaluate(() => window.DURATION);
    if (!(DURATION > 0)) throw new Error('the page must set window.DURATION (seconds) to render a video');
    const out = arg || path.join(path.dirname(file), path.basename(file, '.html') + '.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', CRF, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round(DURATION * FPS);
    for (let i = 0; i < n; i++) {
      const buf = await shoot(i / FPS);
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % (FPS * 2) === 0) console.error(`frame ${i}/${n}`);
    }
    ff.stdin.end();
    const code = await new Promise((r) => ff.on('close', r));
    if (code !== 0) throw new Error(`ffmpeg exited ${code}`);
    console.error(`wrote ${out} (${n} frames, ${DURATION}s at ${FPS}fps)`);
  }
  await browser.close();
})().catch((e) => { console.error('error:', e.message); process.exit(1); });
