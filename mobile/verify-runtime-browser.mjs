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

    const native = {handlers:{}, metadata:[], playback:[], positions:[]};
    const plugin = {
      async setMetadata(value){native.metadata.push(value);},
      async setPlaybackState(value){native.playback.push(value);},
      async setPositionState(value){native.positions.push(value);},
      async setActionHandler({action},handler){native.handlers[action]=handler;},
      async getPluginVersion(){return {version:'8.0.30-test'};}
    };
    window.__nativeMedia = native;
    window.Capacitor = {getPlatform:()=> 'android', Plugins:{MediaSession:plugin}};

    const mediaProto = window.HTMLMediaElement.prototype;
    Object.defineProperty(mediaProto, 'paused', {configurable:true,get(){return this.__paused!==false;}});
    Object.defineProperty(mediaProto, 'duration', {configurable:true,get(){return 180;}});
    Object.defineProperty(mediaProto, 'currentTime', {configurable:true,get(){return this.__currentTime||0;},set(v){this.__currentTime=Number(v)||0;}});
    Object.defineProperty(mediaProto, 'play', {configurable:true, value(){this.__paused=false;this.dispatchEvent(new window.Event('play'));return Promise.resolve();}});
    Object.defineProperty(mediaProto, 'pause', {configurable:true, value(){this.__paused=true;this.dispatchEvent(new window.Event('pause'));}});
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

const drawer = window.document.getElementById('journey-drawer');
if(!drawer) throw new Error('journey drawer was not rendered');
if(drawer.classList.contains('from-right')) throw new Error('journey drawer unexpectedly exposes a right-side variant');
const journeyItems = [...drawer.querySelectorAll('[data-journey-episode]')];
if(journeyItems.length !== cards.length) throw new Error(`journey drawer mismatch: ${journeyItems.length}/${cards.length}`);
const drawerButton = window.document.querySelector('[data-journey-open]');
if(!drawerButton) throw new Error('journey drawer fallback button missing');
const edgeHint = window.document.querySelector('.journey-edge-hint');
if(!edgeHint) throw new Error('left-edge journey affordance missing');
if(edgeHint.getAttribute('aria-label') !== 'Ouvrir le parcours depuis le bord gauche') throw new Error('left-edge affordance is not self-describing');
edgeHint.click();
if(drawer.getAttribute('aria-hidden') !== 'false') throw new Error('left-edge affordance did not open journey drawer');
if(!edgeHint.hidden) throw new Error('left-edge affordance should hide while drawer is open');
drawer.querySelector('.journey-close')?.click();
if(drawer.getAttribute('aria-hidden') !== 'true') throw new Error('journey drawer did not close');
if(edgeHint.hidden) throw new Error('left-edge affordance did not return after drawer close');
drawerButton.click();
if(drawer.getAttribute('aria-hidden') !== 'false') throw new Error('journey drawer fallback button did not open drawer');
drawer.querySelector('.journey-close')?.click();

const native = window.__nativeMedia;
for(const action of ['play','pause','seekbackward','seekforward','seekto']){
  if(typeof native.handlers[action] !== 'function') throw new Error(`native media action handler missing: ${action}`);
}

const firstPlay = window.document.querySelector('[data-play]');
if(!firstPlay) throw new Error('no playable episode button rendered');
firstPlay.click();
await new Promise(r => setTimeout(r, 25));
const audio = window.document.getElementById('player-audio');
if(!audio?.src) throw new Error('audio src was not assigned after clicking play');
audio.dispatchEvent(new window.Event('loadedmetadata'));
const audioUrl = new URL(audio.src);
if(audioUrl.origin !== 'https://localhost') throw new Error(`audio is not local: ${audio.src}`);
const audioPath = normalize(join(www, decodeURIComponent(audioUrl.pathname)));
if(!audioPath.startsWith(www)) throw new Error('audio path escapes www');
await access(audioPath);
if(!native.metadata.some(x => x?.title)) throw new Error('native media metadata was not populated');
if(!native.playback.some(x => x?.playbackState === 'playing')) throw new Error('native media playback state never reached playing');

const saved = JSON.parse(window.localStorage.getItem(`recit:${slug}`) || 'null');
if(!saved?.episode) throw new Error('journey progress was not persisted after first play');

audio.currentTime=30;
native.handlers.seekforward({action:'seekforward'});
if(audio.currentTime !== 45) throw new Error(`native +15 seek failed: ${audio.currentTime}`);
native.handlers.seekbackward({action:'seekbackward'});
if(audio.currentTime !== 30) throw new Error(`native -15 seek failed: ${audio.currentTime}`);
native.handlers.pause({action:'pause'});
if(!audio.paused) throw new Error('native pause did not pause audio');
native.handlers.play({action:'play'});
await new Promise(r => setTimeout(r, 10));
if(audio.paused) throw new Error('native play did not resume audio');

// Simulate platform audio-focus interruption followed by an unsolicited auto-resume.
audio.pause();
await new Promise(r => setTimeout(r, 1250));
audio.__paused=false;
audio.dispatchEvent(new window.Event('play'));
await new Promise(r => setTimeout(r, 10));
if(!audio.paused) throw new Error('unsolicited post-interruption auto-resume was not blocked');

const snap = window.RECIT_DIAG?.snapshot?.();
if(!snap?.ready) throw new Error('field diagnostics did not observe ready state');
if(errors.some(e => /resource:|console\.error:|jsdom:Could not load script/i.test(e))) throw new Error(`runtime errors: ${errors.join(' | ')}`);
console.log(`Browser runtime PASS: ${cards.length} episodes + ${journeyItems.length} left-only drawer items + discoverable edge handle; Android media play/pause/±15 PASS; interruption latch PASS; audio local ${audioUrl.pathname}`);
dom.window.close();
