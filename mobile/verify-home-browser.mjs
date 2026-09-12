import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const www = resolve(here, 'www');
const html = await readFile(join(www, 'index.html'), 'utf8');
const source = await readFile(join(here, 'home-library.js'), 'utf8');

const dom = new JSDOM(html, {
  url: 'https://localhost/',
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(window){
    window.scrollTo = () => {};
    window.localStorage.setItem('recit:seville-discovery', JSON.stringify({episode:'seville-discovery-ep00', time:42, updated:Date.now()}));
  }
});

const {window} = dom;
const {document} = window;
const waitUntil = async (predicate, timeoutMs=3000) => {
  const started = Date.now();
  while(Date.now() - started < timeoutMs){
    if(predicate()) return;
    await new Promise(r => setTimeout(r, 20));
  }
  throw new Error(`timeout after ${timeoutMs}ms`);
};

await waitUntil(() => document.documentElement.dataset.recitHomeReady === '1');
const catalog = window.RECIT_CATALOG_DATA;
if(!Array.isArray(catalog) || !catalog.length) throw new Error('embedded FIELD catalog missing on home');
const editorial = catalog.filter(item => item.visible !== false);
const hiddenEditorial = catalog.filter(item => item.visible === false);
if(!editorial.length) throw new Error('traveler catalog unexpectedly empty');

const drawer = document.getElementById('home-library-drawer');
const openButton = document.querySelector('.home-library-button');
const edgeHint = document.querySelector('.home-library-edge-hint');
if(!drawer || !openButton || !edgeHint) throw new Error('home library shell incomplete');
if(openButton.textContent.trim() !== '☰ Bibliothèque') throw new Error(`unexpected visible library action: ${openButton.textContent}`);
if(edgeHint.getAttribute('aria-label') !== 'Ouvrir la bibliothèque depuis le bord gauche') throw new Error('home library edge affordance is not self-describing');

const cards = () => [...document.querySelectorAll('[data-library-card]')];
if(cards().length !== editorial.length) throw new Error(`initial visible card mismatch: ${cards().length}/${editorial.length}`);
for(const item of hiddenEditorial){
  if(document.querySelector(`[data-library-card="${item.slug}"]`)) throw new Error(`editorially hidden item leaked to home: ${item.slug}`);
  if([...drawer.querySelectorAll('[data-library-toggle]')].some(input => input.dataset.libraryToggle === item.slug)) throw new Error(`editorially hidden item leaked to user library controls: ${item.slug}`);
}

edgeHint.click();
if(drawer.getAttribute('aria-hidden') !== 'false') throw new Error('left edge hint did not open home library drawer');
drawer.querySelector('[data-library-close]')?.click();
if(drawer.getAttribute('aria-hidden') !== 'true') throw new Error('home library drawer did not close');

openButton.click();
const resumeButton = drawer.querySelector('[data-library-filter="resume"]');
if(!resumeButton || resumeButton.disabled) throw new Error('À reprendre filter should be available after seeded progress');
resumeButton.click();
if(cards().length !== 1 || cards()[0].dataset.libraryCard !== 'seville-discovery') throw new Error('À reprendre filter did not isolate the persisted Seville journey');
if(!cards()[0].textContent.includes('À reprendre · 0:42')) throw new Error('resume position is not visible on the home card');

window.RECIT_HOME_LIBRARY.open();
drawer.querySelector('[data-library-filter="all"]')?.click();
if(cards().length !== editorial.length) throw new Error('Tous les parcours did not restore all user-visible guides');

window.RECIT_HOME_LIBRARY.open();
const visitButton = drawer.querySelector('[data-library-filter="visit"]');
const expectedVisits = editorial.filter(item => item.type === 'visit').length;
if(expectedVisits && !visitButton?.disabled){
  visitButton.click();
  const visitCards = cards();
  if(visitCards.length !== expectedVisits) throw new Error(`visit filter mismatch: ${visitCards.length}/${expectedVisits}`);
  if(visitCards.some(card => card.dataset.libraryType !== 'visit')) throw new Error('visit filter exposed a non-visit guide');
}

window.RECIT_HOME_LIBRARY.open();
drawer.querySelector('[data-library-filter="all"]')?.click();
const target = editorial.find(item => item.slug !== 'seville-discovery') || editorial[0];
window.RECIT_HOME_LIBRARY.open();
let toggle = [...drawer.querySelectorAll('[data-library-toggle]')].find(input => input.dataset.libraryToggle === target.slug);
if(!toggle) throw new Error(`library toggle missing for ${target.slug}`);
toggle.checked = false;
toggle.dispatchEvent(new window.Event('change', {bubbles:true}));
const hidden = JSON.parse(window.localStorage.getItem('recit:library:hidden:v1') || '[]');
if(!hidden.includes(target.slug)) throw new Error(`user-hidden preference was not persisted for ${target.slug}`);
if(document.querySelector(`[data-library-card="${target.slug}"]`)) throw new Error(`user-hidden guide remains visible on home: ${target.slug}`);

window.RECIT_HOME_LIBRARY.open();
toggle = [...drawer.querySelectorAll('[data-library-toggle]')].find(input => input.dataset.libraryToggle === target.slug);
if(!toggle || toggle.checked) throw new Error(`hidden guide toggle state not restored for ${target.slug}`);
toggle.checked = true;
toggle.dispatchEvent(new window.Event('change', {bubbles:true}));
if(!document.querySelector(`[data-library-card="${target.slug}"]`)) throw new Error(`re-enabled guide did not return to home: ${target.slug}`);

if(!source.includes("t.clientX <= edge")) throw new Error('home drawer must start only from the left edge');
if(source.includes("innerWidth - edge") || source.includes("side:'right'") || source.includes('from-right')) throw new Error('home library must not expose right-edge opening');
if(!source.includes("item.visible !== false")) throw new Error('user library must remain subordinate to editorial visibility');
if(!source.includes("recit:library:hidden:v1")) throw new Error('persistent user library preference key missing');

console.log(`Home library PASS: ${catalog.length} packaged / ${editorial.length} editorially visible; drawer + filters + À reprendre + local hide/show + left-only gesture`);
dom.window.close();
