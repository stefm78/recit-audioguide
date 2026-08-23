(() => {
  const slug = window.RECIT_SERIES_SLUG;
  const root = document.getElementById('app');
  const player = document.getElementById('player');
  const audio = document.getElementById('player-audio');
  const toggle = document.getElementById('player-toggle');
  const playerTitle = document.getElementById('player-title');
  const playerSubtitle = document.getElementById('player-subtitle');
  let series, currentEpisode;

  boot();

  async function boot(){
    try {
      const r = await fetch(`../../data/${encodeURIComponent(slug)}/series.json`, {cache:'no-store'});
      if(!r.ok) throw new Error(`HTTP ${r.status}`);
      series = await r.json();
      document.title = `${series.title} — Récit audioguide`;
      render(series);
      restore(series);
    } catch(e) {
      root.innerHTML = '<section class="card"><h1>Récit indisponible</h1><p>Cette série ne peut pas être chargée pour le moment.</p><p><a href="../../">Retour aux voyages</a></p></section>';
    }
  }

  function render(s){
    root.className = `series-shell mode-${s.type}`;
    root.innerHTML = `${hero(s)}${s.type==='visit' ? visitNav(s) : ''}${s.type==='route' ? routeIntro(s) : ''}<section class="episodes">${s.episodes.map(episodeCard).join('')}</section><footer><a href="../../">← Tous les voyages</a></footer>`;
    root.addEventListener('click', onClick);
  }

  function hero(s){
    const action = s.episodes[0] ? `<button class="primary start" data-play="${escAttr(s.episodes[0].id)}">▶ Commencer</button>` : '';
    return `<header class="series-hero"><p class="eyebrow">${modeLabel(s.type)}</p><h1>${esc(s.title)}</h1><p>${esc(s.subtitle||'')}</p>${action}${s.note ? `<p class="quiet">${esc(s.note)}</p>`:''}</header>`;
  }

  function visitNav(s){
    if(!s.visit) return '';
    const steps = s.episodes.map((e,i)=>`<a href="#${escAttr(e.id)}" aria-label="Étape ${i+1}">${i+1}</a>`).join('');
    const plan = s.visit.plan_url ? `<img class="visit-plan" src="${escAttr(s.visit.plan_url)}" alt="Plan simplifié de la visite">` : '';
    return `<section class="visit-strip"><strong>${esc(s.visit.start_label || 'Parcours')}</strong>${plan}<nav>${steps}</nav></section>`;
  }

  function routeIntro(s){
    return `<section class="safety card"><strong>En voiture</strong><p>${esc(s.route?.safety || 'Le GPS et les conditions réelles priment. Les détails visuels sont destinés aux passagers ou aux arrêts.')}</p>${s.route?.maps_url ? `<a class="secondary" target="_blank" rel="noopener" href="${escAttr(s.route.maps_url)}">Ouvrir l’itinéraire</a>`:''}</section>`;
  }

  function episodeCard(e, index){
    const look = e.look ? `<p class="look"><strong>Regardez :</strong> ${esc(e.look)}</p>`:'';
    const maps = e.maps_url ? `<a class="secondary" href="${escAttr(e.maps_url)}" target="_blank" rel="noopener">Y aller</a>`:'';
    const transcript = e.transcript_url ? `<button class="secondary" data-transcript="${escAttr(e.id)}">Transcription et sources</button>`:'';
    const extras = (e.extras||[]).map(x=>`<details class="extra"><summary>${esc(x.title)}</summary><p>${esc(x.summary||'')}</p>${x.audio_url?`<button class="secondary" data-external-play="${escAttr(x.audio_url)}" data-title="${escAttr(x.title)}">▶ Écouter</button>`:''}</details>`).join('');
    return `<article id="${escAttr(e.id)}" class="episode card" data-episode="${escAttr(e.id)}"><div class="episode-top"><span class="number">${index+1}</span><div><small>${esc(e.stop||'')}</small><h2>${esc(e.title)}</h2></div></div>${e.launch?`<p class="launch">${esc(e.launch)}</p>`:''}<p>${esc(e.summary||'')}</p>${look}<button class="primary" data-play="${escAttr(e.id)}">▶ Écouter</button><div class="actions">${maps}${transcript}</div><div class="transcript" data-transcript-box="${escAttr(e.id)}" hidden></div>${extras}</article>`;
  }

  function onClick(ev){
    const play = ev.target.closest('[data-play]');
    if(play){ const e = series.episodes.find(x=>x.id===play.dataset.play); if(e) playEpisode(e); return; }
    const external = ev.target.closest('[data-external-play]');
    if(external){ playUrl({id:'extra',title:external.dataset.title,stop:'Bonus',audio_url:external.dataset.externalPlay}); return; }
    const transcript = ev.target.closest('[data-transcript]');
    if(transcript){ const e=series.episodes.find(x=>x.id===transcript.dataset.transcript); if(e) toggleTranscript(e, transcript); }
  }

  function playEpisode(e){ playUrl(e); currentEpisode=e; saveProgress(); }
  function playUrl(e){
    if(!e.audio_url) return;
    audio.src=e.audio_url;
    player.hidden=false;
    playerTitle.textContent=e.title;
    playerSubtitle.textContent=e.stop||series.title;
    audio.play().catch(()=>{});
    toggle.textContent='❚❚';
    currentEpisode=e;
    if('mediaSession' in navigator){
      navigator.mediaSession.metadata = new MediaMetadata({title:e.title,artist:'Récit audioguide',album:series.title});
      navigator.mediaSession.setActionHandler('play',()=>audio.play());
      navigator.mediaSession.setActionHandler('pause',()=>audio.pause());
      try{navigator.mediaSession.setActionHandler('seekbackward',()=>{audio.currentTime=Math.max(0,audio.currentTime-15)});navigator.mediaSession.setActionHandler('seekforward',()=>{audio.currentTime=Math.min(audio.duration||Infinity,audio.currentTime+15)});}catch(_){}
    }
  }

  toggle.addEventListener('click',()=>{ if(audio.paused) audio.play(); else audio.pause(); });
  audio.addEventListener('play',()=>toggle.textContent='❚❚');
  audio.addEventListener('pause',()=>toggle.textContent='▶');
  audio.addEventListener('timeupdate',()=>{ if(currentEpisode && Math.floor(audio.currentTime)%5===0) saveProgress(); });
  audio.addEventListener('ended',()=>{ if(currentEpisode){markDone(currentEpisode.id); const i=series.episodes.findIndex(x=>x.id===currentEpisode.id); const next=i>=0?series.episodes[i+1]:null; if(next) playerSubtitle.textContent=`Terminé · suite : ${next.title}`; }});

  async function toggleTranscript(e, button){
    const box=root.querySelector(`[data-transcript-box="${cssEscape(e.id)}"]`);
    if(box.dataset.loaded==='1'){box.hidden=!box.hidden;return;}
    button.disabled=true;
    try{
      const r=await fetch(e.transcript_url); if(!r.ok) throw new Error(); const d=await r.json();
      const segments=d.segments || d.guide?.segments || d.resolved_segments || [];
      const sources=d.sources || d.guide?.sources || [];
      box.innerHTML=`${segments.map(s=>`<p><strong>${esc(s.speaker||'Narrateur')} :</strong> ${esc(s.text||'')}</p>`).join('')}${sources.length?`<h3>Sources</h3><ul>${sources.map(u=>`<li><a href="${escAttr(u)}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('')}</ul>`:''}`;
      box.dataset.loaded='1';box.hidden=false;
    }catch(_){box.innerHTML='<p>La transcription n’est pas disponible. L’audio reste accessible.</p>';box.hidden=false;}finally{button.disabled=false;}
  }

  function saveProgress(){
    if(!series||!currentEpisode)return;
    localStorage.setItem(`recit:${series.slug}`,JSON.stringify({episode:currentEpisode.id,time:audio.currentTime||0,updated:Date.now()}));
  }
  function markDone(id){localStorage.setItem(`recit:done:${series.slug}:${id}`,'1');}
  function restore(s){
    try{const p=JSON.parse(localStorage.getItem(`recit:${s.slug}`)||'null');if(!p)return;const e=s.episodes.find(x=>x.id===p.episode);if(!e)return;const b=document.createElement('button');b.className='resume';b.textContent=`Continuer · ${e.title}`;b.addEventListener('click',()=>{playEpisode(e);audio.addEventListener('loadedmetadata',()=>{audio.currentTime=Math.min(p.time||0,audio.duration||p.time||0)},{once:true});});root.querySelector('.series-hero').appendChild(b);}catch(_){}
  }

  function modeLabel(t){return ({story:'Histoire',visit:'Visite',route:'Route'})[t]||'Récit';}
  function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function escAttr(s){return esc(s);}
  function cssEscape(s){return (window.CSS&&CSS.escape)?CSS.escape(s):String(s).replace(/"/g,'\\"');}
})();
