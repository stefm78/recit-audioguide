(() => {
  const slug = window.RECIT_SERIES_SLUG;
  if (!slug) return;

  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cueLabels = {ARRIVAL:'Arriver',LOOK:'Regarder',STORY:'Comprendre',REVEAL:'Découvrir',MOVE:'Marcher',SILENCE:'Regarder sans audio',COMPARE:'Comparer',HUMAN_STORY:'Histoire humaine',OPTIONAL_DEPTH:'Approfondir',EXIT:'Continuer'};

  async function load() {
    const r = await fetch(`../../data/${encodeURIComponent(slug)}/series.json`, {cache:'no-store'});
    if (!r.ok) return;
    const series = await r.json();
    const episodes = series.episodes || [];
    let experience = null;
    if (series.type === 'visit') {
      try {
        const x = await fetch(`../../data/${encodeURIComponent(slug)}/assets/visit-experience.json`, {cache:'no-store'});
        if (x.ok) experience = await x.json();
      } catch (_) {}
    }

    if (experience) injectStyles();

    function firstPendingIndex() {
      const pending = episodes.findIndex(e => localStorage.getItem(`recit:done:${series.slug || slug}:${e.id}`) !== '1');
      return pending < 0 ? Math.max(episodes.length - 1, 0) : pending;
    }

    function renderNow() {
      if (!experience || !episodes.length) return false;
      const hero = document.querySelector('.series-hero');
      if (!hero) return true;
      if (document.querySelector('[data-visit-now]')) return false;
      const index = firstPendingIndex();
      const episode = episodes[index];
      const field = experience.episodes?.[episode.id];
      if (!field) return false;
      const now = document.createElement('section');
      now.dataset.visitNow = '1';
      now.className = 'visit-now card';
      const route = episode.maps_url ? `<a class="secondary" target="_blank" rel="noopener" href="${esc(episode.maps_url)}">Itinéraire</a>` : '';
      const play = episode.audio_url && episode.state !== 'failed' ? `<button class="primary" data-play="${esc(episode.id)}">▶ Écouter</button>` : '';
      now.innerHTML = `<p class="visit-now-kicker">Maintenant · étape ${index + 1}/${episodes.length}</p><h2>${esc(episode.title)}</h2><p class="visit-now-why">${esc(field.why || episode.summary || '')}</p>${field.look_first ? `<div class="look-first"><strong>Regardez d’abord</strong><span>${esc(field.look_first)}</span></div>` : ''}<div class="visit-now-meta">${field.field_minutes ? `<span>≈ ${esc(field.field_minutes)} min sur place</span>` : ''}${episode.stop ? `<span>${esc(episode.stop)}</span>` : ''}</div><div class="visit-now-actions">${play}${route}<a class="secondary" href="#${esc(episode.id)}">Voir l’étape</a></div>`;
      hero.insertAdjacentElement('afterend', now);
      return false;
    }

    function renderFieldProgram(episode) {
      if (!experience) return '';
      const field = experience.episodes?.[episode.id];
      if (!field) return '';
      const cues = (field.cues || []).filter(c => c.type !== 'OPTIONAL_DEPTH' && c.text);
      if (!cues.length) return '';
      return `<details class="field-program"><summary>Sur place · quoi regarder et quand ralentir</summary><ol>${cues.map(c => `<li class="cue cue-${esc(c.type.toLowerCase())}"><strong>${esc(cueLabels[c.type] || c.type)}</strong><span>${esc(c.text)}</span></li>`).join('')}</ol></details>`;
    }

    function enhance() {
      let pending = renderNow();

      if (series.type === 'visit' && series.visit?.overview_maps_url) {
        const strip = document.querySelector('.visit-strip');
        if (!strip) pending = true;
        else if (!strip.querySelector('[data-route-overview]')) {
          const overview = document.createElement('a');
          overview.dataset.routeOverview = '1';
          overview.className = 'secondary';
          overview.target = '_blank';
          overview.rel = 'noopener';
          overview.href = series.visit.overview_maps_url;
          overview.textContent = 'Voir le parcours complet';
          strip.appendChild(overview);
        }
      }

      episodes.forEach((episode, index) => {
        const card = document.getElementById(episode.id);
        if (!card) { pending = true; return; }

        if (experience && !card.querySelector('[data-field-experience]')) {
          const field = experience.episodes?.[episode.id];
          if (field) {
            const block = document.createElement('div');
            block.dataset.fieldExperience = '1';
            block.className = 'field-experience';
            block.innerHTML = `${field.why ? `<p class="field-why"><strong>Pourquoi ici :</strong> ${esc(field.why)}</p>` : ''}${field.look_first ? `<p class="field-look"><strong>Regardez d’abord :</strong> ${esc(field.look_first)}</p>` : ''}${renderFieldProgram(episode)}`;
            const actions = card.querySelector('.actions');
            if (actions) actions.insertAdjacentElement('afterend', block); else card.appendChild(block);
          }
        }

        if (!episode.next_step || index >= episodes.length - 1 || card.querySelector('[data-next-step]')) return;
        const next = episode.next_step;
        const block = document.createElement('div');
        block.dataset.nextStep = '1';
        block.className = 'next-step';
        const precision = next.precision === 'routed' ? 'routé' : 'indicatif';
        block.innerHTML = `<p><strong>Étape suivante :</strong> ${esc(next.label || episodes[index + 1].stop || episodes[index + 1].title)}${next.distance_km != null ? ` · ~${esc(next.distance_km)} km` : ''}${next.walk_minutes != null ? ` · ~${esc(next.walk_minutes)} min` : ''} <small>(${precision})</small></p>`;
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

  function injectStyles() {
    if (document.getElementById('visit-experience-styles')) return;
    const style = document.createElement('style');
    style.id = 'visit-experience-styles';
    style.textContent = `
      .visit-now{border:2px solid #183d49;margin:0 0 1rem;padding:1rem;background:#f7fbfb}
      .visit-now-kicker{margin:0 0 .25rem;text-transform:uppercase;letter-spacing:.08em;font-size:.78rem;font-weight:800;color:#183d49}
      .visit-now h2{margin:.2rem 0 .5rem}.visit-now-why{font-size:1.06rem;margin:.25rem 0 .75rem}
      .look-first{display:grid;gap:.2rem;padding:.75rem;border-radius:.65rem;background:#eef5f3;margin:.6rem 0}.look-first strong{font-size:.82rem;text-transform:uppercase;letter-spacing:.05em}
      .visit-now-meta{display:flex;flex-wrap:wrap;gap:.4rem .8rem;font-size:.88rem;color:#536366;margin:.65rem 0}
      .visit-now-actions{display:flex;gap:.5rem;flex-wrap:wrap}.field-experience{margin-top:.8rem;border-top:1px solid #d9e2e2;padding-top:.7rem}
      .field-why,.field-look{margin:.45rem 0}.field-program{margin-top:.6rem}.field-program summary{font-weight:750;cursor:pointer}
      .field-program ol{list-style:none;padding:0;margin:.7rem 0 0;display:grid;gap:.55rem}.cue{display:grid;grid-template-columns:minmax(6.8rem,auto) 1fr;gap:.6rem;align-items:start;padding:.55rem .65rem;border-left:3px solid #9bb7b1;background:#f8faf9;border-radius:.25rem}
      .cue strong{font-size:.82rem;color:#183d49}.cue-silence{border-left-color:#b58a5d;background:#fbf7f1}.cue-reveal{border-left-color:#6d82a8}.cue-look{border-left-color:#678f76}
      @media (max-width:640px){.visit-now{margin-left:-.15rem;margin-right:-.15rem}.visit-now-actions>*{flex:1 1 8rem;text-align:center}.cue{grid-template-columns:1fr;gap:.15rem}}
    `;
    document.head.appendChild(style);
  }

  load().catch(() => {});
})();
