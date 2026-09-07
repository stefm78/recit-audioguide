(() => {
  const slug = window.RECIT_SERIES_SLUG;
  if (!slug) return;

  async function load() {
    const r = await fetch(`../../data/${encodeURIComponent(slug)}/series.json`, {cache:'no-store'});
    if (!r.ok) return;
    const series = await r.json();
    const episodes = series.episodes || [];

    function enhance() {
      let pending = false;
      episodes.forEach((episode, index) => {
        if (!episode.next_step || index >= episodes.length - 1) return;
        const card = document.getElementById(episode.id);
        if (!card) { pending = true; return; }
        if (card.querySelector('[data-next-step]')) return;

        const next = episode.next_step;
        const block = document.createElement('div');
        block.dataset.nextStep = '1';
        block.className = 'next-step';
        const precision = next.precision === 'routed' ? 'routé' : 'indicatif';
        block.innerHTML = `<p><strong>Étape suivante :</strong> ${escapeHtml(next.label || episodes[index + 1].stop || episodes[index + 1].title)}${next.distance_km != null ? ` · ~${escapeHtml(next.distance_km)} km` : ''}${next.walk_minutes != null ? ` · ~${escapeHtml(next.walk_minutes)} min` : ''} <small>(${precision})</small></p>`;
        if (episode.maps_url) {
          const a = document.createElement('a');
          a.className = 'secondary';
          a.target = '_blank';
          a.rel = 'noopener';
          a.href = episode.maps_url;
          a.textContent = 'Rejoindre l’étape suivante';
          block.appendChild(a);
        }
        card.appendChild(block);
      });
      return pending;
    }

    if (!enhance()) return;
    const observer = new MutationObserver(() => { if (!enhance()) observer.disconnect(); });
    observer.observe(document.getElementById('app'), {childList:true, subtree:true});
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  load().catch(() => {});
})();
