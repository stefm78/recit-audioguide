(() => {
  const slug = window.RECIT_SERIES_SLUG;
  if (!slug) return;
  load().catch(() => {});

  async function load(){
    const r = await fetch(`../../data/${encodeURIComponent(slug)}/series.json`, {cache:'no-store'});
    if(!r.ok) return;
    const series = await r.json();
    if(series.type !== 'visit' || !series.visit?.route_map_url) return;
    const mr = await fetch(series.visit.route_map_url, {cache:'no-store'});
    if(!mr.ok) return;
    const routeMap = await mr.json();
    decorateEpisodes(series);
    mount(series, routeMap);
  }

  function decorateEpisodes(series){
    (series.episodes || []).forEach(e => {
      const card = document.getElementById(e.id);
      if(!card) return;
      const head = card.querySelector('.episode-top > div');
      if(head && !head.querySelector('.visit-day-meta')){
        const meta = document.createElement('div');
        meta.className = 'visit-day-meta';
        meta.textContent = [e.day_label, e.time].filter(Boolean).join(' · ');
        head.prepend(meta);
      }
      if(e.next_step?.route_hint && !card.querySelector('.route-guidance')){
        const block = document.createElement('p');
        block.className = 'route-guidance';
        block.innerHTML = `<strong>Déambulation :</strong> ${esc(e.next_step.route_hint)}`;
        const actions = card.querySelector('.actions');
        (actions || card).before(block);
      }
    });
  }

  function mount(series, routeMap){
    const strip = document.querySelector('.visit-strip');
    if(!strip || document.querySelector('[data-visit-map]')) return;
    const section = document.createElement('section');
    section.dataset.visitMap = '1';
    section.className = 'visit-map-shell card';
    section.innerHTML = `
      <div class="visit-map-head"><div><p class="eyebrow">Carte de la visite</p><h2>Déambulations à pied</h2></div><div class="visit-map-tools"><p>Hébergement, zones et rues servent de repères. Google Maps reste l’autorité de navigation réelle.</p><button type="button" class="secondary visit-map-toggle" aria-expanded="true">Réduire la carte</button></div></div>
      <div class="visit-map-body">
        <div class="visit-day-tabs" role="tablist"></div>
        <div id="visit-map-canvas" class="visit-map-canvas" aria-label="Carte du parcours"></div>
        <div class="visit-map-fallback" hidden></div>
        <div class="visit-leg-list"></div>
      </div>`;
    strip.after(section);
    const tabs = section.querySelector('.visit-day-tabs');
    routeMap.days.forEach((d,i)=>{
      const b=document.createElement('button');
      b.type='button'; b.className=i===0?'active':''; b.textContent=d.label;
      b.addEventListener('click',()=>showDay(d,section,b)); tabs.appendChild(b);
    });
    const toggle=section.querySelector('.visit-map-toggle');
    const key=`recit:visit-map-collapsed:${slug}`;
    let saved=null; try{ saved=localStorage.getItem(key); }catch(_){ }
    const defaultCollapsed=saved===null ? window.matchMedia('(max-width: 719px)').matches : saved==='1';
    setCollapsed(section,toggle,defaultCollapsed,false,key);
    toggle.addEventListener('click',()=>setCollapsed(section,toggle,!section.classList.contains('collapsed'),true,key));
    showDay(routeMap.days[0],section,tabs.querySelector('button'));
  }

  function setCollapsed(section,toggle,collapsed,persist,key){
    section.classList.toggle('collapsed',collapsed);
    const body=section.querySelector('.visit-map-body');
    body.hidden=collapsed;
    toggle.textContent=collapsed?'Afficher la carte':'Réduire la carte';
    toggle.setAttribute('aria-expanded',String(!collapsed));
    if(persist){ try{localStorage.setItem(key,collapsed?'1':'0');}catch(_){ } }
    if(!collapsed && map) setTimeout(()=>map.invalidateSize(),0);
  }

  let map, layers=[];
  function showDay(day, section, activeButton){
    section.querySelectorAll('.visit-day-tabs button').forEach(b=>b.classList.toggle('active', b===activeButton));
    section.querySelector('.visit-leg-list').innerHTML = `<div class="visit-day-summary"><strong>${esc(day.theme||day.label)}</strong><span>${esc(day.summary||'')}</span></div>` +
      (day.legs||[]).map((leg,i)=>`<article class="visit-leg"><div class="visit-leg-number">${i+1}</div><div><strong>${esc(leg.label)}</strong><small>${esc(leg.time||'')}</small><p>${esc(leg.instructions||'')}</p>${leg.audio_episode_id?`<a class="secondary" href="#${esc(leg.audio_episode_id)}">Voir l’audio associé</a> `:''}<a class="secondary" target="_blank" rel="noopener" href="${esc(leg.maps_url||'#')}">Navigation piétonne</a></div></article>`).join('');

    const canvas=section.querySelector('#visit-map-canvas');
    const fallback=section.querySelector('.visit-map-fallback');
    if(!window.L){ canvas.hidden=true; fallback.hidden=false; fallback.innerHTML='<p>La carte interactive ne peut pas être chargée. Les itinéraires Google Maps et les rues détaillées restent disponibles ci-dessous.</p>'; return; }
    canvas.hidden=false; fallback.hidden=true;
    if(!map){ map=L.map(canvas,{scrollWheelZoom:false}); L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap'}).addTo(map); }
    layers.forEach(x=>map.removeLayer(x)); layers=[];
    const all=[];
    (day.legs||[]).forEach(leg=>{
      const pts=(leg.points||[]).map(p=>[p[0],p[1]]); if(pts.length>1){const line=L.polyline(pts,{weight:5,opacity:.76}).addTo(map);layers.push(line);all.push(...pts);}
      (leg.points||[]).forEach((p,i)=>{ if(i!==0 && i!==leg.points.length-1 && p[3]==='passage') return; const m=L.marker([p[0],p[1]]).addTo(map).bindPopup(`<strong>${esc(p[2])}</strong><br>${esc(leg.label)}`); layers.push(m); });
    });
    if(all.length) map.fitBounds(all,{padding:[24,24]}); setTimeout(()=>map.invalidateSize(),0);
  }
  function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
})();
