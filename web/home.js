(async () => {
  const STORAGE_KEY = 'recit:library:hidden:v1';
  const root = document.getElementById('catalog');
  if(!root) return;

  let source;
  try {
    source = Array.isArray(window.RECIT_CATALOG_DATA)
      ? window.RECIT_CATALOG_DATA
      : await fetchJson('./catalog.json');
    if(!Array.isArray(source) || !source.length) throw new Error('catalog empty');
  } catch (e) {
    console.error('Récit catalog bootstrap failed', e);
    root.innerHTML = '<div class="card"><strong>Impossible de charger les voyages.</strong><p>Le catalogue n’a pas pu être initialisé.</p><button type="button" onclick="location.reload()">Réessayer</button></div>';
    return;
  }

  const editorialCatalog = source.filter(item => item && item.editorially_visible !== false);
  const editorialSlugs = new Set(editorialCatalog.map(item => item.slug));
  let hidden = readHidden();
  let activeFilter = 'all';
  let drawer = null;
  let backdrop = null;
  let edgeHint = null;
  let openButton = null;

  setupShell();
  render();
  document.documentElement.dataset.recitHomeReady = '1';
  window.RECIT_HOME_LIBRARY = {
    open: openDrawer,
    close: closeDrawer,
    refresh(){ hidden = readHidden(); render(); },
    getState(){ return {filter:activeFilter, hidden:[...hidden]}; }
  };

  function readHidden(){
    try{
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      if(!Array.isArray(parsed)) return new Set();
      return new Set(parsed.filter(slug => editorialSlugs.has(slug)));
    }catch(_){ return new Set(); }
  }

  function writeHidden(){
    const safe = [...hidden].filter(slug => editorialSlugs.has(slug)).sort();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(safe));
  }

  function progressFor(item){
    try{
      const value = JSON.parse(localStorage.getItem(`recit:${item.slug}`) || 'null');
      return value && value.episode ? value : null;
    }catch(_){ return null; }
  }

  function resumeLabel(item){
    const p = progressFor(item);
    if(!p) return '';
    const total = Math.max(0, Math.floor(Number(p.time) || 0));
    const min = Math.floor(total / 60);
    const sec = total % 60;
    return `À reprendre · ${min}:${String(sec).padStart(2,'0')}`;
  }

  function visibleToUser(){ return editorialCatalog.filter(item => !hidden.has(item.slug)); }

  function filteredItems(){
    const items = visibleToUser();
    if(activeFilter === 'resume') return items.filter(progressFor);
    if(['visit','route','story'].includes(activeFilter)) return items.filter(item => item.type === activeFilter);
    return items;
  }

  function render(){
    const items = filteredItems();
    if(!items.length){
      const message = activeFilter === 'resume'
        ? 'Aucun parcours à reprendre pour le moment.'
        : 'Aucun parcours visible dans cette sélection.';
      root.innerHTML = `<section class="catalog-empty card"><strong>${esc(message)}</strong><p>Vous pouvez modifier votre bibliothèque depuis le menu.</p><button type="button" class="secondary" data-library-manage-open>Gérer ma bibliothèque</button></section>`;
    }else{
      root.innerHTML = catalogGroups(items).map(group => `<section class="catalog-group" data-catalog-group="${escAttr(group.type)}"><div class="catalog-group-head"><h3>${esc(group.label)}</h3><span>${group.items.length} expérience${group.items.length > 1 ? 's' : ''}</span></div><div class="catalog">${group.items.map(catalogCard).join('')}</div></section>`).join('');
    }
    renderDrawer();
  }

  function catalogGroups(items){
    if(activeFilter === 'resume') return [{type:'resume', label:'À reprendre', items}];
    if(['visit','route','story'].includes(activeFilter)) return [{type:activeFilter, label:modePlural(activeFilter), items}];
    const orderedTypes = ['visit','route','story'];
    const buckets = orderedTypes.map(type => ({type, items:items.filter(item => item.type === type)})).filter(group => group.items.length);
    const known = new Set(orderedTypes);
    const otherItems = items.filter(item => !known.has(item.type));
    if(buckets.length + (otherItems.length ? 1 : 0) <= 1) return [{type:'all', label:'Tous les parcours', items}];
    const groups = [];
    const singletons = [];
    for(const group of buckets){
      if(group.items.length === 1) singletons.push(...group.items);
      else groups.push({type:group.type, label:modePlural(group.type), items:group.items});
    }
    singletons.push(...otherItems);
    if(singletons.length) groups.push({type:'other', label:'Autres expériences', items:singletons});
    return groups.length ? groups : [{type:'all', label:'Tous les parcours', items}];
  }

  function catalogCard(item){
    const count = `${item.episode_count} épisode${item.episode_count > 1 ? 's' : ''}`;
    const status = availabilityLabel(item);
    const resume = resumeLabel(item);
    const resumeHtml = resume ? `<span class="catalog-resume">${esc(resume)}</span>` : '';
    return `<a class="catalog-card" data-library-card="${escAttr(item.slug)}" data-library-type="${escAttr(item.type || '')}" href="./s/${encodeURIComponent(item.slug)}/index.html"><span class="mode">${modeLabel(item.type)}</span><strong>${esc(item.title)}</strong><span>${esc(item.subtitle || '')}</span>${resumeHtml}<small>${count} · <span class="catalog-status">${esc(status)}</span></small></a>`;
  }

  function availabilityLabel(item){
    if(item.field_qualified) return 'qualifié terrain';
    if(item.state === 'blocked') return 'indisponible';
    if(item.state === 'degraded') return 'partiel';
    return 'disponible';
  }

  function setupShell(){
    installStyles();
    const hero = document.querySelector('.home-hero');
    openButton = document.createElement('button');
    openButton.type = 'button';
    openButton.className = 'home-library-button secondary';
    openButton.setAttribute('aria-controls','home-library-drawer');
    openButton.setAttribute('aria-expanded','false');
    openButton.innerHTML = '☰ Bibliothèque';
    openButton.addEventListener('click',openDrawer);
    hero?.appendChild(openButton);

    backdrop = document.createElement('div');
    backdrop.className = 'home-library-backdrop';
    backdrop.hidden = true;
    backdrop.addEventListener('click',closeDrawer);

    drawer = document.createElement('aside');
    drawer.id = 'home-library-drawer';
    drawer.className = 'home-library-drawer';
    drawer.setAttribute('aria-label','Navigation de la bibliothèque');
    drawer.setAttribute('aria-hidden','true');
    drawer.addEventListener('click',onDrawerClick);
    drawer.addEventListener('change',onDrawerChange);

    edgeHint = document.createElement('button');
    edgeHint.type = 'button';
    edgeHint.className = 'home-library-edge-hint';
    edgeHint.setAttribute('aria-label','Ouvrir la bibliothèque depuis le bord gauche');
    edgeHint.setAttribute('title','Bibliothèque');
    edgeHint.addEventListener('click',openDrawer);

    root.addEventListener('click',ev => {
      const manage = ev.target.closest('[data-library-manage-open]');
      if(!manage) return;
      openDrawer();
      drawer.querySelector('.home-library-manage')?.setAttribute('open','');
    });

    document.body.append(backdrop, drawer, edgeHint);
    installGestures();
  }

  function renderDrawer(){
    if(!drawer) return;
    const userVisible = visibleToUser();
    const counts = {
      all:userVisible.length,
      resume:userVisible.filter(progressFor).length,
      visit:userVisible.filter(item => item.type === 'visit').length,
      route:userVisible.filter(item => item.type === 'route').length,
      story:userVisible.filter(item => item.type === 'story').length
    };
    const nav = [
      ['all','Tous les parcours',counts.all],
      ['resume','À reprendre',counts.resume],
      ['visit','Visites',counts.visit],
      ['route','Routes',counts.route],
      ['story','Histoires',counts.story]
    ].map(([key,label,count]) => `<button type="button" class="home-library-nav${activeFilter === key ? ' active' : ''}" data-library-filter="${key}" ${key === 'resume' && count === 0 ? 'disabled' : ''}><span>${label}</span><strong>${count}</strong></button>`).join('');
    const management = editorialCatalog.map(item => {
      const checked = hidden.has(item.slug) ? '' : ' checked';
      return `<label class="home-library-toggle"><input type="checkbox" data-library-toggle="${escAttr(item.slug)}"${checked}><span><strong>${esc(item.title)}</strong><small>${modeLabel(item.type)} · ${availabilityLabel(item)}</small></span></label>`;
    }).join('');
    const wasOpen = drawer.querySelector('.home-library-manage')?.open || false;
    drawer.innerHTML = `<div class="home-library-head"><div><small>Récit audioguide</small><strong>Bibliothèque</strong></div><button type="button" class="home-library-close" data-library-close aria-label="Fermer la bibliothèque">×</button></div><nav class="home-library-nav-list">${nav}</nav><details class="home-library-manage"${wasOpen ? ' open' : ''}><summary>Gérer ma bibliothèque <span>${hidden.size} masqué${hidden.size > 1 ? 's' : ''}</span></summary><p>Masquez les parcours que vous ne souhaitez pas voir sur l’accueil. Ils restent installés et peuvent être réaffichés ici.</p><div class="home-library-toggle-list">${management}</div><button type="button" class="secondary home-library-reset" data-library-reset ${hidden.size ? '' : 'disabled'}>Tout réafficher</button></details>`;
  }

  function onDrawerClick(ev){
    if(ev.target.closest('[data-library-close]')){ closeDrawer(); return; }
    const filter = ev.target.closest('[data-library-filter]');
    if(filter && !filter.disabled){
      activeFilter = filter.dataset.libraryFilter || 'all';
      render();
      closeDrawer();
      window.scrollTo?.({top:0,behavior:'smooth'});
      return;
    }
    if(ev.target.closest('[data-library-reset]')){
      hidden.clear();
      writeHidden();
      render();
    }
  }

  function onDrawerChange(ev){
    const toggle = ev.target.closest('[data-library-toggle]');
    if(!toggle) return;
    const slug = toggle.dataset.libraryToggle;
    if(!editorialSlugs.has(slug)) return;
    if(toggle.checked) hidden.delete(slug); else hidden.add(slug);
    writeHidden();
    render();
  }

  function openDrawer(){
    if(!drawer || !backdrop) return;
    const fieldBuild = document.getElementById('recit-field-build');
    document.documentElement.style.setProperty('--recit-shell-top',`${fieldBuild?.offsetHeight || 0}px`);
    drawer.classList.add('open');
    backdrop.hidden = false;
    backdrop.classList.add('open');
    drawer.setAttribute('aria-hidden','false');
    document.body.classList.add('home-library-open');
    openButton?.setAttribute('aria-expanded','true');
    if(edgeHint) edgeHint.hidden = true;
  }

  function closeDrawer(){
    if(!drawer || !backdrop) return;
    drawer.classList.remove('open');
    backdrop.classList.remove('open');
    drawer.setAttribute('aria-hidden','true');
    document.body.classList.remove('home-library-open');
    openButton?.setAttribute('aria-expanded','false');
    if(edgeHint) edgeHint.hidden = false;
    setTimeout(() => { if(!backdrop.classList.contains('open')) backdrop.hidden = true; },180);
  }

  function installGestures(){
    let start = null;
    const edge = 28;
    document.addEventListener('touchstart',ev => {
      if(ev.touches.length !== 1 || drawer?.classList.contains('open')) return;
      const t = ev.touches[0];
      start = t.clientX <= edge ? {x:t.clientX,y:t.clientY} : null;
    },{passive:true});
    document.addEventListener('touchmove',ev => {
      if(!start || ev.touches.length !== 1) return;
      const t = ev.touches[0], dx = t.clientX - start.x, dy = t.clientY - start.y;
      if(dx > 58 && Math.abs(dx) > Math.abs(dy) * 1.25){ openDrawer(); start = null; }
      else if(Math.abs(dy) > 48 || dx < 0) start = null;
    },{passive:true});
    document.addEventListener('touchend',() => { start = null; },{passive:true});
    let drawerStart = null;
    drawer?.addEventListener('touchstart',ev => {
      if(ev.touches.length === 1){ const t = ev.touches[0]; drawerStart = {x:t.clientX,y:t.clientY}; }
    },{passive:true});
    drawer?.addEventListener('touchmove',ev => {
      if(!drawerStart || ev.touches.length !== 1) return;
      const t = ev.touches[0], dx = t.clientX - drawerStart.x, dy = t.clientY - drawerStart.y;
      if(dx < -58 && Math.abs(dx) > Math.abs(dy) * 1.25){ closeDrawer(); drawerStart = null; }
    },{passive:true});
    drawer?.addEventListener('touchend',() => { drawerStart = null; },{passive:true});
    document.addEventListener('keydown',ev => { if(ev.key === 'Escape') closeDrawer(); });
  }

  function installStyles(){
    if(document.getElementById('recit-home-library-style')) return;
    const style = document.createElement('style');
    style.id = 'recit-home-library-style';
    style.textContent = `.home-library-button{display:inline-flex;align-items:center;margin-top:6px;min-height:40px}.catalog-resume{font:850 .76rem/1.2 system-ui,sans-serif;color:#8a611e!important}.catalog-empty{font-family:system-ui,sans-serif}.catalog-empty p{color:var(--muted)}.home-library-backdrop{position:fixed;inset:var(--recit-shell-top,0px) 0 0;background:rgba(5,18,23,.42);opacity:0;transition:opacity .18s ease;z-index:2147483644}.home-library-backdrop[hidden]{display:none}.home-library-backdrop.open{opacity:1}.home-library-drawer{position:fixed;top:var(--recit-shell-top,0px);bottom:0;left:0;width:min(88vw,390px);background:var(--paper);box-shadow:18px 0 48px rgba(0,0,0,.28);transform:translateX(-104%);transition:transform .2s ease;z-index:2147483645;display:grid;grid-template-rows:auto auto minmax(0,1fr);font-family:system-ui,sans-serif}.home-library-drawer.open{transform:translateX(0)}.home-library-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;padding:18px 16px 13px;border-bottom:1px solid var(--line)}.home-library-head small,.home-library-head strong{display:block}.home-library-head small{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:.68rem;font-weight:850}.home-library-head strong{font-family:Georgia,serif;font-size:1.35rem;line-height:1.2}.home-library-close{border:0;background:var(--soft);color:var(--accent);width:38px;height:38px;border-radius:50%;font-size:1.5rem;line-height:1;cursor:pointer}.home-library-nav-list{display:grid;padding:8px 9px;border-bottom:1px solid var(--line)}.home-library-nav{display:flex;justify-content:space-between;align-items:center;gap:12px;border:0;background:transparent;color:var(--ink);padding:11px 10px;border-radius:12px;font:800 .9rem/1.2 system-ui,sans-serif;text-align:left;cursor:pointer}.home-library-nav strong{min-width:28px;text-align:center;border-radius:999px;padding:3px 7px;background:var(--soft);color:var(--accent);font-size:.72rem}.home-library-nav.active{background:#f8f1df;color:#6b4a17}.home-library-nav:disabled{opacity:.42;cursor:default}.home-library-manage{overflow:auto;padding:11px 14px calc(92px + env(safe-area-inset-bottom))}.home-library-manage summary{display:flex;justify-content:space-between;gap:10px;cursor:pointer;font-weight:850;color:var(--accent);list-style:none}.home-library-manage summary::-webkit-details-marker{display:none}.home-library-manage summary span{color:var(--muted);font-size:.72rem}.home-library-manage>p{margin:.55rem 0 1rem;color:var(--muted);font-size:.8rem}.home-library-toggle-list{display:grid;gap:2px}.home-library-toggle{display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px;align-items:center;padding:10px 4px;border-top:1px solid var(--line);cursor:pointer}.home-library-toggle input{width:20px;height:20px;accent-color:var(--accent)}.home-library-toggle strong,.home-library-toggle small{display:block}.home-library-toggle strong{font-size:.85rem;line-height:1.2}.home-library-toggle small{color:var(--muted);font-size:.68rem;margin-top:2px}.home-library-reset{margin-top:12px}.home-library-open{overflow:hidden}.home-library-edge-hint{display:none;position:fixed;left:0;top:52vh;width:6px;height:44px;padding:0;border:0;border-radius:0 4px 4px 0;background:rgba(184,135,46,.58);box-shadow:none;z-index:2147483643;cursor:pointer;opacity:.82}.home-library-edge-hint:focus-visible{width:10px;outline:2px solid var(--gold);outline-offset:2px;opacity:1}.home-library-edge-hint[hidden]{display:none!important}@media(pointer:coarse){.home-library-edge-hint{display:block}}@media(prefers-reduced-motion:reduce){.home-library-drawer,.home-library-backdrop{transition:none}}`;
    document.head.appendChild(style);
  }

  async function fetchJson(url){
    const controller = new AbortController();
    const timer = setTimeout(()=>controller.abort(), 5000);
    try{
      const response = await fetch(url, {cache:'no-store', signal:controller.signal});
      if(!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } finally { clearTimeout(timer); }
  }

  function modeLabel(type){ return ({story:'Histoire',visit:'Visite',route:'Route'})[type] || 'Récit'; }
  function modePlural(type){ return ({story:'Histoires',visit:'Visites',route:'Routes'})[type] || 'Autres expériences'; }
  function esc(value){ return String(value ?? '').replace(/[&<>"']/g,c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  function escAttr(value){ return esc(value); }
})();
