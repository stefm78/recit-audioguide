(() => {
  const startedAt = Date.now();
  const events = [];
  const maxEvents = 100;
  let currentStage = 'Ouverture du guide';
  let failed = false;

  function nowMs(){ return Date.now() - startedAt; }
  function safe(value){
    try { return JSON.parse(JSON.stringify(value)); }
    catch (_) { return String(value); }
  }
  function push(level, stage, data){
    currentStage = stage || currentStage;
    events.push({t_ms: nowMs(), level, stage: currentStage, data: safe(data ?? null)});
    if(events.length > maxEvents) events.splice(0, events.length - maxEvents);
    render();
  }
  function snapshot(){
    return {
      schema: 'recit.android.field-runtime.v1',
      app: '00 Récit Séville Field',
      href: location.href,
      origin: location.origin,
      userAgent: navigator.userAgent,
      slug: window.RECIT_SERIES_SLUG || null,
      embeddedSeries: Boolean(window.RECIT_SERIES_DATA),
      episodeCount: Array.isArray(window.RECIT_SERIES_DATA?.episodes) ? window.RECIT_SERIES_DATA.episodes.length : null,
      playableCount: Array.isArray(window.RECIT_SERIES_DATA?.episodes) ? window.RECIT_SERIES_DATA.episodes.filter(e => e?.audio_url && e?.state !== 'failed').length : null,
      firstAudioUrl: window.RECIT_SERIES_DATA?.episodes?.find(e => e?.audio_url && e?.state !== 'failed')?.audio_url || null,
      ready: document.documentElement.dataset.recitSeriesReady === '1',
      currentStage,
      elapsedMs: nowMs(),
      events: events.slice()
    };
  }
  async function copyDiagnostic(){
    const text = JSON.stringify(snapshot(), null, 2);
    try {
      await navigator.clipboard.writeText(text);
      push('info', 'Diagnostic copié', {bytes:text.length});
      return;
    } catch (_) {}
    const area = document.createElement('textarea');
    area.value = text;
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    try { document.execCommand('copy'); } catch (_) {}
    area.remove();
    push('info', 'Diagnostic prêt à copier', {bytes:text.length});
  }
  function render(){
    const root = document.getElementById('app');
    if(!root || document.documentElement.dataset.recitSeriesReady === '1') return;
    if(root.querySelector('[data-episode]')) return;
    const elapsed = (nowMs()/1000).toFixed(1);
    const recent = events.slice(-6).map(e => `<li><strong>${Math.round(e.t_ms)} ms</strong> — ${escapeHtml(e.stage)}</li>`).join('');
    root.innerHTML = `<section class="card" id="recit-field-status"><p class="eyebrow">Initialisation du guide</p><h1>${failed ? 'Le guide ne démarre pas' : escapeHtml(currentStage)}</h1><p>${failed ? 'Une étape a échoué. Le diagnostic ci-dessous permet d’identifier précisément où.' : `Temps écoulé : ${elapsed} s`}</p><ol>${recent}</ol><details ${failed ? 'open' : ''}><summary>Diagnostic technique</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere;font-size:.75rem">${escapeHtml(JSON.stringify(snapshot(), null, 2))}</pre></details><button type="button" id="recit-copy-diagnostic">Copier le diagnostic</button>${failed ? '<p><button type="button" onclick="location.reload()">Réessayer</button></p>' : ''}</section>`;
    document.getElementById('recit-copy-diagnostic')?.addEventListener('click', copyDiagnostic, {once:true});
  }
  function escapeHtml(value){
    return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  window.RECIT_DIAG = {
    step(stage, data){ push('info', stage, data); },
    warn(stage, data){ push('warn', stage, data); },
    fail(stage, data){ failed = true; push('error', stage, data); },
    ready(data){ document.documentElement.dataset.recitSeriesReady = '1'; push('info', 'Guide prêt', data); },
    snapshot,
    copy: copyDiagnostic
  };

  window.addEventListener('error', event => {
    if(event.target && event.target !== window){
      window.RECIT_DIAG.fail('Ressource impossible à charger', {tag:event.target.tagName, src:event.target.src || event.target.href || null});
      return;
    }
    window.RECIT_DIAG.fail('Erreur JavaScript', {message:event.message, filename:event.filename, line:event.lineno, column:event.colno, stack:event.error?.stack || null});
  }, true);
  window.addEventListener('unhandledrejection', event => {
    window.RECIT_DIAG.fail('Promise rejetée sans gestion', {reason:event.reason?.stack || event.reason?.message || String(event.reason)});
  });

  window.RECIT_DIAG.step('Moniteur terrain actif', {href:location.href, origin:location.origin});
  setTimeout(() => {
    if(document.documentElement.dataset.recitSeriesReady !== '1'){
      window.RECIT_DIAG.fail('Timeout d’initialisation après 8 secondes', snapshot());
    }
  }, 8000);
})();
