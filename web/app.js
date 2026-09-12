(() => {
  const slug = window.RECIT_SERIES_SLUG;
  const root = document.getElementById('app');
  const player = document.getElementById('player');
  const audio = document.getElementById('player-audio');
  const toggle = document.getElementById('player-toggle');
  const back = document.getElementById('player-back');
  const forward = document.getElementById('player-forward');
  const seek = document.getElementById('player-seek');
  const currentTimeLabel = document.getElementById('player-current');
  const durationLabel = document.getElementById('player-duration');
  const playerTitle = document.getElementById('player-title');
  const playerSubtitle = document.getElementById('player-subtitle');
  let series, currentEpisode;
  let lastSavedSecond = -5;
  let lastNativePositionSecond = -1;
  let bootComplete = false;
  let userResumeRequired = false;
  let playAuthorizationUntil = 0;
  let nativeMediaConfigured = false;
  let journeyDrawer = null;
  let journeyBackdrop = null;
  let journeyDrawerSide = 'left';

  const bootWatchdog = setTimeout(() => {
    if (bootComplete) return;
    console.error('Récit series bootstrap timeout', {slug, href: location.href, embedded: Boolean(window.RECIT_SERIES_DATA)});
    root.innerHTML = '<section class="card"><h1>Le guide ne démarre pas</h1><p>Le contenu local est présent mais son initialisation a échoué.</p><p><button type="button" onclick="location.reload()">Réessayer</button></p><p><a href="../../">Retour aux voyages</a></p></section>';
  }, 5000);

  boot();

  async function boot(){
    try {
      const embedded = window.RECIT_SERIES_DATA;
      if (embedded && embedded.slug === slug && Array.isArray(embedded.episodes)) {
        series = embedded;
      } else {
        const r = await fetch(`../../data/${encodeURIComponent(slug)}/series.json`, {cache:'no-store'});
        if(!r.ok) throw new Error(`HTTP ${r.status}`);
        series = await r.json();
      }
      if(!series || !Array.isArray(series.episodes)) throw new Error('series payload invalid');
      document.title = `${series.title} — Récit audioguide`;
      render(series);
      restore(series);
      await configureMediaActions();
      bootComplete = true;
      clearTimeout(bootWatchdog);
      document.documentElement.dataset.recitSeriesReady = '1';
    } catch(e) {
      bootComplete = true;
      clearTimeout(bootWatchdog);
      console.error('Récit series bootstrap failed', e);
      root.innerHTML = '<section class="card"><h1>Récit indisponible</h1><p>Cette série ne peut pas être chargée pour le moment.</p><p><button type="button" onclick="location.reload()">Réessayer</button></p><p><a href="../../">Retour aux voyages</a></p></section>';
    }
  }

  function isPlayable(e){ return Boolean(e && e.audio_url && e.state!=='failed'); }

  function render(s){
    root.className = `series-shell mode-${s.type}`;
    root.innerHTML = `${hero(s)}${s.type==='visit' ? visitNav(s) : ''}${s.type==='route' ? routeIntro(s) : ''}<section class="episodes">${s.episodes.map(episodeCard).join('')}</section><footer><a href="../../">← Tous les voyages</a></footer>`;
    root.addEventListener('click', onClick);
    setupJourneyDrawer(s);
    refreshJourneyUi();
  }

  function hero(s){
    const first = s.episodes.find(isPlayable);
    const action = first ? `<button class="primary start" data-play="${escAttr(first.id)}">▶ Commencer</button>` : '<p class="quiet">Les audios de cette série sont momentanément indisponibles.</p>';
    return `<header class="series-hero"><p class="eyebrow">${modeLabel(s.type)}</p><h1>${esc(s.title)}</h1><p>${esc(s.subtitle||'')}</p>${action}<button class="secondary journey-menu-button" type="button" data-journey-open aria-controls="journey-drawer" aria-expanded="false">☰ Parcours · ${s.episodes.length} étapes</button>${s.note ? `<p class="quiet">${esc(s.note)}</p>`:''}</header>`;
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
    const play = isPlayable(e) ? `<button class="primary" data-play="${escAttr(e.id)}">▶ Écouter</button>` : '<p class="quiet">Audio momentanément indisponible.</p>';
    return `<article id="${escAttr(e.id)}" class="episode card" data-episode="${escAttr(e.id)}"><div class="episode-top"><span class="number">${index+1}</span><div><small>${esc(e.stop||'')}</small><h2>${esc(e.title)}</h2><span class="journey-card-status" data-journey-card-status="${escAttr(e.id)}"></span></div></div>${e.launch?`<p class="launch">${esc(e.launch)}</p>`:''}<p>${esc(e.summary||'')}</p>${look}${play}<div class="actions">${maps}${transcript}</div><div class="transcript" data-transcript-box="${escAttr(e.id)}" hidden></div>${extras}</article>`;
  }

  function onClick(ev){
    const drawerOpen = ev.target.closest('[data-journey-open]');
    if(drawerOpen){ openJourneyDrawer('left'); return; }
    const play = ev.target.closest('[data-play]');
    if(play){ const e = series.episodes.find(x=>x.id===play.dataset.play); if(isPlayable(e)) playEpisode(e); return; }
    const external = ev.target.closest('[data-external-play]');
    if(external){ playUrl({id:'extra',title:external.dataset.title,stop:'Bonus',audio_url:external.dataset.externalPlay}); return; }
    const transcript = ev.target.closest('[data-transcript]');
    if(transcript){ const e=series.episodes.find(x=>x.id===transcript.dataset.transcript); if(e) toggleTranscript(e, transcript); }
  }

  function playEpisode(e){ if(!isPlayable(e)) return; playUrl(e); saveProgress(); }

  function playUrl(e){
    if(!e.audio_url) return;
    audio.src=e.audio_url;
    player.hidden=false;
    playerTitle.textContent=e.title;
    playerSubtitle.textContent=e.stop||series.title;
    currentEpisode=e;
    lastSavedSecond=-5;
    lastNativePositionSecond=-1;
    resetPlayerTime();
    mediaSetMetadata(e);
    requestPlay('episode').catch(err=>console.warn('Audio playback did not start automatically', err));
    refreshJourneyUi();
  }

  function authorizePlay(){ playAuthorizationUntil=Date.now()+1200; }
  function playIsAuthorized(){ return Date.now()<=playAuthorizationUntil; }

  async function requestPlay(source='ui'){
    authorizePlay();
    try{
      await audio.play();
    }catch(err){
      console.warn(`Audio play failed (${source})`,err);
      throw err;
    }
  }

  function requestPause(source='ui'){
    userResumeRequired=true;
    audio.pause();
    window.RECIT_DIAG?.step?.('Pause demandée',{source});
  }

  function nativeMediaSession(){
    const cap=window.Capacitor;
    const platform=cap?.getPlatform?.() || cap?.platform;
    if(platform!=='android') return null;
    return cap?.Plugins?.MediaSession || null;
  }

  async function configureMediaActions(){
    const native=nativeMediaSession();
    if(native && !nativeMediaConfigured){
      const bind=async(action,handler)=>native.setActionHandler({action},handler);
      await bind('play',()=>{requestPlay('native-media').catch(()=>{});});
      await bind('pause',()=>requestPause('native-media'));
      await bind('seekbackward',()=>seekBy(-15));
      await bind('seekforward',()=>seekBy(15));
      await bind('seekto',details=>{
        if(!Number.isFinite(details?.seekTime)) return;
        const target=clampTime(details.seekTime);
        if('fastSeek' in audio) audio.fastSeek(target); else audio.currentTime=target;
        syncPlayerTime(true);
        saveProgress();
      });
      nativeMediaConfigured=true;
      window.RECIT_DIAG?.step?.('Media Session Android native prête');
      return;
    }
    if('mediaSession' in navigator){
      try{
        navigator.mediaSession.setActionHandler('play',()=>{requestPlay('web-media').catch(()=>{});});
        navigator.mediaSession.setActionHandler('pause',()=>requestPause('web-media'));
        navigator.mediaSession.setActionHandler('seekbackward',()=>seekBy(-15));
        navigator.mediaSession.setActionHandler('seekforward',()=>seekBy(15));
        navigator.mediaSession.setActionHandler('seekto',details=>{
          if(!Number.isFinite(details?.seekTime)) return;
          const target=clampTime(details.seekTime);
          if(details.fastSeek && 'fastSeek' in audio) audio.fastSeek(target); else audio.currentTime=target;
          syncPlayerTime(true);
          saveProgress();
        });
      }catch(_){}
    }
  }

  function mediaSetMetadata(e){
    const native=nativeMediaSession();
    if(native){
      native.setMetadata({title:e.title,artist:'Récit audioguide',album:series.title}).catch(err=>console.warn('Native media metadata failed',err));
      return;
    }
    if('mediaSession' in navigator){
      try{if(typeof MediaMetadata==='function')navigator.mediaSession.metadata=new MediaMetadata({title:e.title,artist:'Récit audioguide',album:series.title});}catch(_){}
    }
  }

  function mediaSetPlaybackState(state){
    const native=nativeMediaSession();
    if(native){native.setPlaybackState({playbackState:state}).catch(err=>console.warn('Native media state failed',err));return;}
    if('mediaSession' in navigator){try{navigator.mediaSession.playbackState=state;}catch(_){}}
  }

  function mediaSetPositionState(force=false){
    const current=Number.isFinite(audio.currentTime)?audio.currentTime:0;
    const duration=Number.isFinite(audio.duration)&&audio.duration>0?audio.duration:0;
    if(!duration)return;
    const second=Math.floor(current);
    if(!force && second===lastNativePositionSecond)return;
    lastNativePositionSecond=second;
    const payload={duration,playbackRate:audio.playbackRate||1,position:Math.min(current,duration)};
    const native=nativeMediaSession();
    if(native){native.setPositionState(payload).catch(err=>console.warn('Native media position failed',err));return;}
    if('mediaSession' in navigator){try{navigator.mediaSession.setPositionState(payload);}catch(_){}}
  }

  function clampTime(value){
    const duration=Number.isFinite(audio.duration) ? audio.duration : Math.max(0,Number(value)||0);
    return Math.max(0,Math.min(duration,Number(value)||0));
  }

  function seekBy(seconds){
    if(!Number.isFinite(audio.currentTime)) return;
    audio.currentTime=clampTime(audio.currentTime+seconds);
    syncPlayerTime(true);
    saveProgress();
  }

  function formatTime(seconds){
    const total=Math.max(0,Math.floor(Number(seconds)||0));
    const hours=Math.floor(total/3600);
    const minutes=Math.floor((total%3600)/60);
    const secs=total%60;
    return hours ? `${hours}:${String(minutes).padStart(2,'0')}:${String(secs).padStart(2,'0')}` : `${minutes}:${String(secs).padStart(2,'0')}`;
  }

  function resetPlayerTime(){
    seek.disabled=true;
    seek.min='0'; seek.max='0'; seek.value='0';
    currentTimeLabel.textContent='0:00';
    durationLabel.textContent='0:00';
  }

  function syncPlayerTime(forceMedia=false){
    const current=Number.isFinite(audio.currentTime) ? audio.currentTime : 0;
    const duration=Number.isFinite(audio.duration) && audio.duration>0 ? audio.duration : 0;
    currentTimeLabel.textContent=formatTime(current);
    durationLabel.textContent=formatTime(duration);
    seek.disabled=!duration;
    seek.max=String(duration||0);
    seek.value=String(duration ? Math.min(current,duration) : 0);
    seek.setAttribute('aria-valuetext',`${formatTime(current)} sur ${formatTime(duration)}`);
    mediaSetPositionState(forceMedia);
  }

  back.addEventListener('click',()=>seekBy(-15));
  forward.addEventListener('click',()=>seekBy(15));
  toggle.addEventListener('click',()=>{ if(audio.paused) requestPlay('player').catch(()=>{}); else requestPause('player'); });
  seek.addEventListener('input',()=>{ if(!seek.disabled){ audio.currentTime=clampTime(Number(seek.value)); syncPlayerTime(true); }});
  seek.addEventListener('change',saveProgress);
  audio.addEventListener('loadedmetadata',syncPlayerTime);
  audio.addEventListener('durationchange',()=>syncPlayerTime(true));
  audio.addEventListener('play',()=>{
    if(userResumeRequired && !playIsAuthorized()){
      window.RECIT_DIAG?.step?.('Reprise automatique bloquée après interruption');
      queueMicrotask(()=>{if(!audio.paused)audio.pause();});
      return;
    }
    userResumeRequired=false;
    toggle.textContent='❚❚';
    mediaSetPlaybackState('playing');
    refreshJourneyUi();
  });
  audio.addEventListener('pause',()=>{
    userResumeRequired=true;
    toggle.textContent='▶';
    mediaSetPlaybackState('paused');
    saveProgress();
    refreshJourneyUi();
  });
  audio.addEventListener('timeupdate',()=>{
    syncPlayerTime();
    if(currentEpisode && audio.currentTime-lastSavedSecond>=5){lastSavedSecond=audio.currentTime;saveProgress();}
  });
  audio.addEventListener('ended',()=>{
    if(!currentEpisode)return;
    const i=series.episodes.findIndex(x=>x.id===currentEpisode.id);
    if(i<0)return;
    markDone(currentEpisode.id);
    mediaSetPlaybackState('paused');
    const next=series.episodes.slice(i+1).find(isPlayable);
    if(next) playerSubtitle.textContent=`Terminé · suite : ${next.title}`;
    refreshJourneyUi();
  });

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

  function progressSnapshot(s=series){
    try{return JSON.parse(localStorage.getItem(`recit:${s.slug}`)||'null');}catch(_){return null;}
  }

  function saveProgress(){
    if(!series||!currentEpisode||!series.episodes.some(e=>e.id===currentEpisode.id))return;
    localStorage.setItem(`recit:${series.slug}`,JSON.stringify({episode:currentEpisode.id,time:audio.currentTime||0,updated:Date.now()}));
    refreshJourneyUi();
  }
  function markDone(id){localStorage.setItem(`recit:done:${series.slug}:${id}`,'1');}
  function isDone(id){return localStorage.getItem(`recit:done:${series.slug}:${id}`)==='1';}

  function restore(s){
    try{
      const p=progressSnapshot(s);if(!p)return;
      const e=s.episodes.find(x=>x.id===p.episode);if(!isPlayable(e))return;
      const index=s.episodes.findIndex(x=>x.id===e.id)+1;
      const b=document.createElement('button');
      b.className='resume';
      b.textContent=`Continuer · étape ${index} · ${formatTime(p.time||0)}`;
      b.setAttribute('aria-label',`Reprendre ${e.title} à ${formatTime(p.time||0)}`);
      b.addEventListener('click',()=>{
        playEpisode(e);
        audio.addEventListener('loadedmetadata',()=>{audio.currentTime=Math.min(p.time||0,audio.duration||p.time||0);syncPlayerTime(true);},{once:true});
      });
      root.querySelector('.series-hero').appendChild(b);
    }catch(_){}
  }

  function episodeJourneyState(e){
    if(isDone(e.id))return {kind:'done',label:'Écouté'};
    const p=progressSnapshot();
    if(p?.episode===e.id && Number(p.time)>0)return {kind:'current',label:`À reprendre · ${formatTime(p.time)}`};
    if(currentEpisode?.id===e.id)return {kind:'current',label:audio.paused?'En pause':'En cours'};
    return {kind:'todo',label:'À découvrir'};
  }

  function setupJourneyDrawer(s){
    document.getElementById('journey-drawer')?.remove();
    document.querySelector('.journey-backdrop')?.remove();
    journeyBackdrop=document.createElement('div');
    journeyBackdrop.className='journey-backdrop';
    journeyBackdrop.hidden=true;
    journeyBackdrop.addEventListener('click',closeJourneyDrawer);
    journeyDrawer=document.createElement('aside');
    journeyDrawer.id='journey-drawer';
    journeyDrawer.className='journey-drawer';
    journeyDrawer.setAttribute('aria-label','Navigation du parcours');
    journeyDrawer.setAttribute('aria-hidden','true');
    const links=s.episodes.map((e,i)=>`<a class="journey-item" href="#${escAttr(e.id)}" data-journey-episode="${escAttr(e.id)}"><span class="journey-number">${i+1}</span><span><small>${esc(e.stop||`Étape ${i+1}`)}</small><strong>${esc(e.title)}</strong><em data-journey-status="${escAttr(e.id)}"></em></span></a>`).join('');
    journeyDrawer.innerHTML=`<div class="journey-drawer-head"><div><small>Parcours</small><strong>${esc(s.title)}</strong></div><button type="button" class="journey-close" aria-label="Fermer le parcours">×</button></div><nav>${links}</nav>`;
    journeyDrawer.querySelector('.journey-close').addEventListener('click',closeJourneyDrawer);
    journeyDrawer.querySelectorAll('.journey-item').forEach(link=>link.addEventListener('click',()=>closeJourneyDrawer()));
    document.body.append(journeyBackdrop,journeyDrawer);
    installJourneyGestures();
  }

  function openJourneyDrawer(side='left'){
    if(!journeyDrawer||!journeyBackdrop)return;
    journeyDrawerSide=side==='right'?'right':'left';
    const build=document.getElementById('recit-field-build');
    document.documentElement.style.setProperty('--recit-field-top',`${build?.offsetHeight||0}px`);
    journeyDrawer.classList.toggle('from-right',journeyDrawerSide==='right');
    journeyDrawer.classList.add('open');
    journeyBackdrop.hidden=false;
    journeyBackdrop.classList.add('open');
    journeyDrawer.setAttribute('aria-hidden','false');
    document.body.classList.add('journey-drawer-open');
    root.querySelector('[data-journey-open]')?.setAttribute('aria-expanded','true');
    refreshJourneyUi();
  }

  function closeJourneyDrawer(){
    if(!journeyDrawer||!journeyBackdrop)return;
    journeyDrawer.classList.remove('open');
    journeyBackdrop.classList.remove('open');
    journeyDrawer.setAttribute('aria-hidden','true');
    document.body.classList.remove('journey-drawer-open');
    root.querySelector('[data-journey-open]')?.setAttribute('aria-expanded','false');
    setTimeout(()=>{if(!journeyBackdrop.classList.contains('open'))journeyBackdrop.hidden=true;},180);
  }

  function refreshJourneyUi(){
    if(!series)return;
    for(const e of series.episodes){
      const state=episodeJourneyState(e);
      const card=root.querySelector(`[data-episode="${cssEscape(e.id)}"]`);
      if(card){card.classList.toggle('is-current',state.kind==='current');card.classList.toggle('is-done',state.kind==='done');}
      const cardStatus=root.querySelector(`[data-journey-card-status="${cssEscape(e.id)}"]`);
      if(cardStatus){cardStatus.textContent=state.kind==='todo'?'':state.label;cardStatus.dataset.state=state.kind;}
      const drawerStatus=journeyDrawer?.querySelector(`[data-journey-status="${cssEscape(e.id)}"]`);
      if(drawerStatus){drawerStatus.textContent=state.label;drawerStatus.dataset.state=state.kind;}
      const drawerItem=journeyDrawer?.querySelector(`[data-journey-episode="${cssEscape(e.id)}"]`);
      if(drawerItem){drawerItem.classList.toggle('is-current',state.kind==='current');drawerItem.classList.toggle('is-done',state.kind==='done');}
    }
  }

  function installJourneyGestures(){
    let start=null;
    const edge=28;
    document.addEventListener('touchstart',ev=>{
      if(ev.touches.length!==1)return;
      const t=ev.touches[0];
      if(journeyDrawer?.classList.contains('open'))return;
      if(t.clientX<=edge)start={x:t.clientX,y:t.clientY,side:'left'};
      else if(t.clientX>=window.innerWidth-edge)start={x:t.clientX,y:t.clientY,side:'right'};
      else start=null;
    },{passive:true});
    document.addEventListener('touchmove',ev=>{
      if(!start||ev.touches.length!==1)return;
      const t=ev.touches[0],dx=t.clientX-start.x,dy=t.clientY-start.y;
      const outward=start.side==='left'?dx:-dx;
      if(outward>58&&Math.abs(dx)>Math.abs(dy)*1.25){openJourneyDrawer(start.side);start=null;}
      else if(Math.abs(dy)>48)start=null;
    },{passive:true});
    document.addEventListener('touchend',()=>{start=null;},{passive:true});
    let drawerStart=null;
    journeyDrawer?.addEventListener('touchstart',ev=>{if(ev.touches.length===1){const t=ev.touches[0];drawerStart={x:t.clientX,y:t.clientY};}},{passive:true});
    journeyDrawer?.addEventListener('touchmove',ev=>{
      if(!drawerStart||ev.touches.length!==1)return;
      const t=ev.touches[0],dx=t.clientX-drawerStart.x,dy=t.clientY-drawerStart.y;
      const closing=journeyDrawerSide==='right'?dx>58:dx<-58;
      if(closing&&Math.abs(dx)>Math.abs(dy)*1.25){closeJourneyDrawer();drawerStart=null;}
    },{passive:true});
    journeyDrawer?.addEventListener('touchend',()=>{drawerStart=null;},{passive:true});
    document.addEventListener('keydown',ev=>{if(ev.key==='Escape')closeJourneyDrawer();});
  }

  function modeLabel(t){return ({story:'Histoire',visit:'Visite',route:'Route'})[t]||'Récit';}
  function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[c]));}
  function escAttr(s){return esc(s);}
  function cssEscape(s){return (window.CSS&&CSS.escape)?CSS.escape(s):String(s).replace(/"/g,'\\"');}
})();
