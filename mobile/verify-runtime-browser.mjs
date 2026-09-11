import { readFile, access } from 'node:fs/promises';
import { join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { JSDOM, ResourceLoader, VirtualConsole } from 'jsdom';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';
const pagePath = join(www, 's', slug, 'index.html');
const html = await readFile(pagePath, 'utf8');
const errors = [];

class LocalResourceLoader extends ResourceLoader {
  async fetch(url, options){
    const u = new URL(url);
    if(u.origin !== 'https://localhost') return null;
    const local = normalize(join(www, decodeURIComponent(u.pathname)));
    if(!local.startsWith(www)) throw new Error(`resource escapes www: ${url}`);
    try { return Buffer.from(await readFile(local)); }
    catch (e) { errors.push(`resource:${url}:${e.message}`); return null; }
  }
}

const vc = new VirtualConsole();
vc.on('jsdomError', e => errors.push(`jsdom:${e.message}`));
vc.on('error', (...args) => errors.push(`console.error:${args.map(String).join(' ')}`));

const dom = new JSDOM(html, {
  url: `https://localhost/s/${slug}/`,
  runScripts: 'dangerously',
  resources: new LocalResourceLoader(),
  pretendToBeVisual: true,
  virtualConsole: vc,
  beforeParse(window){
    window.Response = globalThis.Response;
    window.Headers = globalThis.Headers;
    window.Request = globalThis.Request;
    window.fetch = async input => {
      const raw = typeof input === 'string' ? input : input?.url;
      const u = new URL(raw, window.location.href);
      if(u.origin !== 'https://localhost') throw new Error(`network forbidden in field runtime gate: ${u.href}`);
      const local = normalize(join(www, decodeURIComponent(u.pathname)));
      if(!local.startsWith(www)) throw new Error(`fetch escapes www: ${u.href}`);
      const body = await readFile(local);
      return new globalThis.Response(body, {status:200});
    };
    Object.defineProperty(window.HTMLMediaElement.prototype, 'play', {configurable:true, value(){ this.dispatchEvent(new window.Event('play')); return Promise.resolve(); }});
    Object.defineProperty(window.HTMLMediaElement.prototype, 'pause', {configurable:true, value(){ this.dispatchEvent(new window.Event('pause')); }});
  }
});

const {window} = dom;
const waitUntil = async (predicate, timeoutMs=5000) => {
  const start = Date.now();
  while(Date.now()-start < timeoutMs){
    if(predicate()) return;
    await new Promise(r => setTimeout(r, 25));
  }
  throw new Error(`timeout after ${timeoutMs}ms`);
};

await waitUntil(() => window.document.documentElement.dataset.recitSeriesReady === '1');
const cards = [...window.document.querySelectorAll('[data-episode]')];
if(cards.length < 10) throw new Error(`expected >=10 rendered episodes, got ${cards.length}`);
if(window.document.querySelector('.loading')) throw new Error('permanent loading marker remains after ready');
const firstPlay = window.document.querySelector('[data-play]');
if(!firstPlay) throw new Error('no playable episode button rendered');
firstPlay.click();
await new Promise(r => setTimeout(r, 25));
const audio = window.document.getElementById('player-audio');
if(!audio?.src) throw new Error('audio src was not assigned after clicking play');
const audioUrl = new URL(audio.src);
if(audioUrl.origin !== 'https://localhost') throw new Error(`audio is not local: ${audio.src}`);
const audioPath = normalize(join(www, decodeURIComponent(audioUrl.pathname)));
if(!audioPath.startsWith(www)) throw new Error('audio path escapes www');
await access(audioPath);
const snap = window.RECIT_DIAG?.snapshot?.();
if(!snap?.ready) throw new Error('field diagnostics did not observe ready state');
if(errors.some(e => /resource:|console\.error:|jsdom:Could not load script/i.test(e))) throw new Error(`runtime errors: ${errors.join(' | ')}`);
console.log(`Browser runtime PASS: ${cards.length} episodes rendered; audio resolved locally to ${audioUrl.pathname}; diagnostic events=${snap.events.length}`);
dom.window.close();
