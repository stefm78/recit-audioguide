import { readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';

const catalog = JSON.parse(await readFile(join(www, 'catalog.json'), 'utf8'));
const series = JSON.parse(await readFile(join(www, 'data', slug, 'series.json'), 'utf8'));
const fieldCatalog = catalog.filter(item => item.slug === slug);
if(fieldCatalog.length !== 1) throw new Error(`Expected exactly one field catalog item for ${slug}`);

function safeJson(value){
  return JSON.stringify(value).replaceAll('<', '\\u003c');
}

function bootstrapScript(){
  return `<script id="recit-mobile-bootstrap">\n(() => {\n  const catalog = ${safeJson(fieldCatalog)};\n  const series = ${safeJson(series)};\n  window.RECIT_CATALOG_DATA = catalog;\n  window.RECIT_SERIES_DATA = series;\n  const nativeFetch = window.fetch.bind(window);\n  window.fetch = (input, init) => {\n    const raw = typeof input === 'string' ? input : input?.url;\n    let url;\n    try { url = new URL(raw, location.href); } catch (_) { return nativeFetch(input, init); }\n    if (/\\/catalog\\.json$/.test(url.pathname)) {\n      return Promise.resolve(new Response(JSON.stringify(catalog), {status:200, headers:{'Content-Type':'application/json'}}));\n    }\n    if (url.pathname.endsWith('/data/${slug}/series.json')) {\n      return Promise.resolve(new Response(JSON.stringify(series), {status:200, headers:{'Content-Type':'application/json'}}));\n    }\n    return nativeFetch(input, init);\n  };\n})();\n</script>`;
}

const bootstrap = bootstrapScript();

async function inject(path, marker){
  let html = await readFile(path, 'utf8');
  if(!html.includes(marker)) throw new Error(`Bootstrap marker not found in ${path}`);
  html = html.replace(marker, `${bootstrap}\n${marker}`);
  await writeFile(path, html);
}

await inject(join(www, 'index.html'), '<script src="./assets/home.js" defer></script>');
await inject(join(www, 's', slug, 'index.html'), '<script src="../../assets/app.js" defer></script>');
console.log(`Injected deterministic mobile bootstrap for ${slug}`);
