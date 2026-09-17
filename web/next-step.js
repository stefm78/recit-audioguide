(() => {
  const slug = window.RECIT_SERIES_SLUG;
  if (!slug) return;

  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cueLabels = {ARRIVAL:'Arriver',LOOK:'Regarder',STORY:'Comprendre',REVEAL:'Découvrir',MOVE:'Marcher',SILENCE:'Regarder sans audio',MICRO_SILENCE:'Respiration',USER_PAUSE:'Pause libre · reprenez quand vous voulez',COMPARE:'Comparer',HUMAN_STORY:'Histoire humaine',OPTIONAL_DEPTH:'Approfondir',EXIT:'Continuer'};

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

    const audioFirst = getAudioFirstConfig(experience);
    if (audioFirst) injectAudioFirstStyles();

    function getAudioFirstConfig(payload) {
      const config = payload?.capabilities?.audio_first_field_ui;
      if (!config || config.enabled !== true || Number(config.version) !== 2) return null;
      if (!String(config.classic_fallback_url || '').trim()) return null;
      return config;
    }

    function firstPendingIndex() {
      const pending = episodes.findIndex(e => localStorage.getItem(`recit:done:${series.slug || slug}:${e.id}`) !== '1');
      return pending < 0 ? Math.max(episodes.length - 1, 0) : pending;
    }

    function concise(value, limit) {
      const text = String(value || '').replace(/\s+/g, ' ').trim();
      if (text.length <= limit) return text;
      return `${text.slice(0, Math.max(1, limit - 1)).trimEnd()}…`;
    }

    function primaryCue(episode, field) {
      const cue = field?.look_first
        || (field?.cues || []).find(c => c?.text && c.type !== 'OPTIONAL_DEPTH')?.text
        || episode.look
        || episode.launch
        || episode.summary
        || '';
      return concise(cue, 180);
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

    function decorateEpisodeCard(episode, card) {
      if (!experience || card.querySelector('[data-field-experience]')) return;
      const field = experience.episodes?.[episode.id];
      if (!field) return;
      const block = document.createElement('div');
      block.dataset.fieldExperience = '1';
      block.className = 'field-experience';
      block.innerHTML = `${field.why ? `<p class="field-why"><strong>Pourquoi ici :</strong> ${esc(field.why)}</p>` : ''}${field.look_first ? `<p class="field-look"><strong>Regardez d’abord :</strong> ${esc(field.look_first)}</p>` : ''}${renderFieldProgram(episode)}`;
      const actions = card.querySelector('.actions');
      if (actions) actions.insertAdjacentElement('afterend', block); else card.appendChild(block);
    }

    function decorateEpisodeCards() {
      let pending = false;
      episodes.forEach(episode => {
        const card = document.getElementById(episode.id);
        if (!card) { pending = true; return; }
        decorateEpisodeCard(episode, card);
      });
      return pending;
    }

    function enhanceLegacy() {
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

        decorateEpisodeCard(episode, card);

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

    function setupAudioFirst() {
      const root = document.getElementById('app');
      const hero = document.querySelector('.series-hero');
      const episodesRoot = root?.querySelector('.episodes');
      if (!root || !hero || !episodesRoot) return true;
      if (root.dataset.audioFirstReady === '1') return false;

      const fieldIndexes = episodes
        .map((episode, index) => ({episode, index, field: experience.episodes?.[episode.id]}))
        .filter(item => item.field);
      if (!fieldIndexes.length) return false;

      root.classList.add('audio-first-v2');
      root.dataset.audioFirstReady = '1';
      decorateEpisodeCards();

      const stage = document.createElement('section');
      stage.className = 'audio-first-stage card';
      stage.dataset.audioFirstStage = '1';
      stage.setAttribute('aria-live', 'polite');
      hero.insertAdjacentElement('afterend', stage);

      let cursor = Math.max(0, fieldIndexes.findIndex(item => item.index === firstPendingIndex()));
      if (cursor < 0) cursor = 0;
      let arrived = false;

      const playerAudio = document.getElementById('player-audio');
      const playerToggle = document.getElementById('player-toggle');

      function currentItem() {
        return fieldIndexes[Math.max(0, Math.min(cursor, fieldIndexes.length - 1))];
      }

      function audioMatches(episode) {
        if (!playerAudio || !episode?.audio_url) return false;
        const current = playerAudio.currentSrc || playerAudio.src || '';
        if (!current) return false;
        try {
          return new URL(current, location.href).href === new URL(episode.audio_url, location.href).href;
        } catch (_) {
          return current === episode.audio_url;
        }
      }

      function syncAudioButton() {
        const button = stage.querySelector('[data-audio-first-toggle]');
        if (!button) return;
        const {episode} = currentItem();
        const playable = Boolean(episode.audio_url && episode.state !== 'failed');
        button.disabled = !playable;
        if (!playable) {
          button.textContent = 'Audio indisponible';
          button.setAttribute('aria-label', 'Audio indisponible');
          return;
        }
        if (audioMatches(episode)) {
          const playing = playerAudio && !playerAudio.paused && !playerAudio.ended;
          button.textContent = playing ? '❚❚ Pause' : '▶ Reprendre';
          button.setAttribute('aria-label', playing ? 'Mettre l’audio en pause' : 'Reprendre l’audio');
        } else {
          button.textContent = '▶ Écouter';
          button.setAttribute('aria-label', 'Écouter cette étape');
        }
      }

      function closeDeepContent() {
        episodesRoot.dataset.audioFirstDetailsOpen = '0';
        episodesRoot.querySelectorAll('.audio-first-current-detail').forEach(card => card.classList.remove('audio-first-current-detail'));
      }

      function revealCard(kind = 'detail') {
        const {episode} = currentItem();
        const card = document.getElementById(episode.id);
        if (!card) return;
        episodesRoot.dataset.audioFirstDetailsOpen = '1';
        episodesRoot.querySelectorAll('.audio-first-current-detail').forEach(item => item.classList.remove('audio-first-current-detail'));
        card.classList.add('audio-first-current-detail');
        card.scrollIntoView({behavior:'smooth', block:'start'});
        if (kind === 'transcript') {
          const transcript = card.querySelector('[data-transcript]');
          if (transcript) transcript.click();
        }
      }

      function openJourney() {
        document.querySelector('[data-journey-open]')?.click();
      }

      function renderStage() {
        closeDeepContent();
        arrived = false;
        const {episode, index, field} = currentItem();
        const route = episode.maps_url
          ? `<a class="secondary audio-first-route" target="_blank" rel="noopener" href="${esc(episode.maps_url)}">Itinéraire</a>`
          : '<span class="secondary is-disabled" aria-disabled="true">Itinéraire</span>';
        const help = episode.maps_url
          ? `<a target="_blank" rel="noopener" href="${esc(episode.maps_url)}">Je ne trouve pas</a>`
          : '';
        const sources = (field.sources || []).filter(Boolean);
        stage.innerHTML = `
          <div class="audio-first-heading">
            <p class="audio-first-kicker">Étape ${index + 1}/${episodes.length}</p>
            <h2>${esc(concise(episode.stop || episode.location || episode.title, 100))}</h2>
          </div>
          <p class="audio-first-cue"><strong>À regarder</strong><span>${esc(primaryCue(episode, field))}</span></p>
          <div class="audio-first-primary-actions">
            <button class="primary audio-first-listen" type="button" data-audio-first-toggle>▶ Écouter</button>
            ${route}
            <button class="secondary" type="button" data-audio-first-arrived aria-pressed="false">J’y suis</button>
            <button class="secondary" type="button" data-audio-first-continue ${cursor >= fieldIndexes.length - 1 ? 'disabled' : ''}>Continuer</button>
          </div>
          <p class="audio-first-state" data-audio-first-state>${arrived ? 'Sur place · regardez avant de poursuivre.' : 'Écoutez, regardez, puis agissez.'}</p>
          <details class="audio-first-more">
            <summary>Plus</summary>
            <div class="audio-first-secondary-actions">
              ${help}
              <button type="button" data-audio-first-detail>Approfondir</button>
              ${episode.transcript_url ? '<button type="button" data-audio-first-transcript>Transcription</button>' : '<span class="is-muted">Transcription indisponible</span>'}
              ${sources.length ? `<details class="audio-first-sources"><summary>Sources</summary><ul>${sources.map((source, i) => `<li><a target="_blank" rel="noopener" href="${esc(source)}">Source ${i + 1}</a></li>`).join('')}</ul></details>` : '<span class="is-muted">Sources dans la transcription</span>'}
              <button type="button" data-audio-first-journey>Toutes les étapes</button>
              <a href="${esc(audioFirst.classic_fallback_url)}" data-audio-first-classic>Version classique V1</a>
            </div>
          </details>`;
        syncAudioButton();
      }

      stage.addEventListener('click', event => {
        const toggleAudio = event.target.closest('[data-audio-first-toggle]');
        if (toggleAudio) {
          const {episode} = currentItem();
          if (!episode.audio_url || episode.state === 'failed') return;
          if (audioMatches(episode) && playerToggle) {
            playerToggle.click();
          } else {
            document.getElementById(episode.id)?.querySelector('[data-play]')?.click();
          }
          setTimeout(syncAudioButton, 0);
          return;
        }

        const arrival = event.target.closest('[data-audio-first-arrived]');
        if (arrival) {
          arrived = !arrived;
          arrival.setAttribute('aria-pressed', arrived ? 'true' : 'false');
          arrival.textContent = arrived ? '✓ J’y suis' : 'J’y suis';
          const status = stage.querySelector('[data-audio-first-state]');
          if (status) status.textContent = arrived ? 'Sur place · regardez avant de poursuivre.' : 'Écoutez, regardez, puis agissez.';
          return;
        }

        if (event.target.closest('[data-audio-first-continue]')) {
          const {episode} = currentItem();
          if (audioMatches(episode) && playerAudio && !playerAudio.paused && playerToggle) playerToggle.click();
          if (cursor < fieldIndexes.length - 1) {
            cursor += 1;
            renderStage();
            stage.scrollIntoView({behavior:'smooth', block:'start'});
          }
          return;
        }

        if (event.target.closest('[data-audio-first-detail]')) {
          revealCard('detail');
          return;
        }

        if (event.target.closest('[data-audio-first-transcript]')) {
          revealCard('transcript');
          return;
        }

        if (event.target.closest('[data-audio-first-journey]')) {
          openJourney();
        }
      });

      document.addEventListener('click', event => {
        const journey = event.target.closest?.('[data-journey-episode]');
        if (!journey) return;
        const nextCursor = fieldIndexes.findIndex(item => item.episode.id === journey.dataset.journeyEpisode);
        if (nextCursor < 0) return;
        event.preventDefault();
        const {episode} = currentItem();
        if (audioMatches(episode) && playerAudio && !playerAudio.paused && playerToggle) playerToggle.click();
        cursor = nextCursor;
        renderStage();
        stage.scrollIntoView({behavior:'smooth', block:'start'});
      });

      if (playerAudio) {
        ['play', 'pause', 'ended', 'loadedmetadata'].forEach(name => playerAudio.addEventListener(name, syncAudioButton));
      }

      renderStage();
      return false;
    }

    function enhance() {
      return audioFirst ? setupAudioFirst() : enhanceLegacy();
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
      .cue strong{font-size:.82rem;color:#183d49}.cue-silence,.cue-micro_silence{border-left-color:#b58a5d;background:#fbf7f1}.cue-user_pause{border-left-color:#8a5a2b;background:#fff8ed}.cue-user_pause strong{font-weight:900}.cue-reveal{border-left-color:#6d82a8}.cue-look{border-left-color:#678f76}
      @media (max-width:640px){.visit-now{margin-left:-.15rem;margin-right:-.15rem}.visit-now-actions>*{flex:1 1 8rem;text-align:center}.cue{grid-template-columns:1fr;gap:.15rem}}
    `;
    document.head.appendChild(style);
  }

  function injectAudioFirstStyles() {
    if (document.getElementById('audio-first-v2-styles')) return;
    const style = document.createElement('style');
    style.id = 'audio-first-v2-styles';
    style.textContent = `
      #app.audio-first-v2 .visit-strip,
      #app.audio-first-v2 .series-hero .start,
      #app.audio-first-v2 .series-hero > p:not(.eyebrow),
      #app.audio-first-v2 .episodes,
      #app.audio-first-v2 > footer{display:none}
      #app.audio-first-v2 .series-hero{padding-bottom:.65rem}
      #app.audio-first-v2 .series-hero h1{font-size:clamp(1.45rem,5vw,2rem);margin-bottom:.35rem}
      #app.audio-first-v2 .audio-first-stage{margin:0 0 1rem;padding:1rem;border:2px solid #183d49;background:#f7fbfb}
      .audio-first-heading{display:grid;gap:.2rem}.audio-first-heading h2{margin:0;font-size:clamp(1.35rem,5vw,1.9rem);line-height:1.15}
      .audio-first-kicker{margin:0;text-transform:uppercase;letter-spacing:.08em;font-size:.78rem;font-weight:850;color:#183d49}
      .audio-first-cue{display:grid;gap:.3rem;margin:.9rem 0;padding:.9rem;border-radius:.75rem;background:#eef5f3;font-size:1.06rem;line-height:1.45}
      .audio-first-cue strong{text-transform:uppercase;letter-spacing:.06em;font-size:.75rem;color:#183d49}
      .audio-first-primary-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.55rem}
      .audio-first-primary-actions>*{min-height:3.15rem;display:flex;align-items:center;justify-content:center;text-align:center}
      .audio-first-listen{grid-column:1/-1;font-size:1.08rem;font-weight:850}
      .audio-first-state{margin:.7rem 0 .35rem;color:#536366;font-size:.9rem}
      .audio-first-more{margin-top:.5rem;border-top:1px solid #d9e2e2;padding-top:.55rem}
      .audio-first-more>summary{cursor:pointer;font-weight:750}
      .audio-first-secondary-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.45rem;margin-top:.55rem}
      .audio-first-secondary-actions>a,.audio-first-secondary-actions>button,.audio-first-secondary-actions>span,.audio-first-sources{min-height:2.7rem;padding:.55rem .65rem;border:1px solid #c8d4d2;border-radius:.55rem;background:#fff;color:inherit;text-decoration:none;font:inherit}
      .audio-first-secondary-actions>a,.audio-first-secondary-actions>button{cursor:pointer;text-align:left}
      .audio-first-sources{grid-column:1/-1}.audio-first-sources summary{cursor:pointer}.audio-first-sources ul{margin:.5rem 0 0;padding-left:1.2rem}
      .is-disabled{opacity:.55;pointer-events:none}.is-muted{color:#6c7778}
      #app.audio-first-v2 .episodes[data-audio-first-details-open="1"]{display:block}
      #app.audio-first-v2 .episodes[data-audio-first-details-open="1"] .episode{display:none}
      #app.audio-first-v2 .episodes[data-audio-first-details-open="1"] .episode.audio-first-current-detail{display:block}
      #app.audio-first-v2 .episode.audio-first-current-detail{margin-top:.8rem}
      @media(max-width:640px){
        #app.audio-first-v2 .audio-first-stage{margin-left:-.15rem;margin-right:-.15rem}
        .audio-first-primary-actions,.audio-first-secondary-actions{grid-template-columns:1fr 1fr}
      }
    `;
    document.head.appendChild(style);
  }

  load().catch(() => {});
})();
