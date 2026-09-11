import { readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';

const catalog = JSON.parse(await readFile(join(www, 'catalog.json'), 'utf8'));
const series = JSON.parse(await readFile(join(www, 'data', slug, 'series.json'), 'utf8'));
const fieldCatalog = catalog.filter(item => item.slug === slug);
const fieldMonitor = await readFile(join(here, 'field-monitor.js'), 'utf8');
if(fieldCatalog.length !== 1) throw new Error(`Expected exactly one field catalog item for ${slug}`);

function safeJson(value){
  return JSON.stringify(value).replaceAll('<', '\\u003c');
}

function bootstrapScript({seriesPage=false}={}){
  const monitor = seriesPage ? `<script id="recit-field-monitor">\n${fieldMonitor.replaceAll('</script>', '<\\/script>')}\n</script>\n` : '';
  return `${monitor}<script id="recit-mobile-bootstrap">\n(() => {\n  const catalog = ${safeJson(fieldCatalog)};\n  const series = ${safeJson(series)};\n  window.RECIT_CATALOG_DATA = catalog;\n  window.RECIT_SERIES_DATA = series;\n  window.RECIT_DIAG?.step('Données Séville embarquées', {episodes:Array.isArray(series.episodes)?series.episodes.length:0});\n  const nativeFetch = typeof window.fetch === 'function' ? window.fetch.bind(window) : null;\n  window.fetch = (input, init) => {\n    const raw = typeof input === 'string' ? input : input?.url;\n    let url;\n    try { url = new URL(raw, location.href); } catch (_) { if(nativeFetch) return nativeFetch(input, init); return Promise.reject(new Error('fetch unavailable')); }\n    if (/\\/catalog\\.json$/.test(url.pathname)) {\n      window.RECIT_DIAG?.step('Catalogue local servi', {url:url.href});\n      return Promise.resolve(new Response(JSON.stringify(catalog), {status:200, headers:{'Content-Type':'application/json'}}));\n    }\n    if (url.pathname.endsWith('/data/${slug}/series.json')) {\n      window.RECIT_DIAG?.step('Données série locales servies', {url:url.href});\n      return Promise.resolve(new Response(JSON.stringify(series), {status:200, headers:{'Content-Type':'application/json'}}));\n    }\n    if(nativeFetch) return nativeFetch(input, init);\n    return Promise.reject(new Error('fetch unavailable for '+url.href));\n  };\n})();\n</script>`;
}

async function instrumentMobileApp(){
  const appPath = join(www, 'assets', 'app.js');
  let app = await readFile(appPath, 'utf8');
  const patches = [
    ["  boot();\n", "  window.RECIT_DIAG?.step('app.js exécuté', {slug, href:location.href});\n  boot();\n"],
    ["      const embedded = window.RECIT_SERIES_DATA;\n", "      window.RECIT_DIAG?.step('Lecture des données du guide');\n      const embedded = window.RECIT_SERIES_DATA;\n"],
    ["        series = embedded;\n", "        series = embedded;\n        window.RECIT_DIAG?.step('Données locales acceptées', {episodes:series.episodes.length});\n"],
    ["      render(series);\n      restore(series);\n", "      window.RECIT_DIAG?.step('Construction des épisodes', {episodes:series.episodes.length});\n      render(series);\n      window.RECIT_DIAG?.step('Interface construite', {cards:root.querySelectorAll('[data-episode]').length});\n      restore(series);\n"],
    ["      document.documentElement.dataset.recitSeriesReady = '1';\n", "      document.documentElement.dataset.recitSeriesReady = '1';\n      window.RECIT_DIAG?.ready({episodes:series.episodes.length, playable:series.episodes.filter(isPlayable).length});\n"],
    ["      console.error('Récit series bootstrap failed', e);\n", "      console.error('Récit series bootstrap failed', e);\n      window.RECIT_DIAG?.fail('Bootstrap série en erreur', {message:e?.message||String(e), stack:e?.stack||null});\n"],
    ["    audio.src=e.audio_url;\n", "    window.RECIT_DIAG?.step('Préparation audio', {id:e.id, audio_url:e.audio_url});\n    audio.src=e.audio_url;\n"],
    ["  audio.addEventListener('loadedmetadata',syncPlayerTime);\n", "  audio.addEventListener('loadedmetadata',()=>{window.RECIT_DIAG?.step('Métadonnées audio chargées',{src:audio.currentSrc||audio.src,duration:audio.duration});syncPlayerTime();});\n  audio.addEventListener('error',()=>window.RECIT_DIAG?.fail('Erreur lecteur audio',{src:audio.currentSrc||audio.src,code:audio.error?.code||null,message:audio.error?.message||null}));\n"]
  ];
  for(const [needle, replacement] of patches){
    if(!app.includes(needle)) throw new Error(`Mobile app instrumentation marker not found: ${needle.slice(0,60)}`);
    app = app.replace(needle, replacement);
  }
  await writeFile(appPath, app);
}

async function inject(path, marker, replacementMarker, {seriesPage=false}={}){
  let html = await readFile(path, 'utf8');
  if(!html.includes(marker)) throw new Error(`Bootstrap marker not found in ${path}`);
  html = html.replace(marker, `${bootstrapScript({seriesPage})}\n${replacementMarker ?? marker}`);
  await writeFile(path, html);
}

await instrumentMobileApp();
await inject(join(www, 'index.html'), '<script src="./assets/home.js" defer></script>');
await inject(
  join(www, 's', slug, 'index.html'),
  '<script src="../../assets/app.js" defer></script>',
  '<script src="../../assets/app.js" onload="window.RECIT_DIAG?.step(\'app.js chargé\')" onerror="window.RECIT_DIAG?.fail(\'app.js introuvable\',{src:this.src})"></script>',
  {seriesPage:true}
);
console.log(`Injected deterministic observable mobile bootstrap for ${slug}`);
