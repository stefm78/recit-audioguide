import { access, readFile } from 'node:fs/promises';
import { join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const slug = process.argv[2] || 'seville-discovery';
const home = await readFile(join(www, 'index.html'), 'utf8');
const pagePath = join(www, 's', slug, 'index.html');
const page = await readFile(pagePath, 'utf8');
const app = await readFile(join(www, 'assets', 'app.js'), 'utf8');
const series = JSON.parse(await readFile(join(www, 'data', slug, 'series.json'), 'utf8'));

function assert(cond, msg){ if(!cond) throw new Error(msg); }

assert(home.includes('id="recit-field-build"'), 'visible FIELD build identity missing on home');
assert(home.includes('id="recit-field-build-data"'), 'machine-readable FIELD build identity missing on home');
assert(home.includes('FIELD BUILD 0.4.'), 'FIELD build version not visibly stamped on home');
assert(home.includes('com.stefm78.recitaudioguide.field'), 'FIELD package identity not visibly stamped on home');
assert(home.includes('id="recit-field-seville-launch"'), 'static Seville launcher missing');
assert(home.includes(`href="./s/${slug}/"`), 'static Seville launcher points to wrong target');
assert(!home.includes('<p>Chargement…</p>'), 'home still contains a loading-only state');
assert(!home.includes('src="./assets/home.js"'), 'FIELD home must not depend on home.js');
assert(home.includes('id="recit-mobile-bootstrap"'), 'home embedded bootstrap missing');
assert(home.includes(`\"slug\":\"${slug}\"`), 'embedded field data does not contain Seville');

assert(page.includes('id="recit-field-build"'), 'visible FIELD build identity missing on series page');
assert(page.includes('id="recit-field-build-data"'), 'machine-readable FIELD build identity missing on series page');
assert(page.includes('id="recit-field-monitor"'), 'series field monitor missing');
assert(page.includes('id="recit-mobile-bootstrap"'), 'series bootstrap missing');
assert(page.includes('window.RECIT_SERIES_DATA'), 'inline series data missing');
const bootstrapPos = page.indexOf('id="recit-mobile-bootstrap"');
const appPos = page.indexOf('src="../../assets/app.js"');
assert(bootstrapPos >= 0 && appPos > bootstrapPos, 'series bootstrap must execute before app.js');
assert(app.includes('const embedded = window.RECIT_SERIES_DATA'), 'app.js does not consume embedded series data directly');
assert(app.includes('embedded.slug === slug'), 'embedded series data is not slug-qualified');
assert(app.includes("document.documentElement.dataset.recitSeriesReady = '1'"), 'series-ready runtime marker missing');
assert(app.includes('Récit series bootstrap timeout'), 'visible bootstrap watchdog missing');
assert(series.episodes?.length >= 10, `Seville field series incomplete: ${series.episodes?.length || 0} top-level episodes`);

const playable = series.episodes.filter(e => e.audio_url && e.state !== 'failed');
assert(playable.length >= 10, `Seville field audio incomplete: ${playable.length}/10 top-level episodes playable`);
for(const e of playable){
  const u = new URL(e.audio_url, `https://localhost/s/${slug}/`);
  assert(u.origin === 'https://localhost', `non-local audio URL for ${e.id}: ${e.audio_url}`);
  const local = normalize(join(www, decodeURIComponent(u.pathname)));
  assert(local.startsWith(www), `audio escapes www for ${e.id}`);
  await access(local);
}

await access(pagePath);
console.log(`Runtime PASS: static FIELD launcher -> ${slug} -> ${playable.length} playable local episodes; no home JS/fetch dependency; build identity visible`);
