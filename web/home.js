(async () => {
  const root = document.getElementById('catalog');
  try {
    const r = await fetch('./catalog.json', {cache: 'no-store'});
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const items = await r.json();
    root.replaceChildren(...items.map(item => {
      const a = document.createElement('a');
      a.className = 'catalog-card';
      a.href = `./s/${encodeURIComponent(item.slug)}/`;
      a.innerHTML = `<span class="mode">${label(item.type)}</span><strong>${esc(item.title)}</strong><span>${esc(item.subtitle || '')}</span><small>${item.episode_count} épisode${item.episode_count > 1 ? 's' : ''}</small>`;
      return a;
    }));
  } catch (e) {
    root.innerHTML = '<p>Les voyages ne peuvent pas être chargés pour le moment.</p>';
  }
  function label(type){ return ({story:'Histoire',visit:'Visite',route:'Route'})[type] || 'Récit'; }
  function esc(s){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
})();
