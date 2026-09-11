(async () => {
  const root = document.getElementById('catalog');
  try {
    const items = Array.isArray(window.RECIT_CATALOG_DATA)
      ? window.RECIT_CATALOG_DATA
      : await fetchJson('./catalog.json');
    if(!Array.isArray(items) || !items.length) throw new Error('catalog empty');
    root.replaceChildren(...items.map(item => {
      const a = document.createElement('a');
      a.className = 'catalog-card';
      a.href = `./s/${encodeURIComponent(item.slug)}/`;
      const availability = item.state==='blocked' ? ' · indisponible' : item.state==='degraded' ? ' · partiel' : '';
      a.innerHTML = `<span class="mode">${label(item.type)}</span><strong>${esc(item.title)}</strong><span>${esc(item.subtitle || '')}</span><small>${item.episode_count} épisode${item.episode_count > 1 ? 's' : ''}${availability}</small>`;
      return a;
    }));
  } catch (e) {
    console.error('Récit catalog bootstrap failed', e);
    root.innerHTML = '<div class="card"><strong>Impossible de charger les voyages.</strong><p>Le contenu local de l’application n’a pas pu être initialisé.</p><button type="button" onclick="location.reload()">Réessayer</button></div>';
  }

  async function fetchJson(url){
    const controller = new AbortController();
    const timer = setTimeout(()=>controller.abort(), 5000);
    try{
      const r = await fetch(url, {cache:'no-store', signal:controller.signal});
      if(!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } finally { clearTimeout(timer); }
  }
  function label(type){ return ({story:'Histoire',visit:'Visite',route:'Route'})[type] || 'Récit'; }
  function esc(s){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
})();
