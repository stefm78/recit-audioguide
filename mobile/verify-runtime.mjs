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
const styles = await readFile(join(www, 'assets', 'styles.css'), 'utf8');
const homeSource = await readFile(join(www, 'assets', 'home.js'), 'utf8');
const catalog = JSON.parse(await readFile(join(www, 'catalog.json'), 'utf8'));
const series = JSON.parse(await readFile(join(www, 'data', slug, 'series.json'), 'utf8'));
const pkg = JSON.parse(await readFile(join(here, 'package.json'), 'utf8'));

function assert(cond, msg){ if(!cond) throw new Error(msg); }

assert(home.includes('id="recit-field-build"'), 'visible FIELD build identity missing on home');
assert(home.includes('id="recit-field-build-data"'), 'machine-readable FIELD build identity missing on home');
assert(home.includes('FIELD BUILD 0.4.'), 'FIELD build version not visibly stamped on home');
assert(home.includes('com.stefm78.recitaudioguide.field'), 'FIELD package identity not visibly stamped on home');
assert(home.includes('id="recit-field-seville-launch"'), 'static Seville launcher missing');
assert(home.includes(`href="./s/${slug}/index.html"`), 'static Seville launcher must target explicit packaged index.html');
const launchUrl = new URL(`./s/${slug}/index.html`, 'https://localhost/');
assert(launchUrl.pathname === `/s/${slug}/index.html`, `unexpected field launch URL: ${launchUrl.href}`);
assert(!home.includes('<p>Chargement…</p>'), 'home still contains a loading-only state');
assert(home.includes('src="./assets/home.js"'), 'FIELD home must consume shared Web home.js');
assert(!home.includes('id="recit-home-library"'), 'FIELD home must not inline a second Library implementation');
assert(home.includes('id="recit-mobile-bootstrap"'), 'home embedded bootstrap missing');
assert(home.includes('window.RECIT_CATALOG_DATA = catalog'), 'FIELD home catalog bootstrap missing');
assert(home.includes('class="catalog-groups"'), 'FIELD home must expose grouped catalog navigation');
assert(home.includes('class="catalog-group"'), 'FIELD home catalog grouping is missing');
assert(home.includes('id="recit-field-shell-style"'), 'FIELD shell style missing from home');
assert(catalog.length > 1, `FIELD packaged catalog unexpectedly contains only ${catalog.length} guide`);
assert(catalog.every(item => typeof item.editorially_visible === 'boolean'), 'shared catalog editorial visibility must remain explicit after offline freeze');

const bootstrapMatch = home.match(/const catalog = (\[[\s\S]*?\]);\n  window\.RECIT_CATALOG_DATA/);
assert(bootstrapMatch, 'embedded FIELD catalog payload missing');
const fieldCatalog = JSON.parse(bootstrapMatch[1]);
assert(fieldCatalog.length === catalog.length, `embedded FIELD catalog mismatch: ${fieldCatalog.length}/${catalog.length}`);
assert(fieldCatalog.every(item => typeof item.editorially_visible === 'boolean'), 'FIELD catalog editorial visibility must be explicit for every packaged guide');
assert(fieldCatalog.every(item => typeof item.field_qualified === 'boolean'), 'FIELD qualification marker must be explicit for every packaged guide');
const visibleCatalog = fieldCatalog.filter(item => item.editorially_visible);
const hiddenCatalog = fieldCatalog.filter(item => !item.editorially_visible);
assert(visibleCatalog.length > 1, `FIELD visible catalog unexpectedly contains only ${visibleCatalog.length} guide`);
assert(hiddenCatalog.some(item => item.slug === 'kernel-handover'), 'internal technical explainer should remain packaged but editorially hidden from traveler catalog');
assert(fieldCatalog.filter(item => item.field_qualified).map(item => item.slug).join(',') === slug, 'only the physically qualified Seville guide may carry field_qualified=true');

assert(homeSource.includes("const STORAGE_KEY = 'recit:library:hidden:v1'"), 'persistent shared home-library preference key missing');
assert(homeSource.includes('item && item.editorially_visible !== false'), 'user library must remain subordinate to editorial visibility');
assert(homeSource.includes("['all','Tous les parcours'"), 'home library All navigation missing');
assert(homeSource.includes("['resume','À reprendre'"), 'home library resume navigation missing');
assert(homeSource.includes("['visit','Visites'"), 'home library visits navigation missing');
assert(homeSource.includes("['route','Routes'"), 'home library routes navigation missing');
assert(homeSource.includes("['story','Histoires'"), 'home library stories navigation missing');
assert(homeSource.includes('Gérer ma bibliothèque'), 'home library management surface missing');
assert(homeSource.includes('data-library-toggle'), 'home library hide/show controls missing');
assert(homeSource.includes('t.clientX <= edge'), 'home library must open from the left edge only');
assert(!homeSource.includes('innerWidth - edge') && !homeSource.includes("side:'right'") && !homeSource.includes('from-right'), 'home library must not expose right-edge opening');
assert(!homeSource.includes('kernel-handover'), 'shared home source must not hard-code editorial content identities');
assert(pkg.scripts?.['verify:home-browser'] === 'node verify-home-browser.mjs', 'home browser verification script missing');
assert(pkg.scripts?.['prepare:offline-seville']?.includes('npm run verify:home-browser'), 'offline FIELD pipeline must run the home browser gate');

for(const item of fieldCatalog){
  const href = `href="./s/${item.slug}/index.html"`;
  if(item.editorially_visible) assert(home.includes(href), `FIELD home missing editorially visible guide link: ${item.slug}`);
  else assert(!home.includes(href), `FIELD home exposes editorially hidden guide: ${item.slug}`);
  const packagedPage = join(www, 's', item.slug, 'index.html');
  const packagedData = join(www, 'data', item.slug, 'series.json');
  await access(packagedPage);
  await access(packagedData);
  const packagedHtml = await readFile(packagedPage, 'utf8');
  assert(packagedHtml.includes('id="recit-field-build"'), `FIELD identity missing from packaged guide: ${item.slug}`);
  assert(packagedHtml.includes('id="recit-field-shell-style"'), `FIELD shell style missing from packaged guide: ${item.slug}`);
  assert(packagedHtml.includes('class="series-topbar"'), `top navigation missing from packaged guide: ${item.slug}`);
  assert(packagedHtml.includes('class="series-home-link" href="../../"'), `catalog return link missing from packaged guide: ${item.slug}`);
  assert(packagedHtml.includes('class="series-parcours-button"'), `visible Parcours action missing from packaged guide: ${item.slug}`);
}

assert(page.includes('id="recit-field-build"'), 'visible FIELD build identity missing on qualified series page');
assert(page.includes('id="recit-field-build-data"'), 'machine-readable FIELD build identity missing on series page');
assert(page.includes('id="recit-field-monitor"'), 'qualified series field monitor missing');
assert(page.includes('id="recit-mobile-bootstrap"'), 'series bootstrap missing');
assert(page.includes('window.RECIT_SERIES_DATA = qualifiedSeries'), 'qualified inline series data missing');
assert(page.includes('--recit-system-safe-top:env(safe-area-inset-top,0px)'), 'system safe-area top variable missing from FIELD shell');
assert(page.includes('.series-topbar{top:var(--recit-system-safe-top)!important}'), 'series topbar must stick below the system safe-area inset');
assert(page.includes('padding:calc(9px + env(safe-area-inset-top,0px))'), 'FIELD identity must also respect the top system safe area');
const bootstrapPos = page.indexOf('id="recit-mobile-bootstrap"');
const appPos = page.indexOf('src="../../assets/app.js"');
assert(bootstrapPos >= 0 && appPos > bootstrapPos, 'series bootstrap must execute before app.js');
assert(app.includes('const embedded = window.RECIT_SERIES_DATA'), 'app.js does not consume embedded series data directly');
assert(app.includes('embedded.slug === slug'), 'embedded series data is not slug-qualified');
assert(app.includes("document.documentElement.dataset.recitSeriesReady = '1'"), 'series-ready runtime marker missing');
assert(app.includes('Récit series bootstrap timeout'), 'visible bootstrap watchdog missing');

assert(pkg.dependencies?.['@capgo/capacitor-media-session'] === '8.0.30', 'Capacitor 8 native media-session bridge is not pinned');
assert(app.includes('function nativeMediaSession()'), 'Android native media-session adapter missing');
assert(app.includes("bind('seekbackward',()=>seekBy(-15))"), 'native/media seek backward must remain 15 seconds');
assert(app.includes("bind('seekforward',()=>seekBy(15))"), 'native/media seek forward must remain 15 seconds');
assert(app.includes('userResumeRequired'), 'interruption manual-resume latch missing');
assert(app.includes('Reprise automatique bloquée après interruption'), 'interruption auto-resume guard missing');
assert(app.includes("journeyDrawer.id='journey-drawer'"), 'journey drawer missing');
assert(app.includes("journeyEdgeHint.className='journey-edge-hint'"), 'left-edge journey affordance missing');
assert(styles.includes('.journey-edge-hint'), 'left-edge journey affordance styling missing');
assert(styles.includes('width:6px;height:44px'), 'left-edge hint must stay visually thin');
assert(styles.includes('.journey-menu-button{display:none}'), 'legacy in-hero Parcours control should not duplicate the top navigation');
assert(styles.includes('.series-topbar{'), 'series top navigation styling missing');
assert(app.includes('start=t.clientX<=edge?'), 'left-edge swipe start contract missing');
assert(app.includes('if(dx>58&&Math.abs(dx)>Math.abs(dy)*1.25){openJourneyDrawer()'), 'left-to-right drawer swipe contract missing');
assert(!app.includes("side:'right'"), 'right-edge drawer opening must be forbidden');
assert(!app.includes('from-right'), 'right-side drawer variant must be removed');
assert(!styles.includes('.journey-drawer.from-right'), 'right-side drawer CSS variant must be removed');
assert(app.includes('Continuer · étape'), 'visible restart/resume state missing');

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
console.log(`Runtime PASS: ${fieldCatalog.length} packaged / ${visibleCatalog.length} editorially visible / ${hiddenCatalog.length} editorially hidden guides + shared personal home library + grouped traveler catalog + safe-area topbar + ${playable.length} qualified local Seville episodes + thin left-only drawer hint + interruption guard + Android media-session contract`);
