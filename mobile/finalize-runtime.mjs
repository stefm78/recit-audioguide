import { access, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';

const catalog = JSON.parse(await readFile(join(www, 'catalog.json'), 'utf8'));
const series = JSON.parse(await readFile(join(www, 'data', slug, 'series.json'), 'utf8'));
const fieldMonitor = await readFile(join(here, 'field-monitor.js'), 'utf8');
const qualifiedItem = catalog.find(item => item.slug === slug);
if(!qualifiedItem) throw new Error(`Qualified field guide missing from catalog: ${slug}`);
for(const item of catalog){
  await access(join(www, 's', item.slug, 'index.html'));
  await access(join(www, 'data', item.slug, 'series.json'));
}

const runNumber = process.env.GITHUB_RUN_NUMBER || 'local';
const buildSha = process.env.GITHUB_SHA || 'local';
const shortSha = buildSha === 'local' ? 'local' : buildSha.slice(0, 8);
const buildVersion = `0.4.${runNumber}`;
const build = {
  schema: 'recit.android.field-build.v1',
  channel: 'FIELD',
  version: buildVersion,
  run: runNumber,
  sha: buildSha,
  short_sha: shortSha,
  package: 'com.stefm78.recitaudioguide.field',
  slug,
  catalog_count: catalog.length,
  content_mode: 'packaged-catalog-seville-field-qualified'
};

function safeJson(value){
  return JSON.stringify(value).replaceAll('<', '\\u003c');
}

function identityHtml(){
  return `<aside id="recit-field-build" role="status" aria-label="Identité du build terrain" style="position:relative;z-index:2147483647;margin:0;padding:9px 12px;background:#111;color:#fff;font:700 12px/1.35 system-ui,-apple-system,sans-serif;letter-spacing:.02em"><div>FIELD BUILD ${buildVersion} · ${shortSha}</div><div style="font-weight:500;opacity:.82">${build.package} · ${catalog.length} parcours packagés · Séville qualifiée · run ${runNumber}</div></aside>`;
}

function buildIdentityScript(){
  return `<script id="recit-field-build-data">window.RECIT_FIELD_BUILD=${safeJson(build)};</script>`;
}

function bootstrapScript({seriesPage=false, embedQualifiedSeries=false}={}){
  const monitor = seriesPage ? `<script id="recit-field-monitor">\n${fieldMonitor.replaceAll('</script>', '<\\/script>')}\n</script>\n` : '';
  const embeddedSeries = embedQualifiedSeries
    ? `\n  const qualifiedSeries = ${safeJson(series)};\n  window.RECIT_SERIES_DATA = qualifiedSeries;\n  window.RECIT_DIAG?.step('Données Séville embarquées', {episodes:Array.isArray(qualifiedSeries.episodes)?qualifiedSeries.episodes.length:0, build:window.RECIT_FIELD_BUILD});`
    : '';
  const seriesFetch = embedQualifiedSeries
    ? `\n    if (url.pathname.endsWith('/data/${slug}/series.json')) {\n      window.RECIT_DIAG?.step('Données série locales servies', {url:url.href});\n      return Promise.resolve(new Response(JSON.stringify(qualifiedSeries), {status:200, headers:{'Content-Type':'application/json'}}));\n    }`
    : '';
  return `${buildIdentityScript()}\n${monitor}<script id="recit-mobile-bootstrap">\n(() => {\n  const catalog = ${safeJson(catalog)};\n  window.RECIT_CATALOG_DATA = catalog;${embeddedSeries}\n  const nativeFetch = typeof window.fetch === 'function' ? window.fetch.bind(window) : null;\n  window.fetch = (input, init) => {\n    const raw = typeof input === 'string' ? input : input?.url;\n    let url;\n    try { url = new URL(raw, location.href); } catch (_) { if(nativeFetch) return nativeFetch(input, init); return Promise.reject(new Error('fetch unavailable')); }\n    if (/\\/catalog\\.json$/.test(url.pathname)) {\n      window.RECIT_DIAG?.step('Catalogue local servi', {url:url.href, count:catalog.length});\n      return Promise.resolve(new Response(JSON.stringify(catalog), {status:200, headers:{'Content-Type':'application/json'}}));\n    }${seriesFetch}\n    if(nativeFetch) return nativeFetch(input, init);\n    return Promise.reject(new Error('fetch unavailable for '+url.href));\n  };\n})();\n</script>`;
}

async function instrumentMobileApp(){
  const appPath = join(www, 'assets', 'app.js');
  let app = await readFile(appPath, 'utf8');
  const patches = [
    ["  boot();\n", "  window.RECIT_DIAG?.step('app.js exécuté', {slug, href:location.href});\n  boot();\n"],
    ["      const embedded = window.RECIT_SERIES_DATA;\n", "      window.RECIT_DIAG?.step('Lecture des données du guide');\n      const embedded = window.RECIT_SERIES_DATA;\n"],
    ["        series = embedded;\n", "        series = embedded;\n        window.RECIT_DIAG?.step('Données locales acceptées', {episodes:series.episodes.length});\n"],
    ["      render(series);\n      restore(series);\n", "      window.RECIT_DIAG?.step('Construction des épisodes', {episodes:series.episodes.length});\n      render(series);\n      window.RECIT_DIAG?.step('Interface construite', {cards:root.querySelectorAll('[data-episode]').length});\n      restore(series);\n"],
    ["      document.documentElement.dataset.recitSeriesReady = '1';\n", "      document.documentElement.dataset.recitSeriesReady = '1';\n      window.RECIT_DIAG?.ready({episodes:series.episodes.length, playable:series.episodes.filter(isPlayable).length, build:window.RECIT_FIELD_BUILD});\n"],
    ["      console.error('Récit series bootstrap failed', e);\n", "      console.error('Récit series bootstrap failed', e);\n      window.RECIT_DIAG?.fail('Bootstrap série en erreur', {message:e?.message||String(e), stack:e?.stack||null, build:window.RECIT_FIELD_BUILD});\n"],
    ["    audio.src=e.audio_url;\n", "    window.RECIT_DIAG?.step('Préparation audio', {id:e.id, audio_url:e.audio_url});\n    audio.src=e.audio_url;\n"],
    ["  audio.addEventListener('loadedmetadata',syncPlayerTime);\n", "  audio.addEventListener('loadedmetadata',()=>{window.RECIT_DIAG?.step('Métadonnées audio chargées',{src:audio.currentSrc||audio.src,duration:audio.duration});syncPlayerTime();});\n  audio.addEventListener('error',()=>window.RECIT_DIAG?.fail('Erreur lecteur audio',{src:audio.currentSrc||audio.src,code:audio.error?.code||null,message:audio.error?.message||null}));\n"]
  ];
  for(const [needle, replacement] of patches){
    if(!app.includes(needle)) throw new Error(`Mobile app instrumentation marker not found: ${needle.slice(0,60)}`);
    app = app.replace(needle, replacement);
  }
  await writeFile(appPath, app);
}

function modeLabel(type){
  return ({story:'Histoire',visit:'Visite',route:'Route'})[type] || 'Récit';
}

function availabilityLabel(item){
  if(item.slug === slug) return ' · qualifié terrain';
  if(item.state === 'blocked') return ' · indisponible';
  if(item.state === 'degraded') return ' · partiel';
  return '';
}

async function hardenHome(){
  const path = join(www, 'index.html');
  let html = await readFile(path, 'utf8');
  const loading = '<div id="catalog" class="catalog" aria-live="polite"><p>Chargement…</p></div>';
  if(!html.includes(loading)) throw new Error('Field home loading marker not found');
  const cards = catalog.map(item => {
    const id = item.slug === slug ? ' id="recit-field-seville-launch"' : '';
    const count = `${item.episode_count} épisode${item.episode_count > 1 ? 's' : ''}`;
    return `<a${id} class="catalog-card" href="./s/${escapeHtml(item.slug)}/index.html"><span class="mode">${modeLabel(item.type)}</span><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.subtitle || '')}</span><small>${count}${availabilityLabel(item)}</small></a>`;
  }).join('');
  const staticCatalog = `<div id="catalog" class="catalog" aria-live="polite">${cards}</div>`;
  html = html.replace(loading, staticCatalog);
  html = html.replace('  <script src="./assets/home.js" defer></script>\n', '');
  html = html.replace('<body>', `<body>\n  ${identityHtml()}\n  ${bootstrapScript()}`);
  await writeFile(path, html);
}

async function hardenSeriesPages(){
  const marker = '<script src="../../assets/app.js" defer></script>';
  for(const item of catalog){
    const path = join(www, 's', item.slug, 'index.html');
    let html = await readFile(path, 'utf8');
    if(!html.includes(marker)) throw new Error(`Series app marker not found in ${path}`);
    html = html.replace('<body>', `<body>\n  ${identityHtml()}`);
    if(item.slug === slug){
      html = html.replace(marker, `${bootstrapScript({seriesPage:true, embedQualifiedSeries:true})}\n<script src="../../assets/app.js" onload="window.RECIT_DIAG?.step('app.js chargé')" onerror="window.RECIT_DIAG?.fail('app.js introuvable',{src:this.src})"></script>`);
    }else{
      html = html.replace(marker, `${bootstrapScript()}\n${marker}`);
    }
    await writeFile(path, html);
  }
}

function escapeHtml(value){
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

await instrumentMobileApp();
await hardenHome();
await hardenSeriesPages();
console.log(`Hardened FIELD ${buildVersion} ${shortSha}: ${catalog.length} packaged guides + Seville qualified runtime`);
