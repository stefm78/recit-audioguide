import { access, readFile } from 'node:fs/promises';
import { dirname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';
const home = await readFile(join(www, 'index.html'), 'utf8');
const pagePath = join(www, 's', slug, 'index.html');
const page = await readFile(pagePath, 'utf8');
const series = JSON.parse(await readFile(join(www, 'data', slug, 'series.json'), 'utf8'));

function assert(cond, msg){ if(!cond) throw new Error(msg); }
assert(home.includes('id="recit-mobile-bootstrap"'), 'home bootstrap missing');
assert(home.includes(`\"slug\":\"${slug}\"`), 'field catalog does not contain Seville');
assert(page.includes('id="recit-mobile-bootstrap"'), 'series bootstrap missing');
assert(page.includes(`window.RECIT_SERIES_DATA`), 'inline series data missing');
assert(series.episodes?.length > 0, 'series has no episodes');

const playable = series.episodes.filter(e => e.audio_url && e.state !== 'failed');
assert(playable.length > 0, 'no playable Seville episode');
for(const e of playable){
  const u = new URL(e.audio_url, `https://localhost/s/${slug}/`);
  assert(u.origin === 'https://localhost', `non-local audio URL for ${e.id}: ${e.audio_url}`);
  const local = normalize(join(www, decodeURIComponent(u.pathname)));
  assert(local.startsWith(www), `audio escapes www for ${e.id}`);
  await access(local);
}

const target = join(www, 's', slug, 'index.html');
await access(target);
console.log(`Runtime PASS: catalog -> ${slug} -> ${playable.length} playable local episodes`);
