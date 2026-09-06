(() => {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get('slug');
  const title = document.getElementById('title');
  const requestEl = document.getElementById('request');
  const summaryEl = document.getElementById('summary');
  const stopsEl = document.getElementById('stops');
  const questionEl = document.getElementById('question');

  function metric(value, label, warning=false) {
    const box = document.createElement('div');
    box.className = 'metric' + (warning ? ' warning' : '');
    const strong = document.createElement('strong');
    strong.textContent = value;
    const span = document.createElement('span');
    span.textContent = label;
    box.append(strong, span);
    return box;
  }

  function render(data) {
    title.textContent = data.title || data.slug || 'Proposition de visite';
    const req = data.request || {};
    requestEl.textContent = [req.city, req.duration_budget, req.mobility, req.audience].filter(Boolean).join(' · ');

    const s = data.review_summary || {};
    summaryEl.append(
      metric(`${s.visit_budget_minutes ?? '?'} min`, 'budget total'),
      metric(`${s.stop_count ?? (data.route || []).length}`, 'étapes'),
      metric(`${s.walking_distance_km ?? '?'} km`, 'marche indicative', s.walking_metrics_status !== 'ROUTED_FROZEN'),
      metric(`${s.walking_time_minutes ?? '?'} min`, 'temps de marche indicatif', s.walking_metrics_status !== 'ROUTED_FROZEN'),
      metric(`${s.buffer_minutes ?? '?'} min`, 'marge / respiration'),
      metric(s.effort || 'non évalué', 'effort')
    );

    const points = [];
    (data.route || []).forEach((stop, index) => {
      const li = document.createElement('li');
      li.className = 'stop';
      const h = document.createElement('h3');
      h.textContent = stop.name;
      const address = document.createElement('p');
      address.className = 'address';
      address.textContent = stop.address || '';
      li.append(h, address);

      if (stop.incoming_leg) {
        const leg = document.createElement('p');
        leg.className = 'leg';
        leg.textContent = `Depuis l’étape précédente : ~${stop.incoming_leg.distance_km} km · ~${stop.incoming_leg.walk_minutes} min`;
        const status = document.createElement('span');
        status.className = 'status';
        status.textContent = stop.incoming_leg.status === 'ROUTED_FROZEN' ? 'routé' : 'indicatif';
        leg.appendChild(status);
        li.appendChild(leg);
      }

      const reason = document.createElement('p');
      reason.className = 'reason';
      reason.textContent = stop.editorial_reason || '';
      const launch = document.createElement('p');
      launch.className = 'launch';
      launch.textContent = stop.launch ? `Déclenchement : ${stop.launch}` : '';
      li.append(reason, launch);
      stopsEl.appendChild(li);

      const c = stop.coordinates;
      if (c && Number.isFinite(Number(c.lat)) && Number.isFinite(Number(c.lon))) {
        points.push([Number(c.lat), Number(c.lon), index + 1, stop.name]);
      }
    });

    questionEl.textContent = (data.human_gate && data.human_gate.question) || 'Valider, ajuster ou rejeter cet itinéraire avant production.';

    if (window.L && points.length) {
      const map = L.map('map', {scrollWheelZoom: false});
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);
      const latLngs = points.map(p => [p[0], p[1]]);
      L.polyline(latLngs, {weight: 4, opacity: .75, dashArray: '7 7'}).addTo(map);
      points.forEach(p => L.marker([p[0], p[1]]).addTo(map).bindPopup(`<strong>${p[2]}. ${p[3]}</strong>`));
      map.fitBounds(latLngs, {padding: [30, 30]});
    }
  }

  if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
    title.textContent = 'Proposition invalide';
    requestEl.textContent = 'Ajoute ?slug=<identifiant> à l’URL.';
    return;
  }

  fetch(`data/${slug}.json`, {cache: 'no-store'})
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(render)
    .catch(err => {
      title.textContent = 'Proposition indisponible';
      requestEl.textContent = `Impossible de charger ${slug}: ${err.message}`;
    });
})();
