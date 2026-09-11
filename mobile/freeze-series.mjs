import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';
const base = new URL(process.env.RECIT_PUBLIC_BASE || 'https://stefm78.github.io/recit-audioguide/');
const seriesUrl = new URL(`data/${encodeURIComponent(slug)}/series.json`, base);
const catalogUrl = new URL('catalog.json', base);
const downloaded = new Map();

async function fetchBytes(url){
  const r = await fetch(url, { redirect: 'follow' });
  if(!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
  return Buffer.from(await r.arrayBuffer());
}

function localPathFor(url){
  const u = new URL(url);
  if(u.origin !== base.origin || !u.pathname.startsWith(base.pathname)) return null;
  const rel = decodeURIComponent(u.pathname.slice(base.pathname.length));
  if(!rel || rel.includes('..')) return null;
  return join(www, rel);
}

async function saveUrl(url){
  const key = String(url);
  if(downloaded.has(key)) return downloaded.get(key);
  const target = localPathFor(url);
  if(!target) return null;
  const bytes = await fetchBytes(url);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, bytes);
  const item = {
    url: key,
    path: target.slice(www.length + 1).replaceAll('\\', '/'),
    bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex')
  };
  downloaded.set(key, item);
  return item;
}

function looksLikeReference(value){
  return /^(https?:|\.\.?\/|\/)/i.test(value);
}
function collectInternalUrls(value, originUrl, out = new Set()){
  if(Array.isArray(value)) value.forEach(v => collectInternalUrls(v, originUrl, out));
  else if(value && typeof value === 'object') Object.values(value).forEach(v => collectInternalUrls(v, originUrl, out));
  else if(typeof value === 'string' && looksLikeReference(value)){
    try {
      const u = new URL(value, originUrl);
      if(u.origin === base.origin && u.pathname.startsWith(base.pathname)) out.add(String(u));
    } catch(_) {}
  }
  return out;
}

await saveUrl(catalogUrl);
const seriesBytes = await fetchBytes(seriesUrl);
const series = JSON.parse(seriesBytes.toString('utf8'));
await mkdir(dirname(localPathFor(seriesUrl)), { recursive: true });
await writeFile(localPathFor(seriesUrl), seriesBytes);
downloaded.set(String(seriesUrl), {
  url: String(seriesUrl),
  path: localPathFor(seriesUrl).slice(www.length + 1).replaceAll('\\', '/'),
  bytes: seriesBytes.length,
  sha256: createHash('sha256').update(seriesBytes).digest('hex')
});

const refs = [...collectInternalUrls(series, seriesUrl)];
for(const ref of refs){
  if(ref === String(seriesUrl)) continue;
  await saveUrl(ref);
}

const files = [...downloaded.values()].sort((a,b)=>a.path.localeCompare(b.path));
const manifest = {
  schema: 'recit.mobile.offline-package.v1',
  slug,
  source: String(seriesUrl),
  generated_at: new Date().toISOString(),
  file_count: files.length,
  total_bytes: files.reduce((n,f)=>n+f.bytes,0),
  files
};
const manifestPath = join(www, 'offline', slug, 'package-manifest.json');
await mkdir(dirname(manifestPath), { recursive: true });
await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
console.log(`Frozen ${slug}: ${manifest.file_count} files, ${manifest.total_bytes} bytes`);
