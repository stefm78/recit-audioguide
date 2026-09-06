(() => {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get('slug');
  const title = document.getElementById('title');
  const requestEl = document.getElementById('request');
  const summaryEl = document.getElementById('summary');
  const stopsEl = document.getElementById('stops');
  const questionEl = document.getElementById('question');
  const mapEl = document.getElementById('map');
  const mapFallbackEl = document.getElementById('map-fallback');
  const mapStatusEl = document.getElementById('map-status');

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

  function showMapFallback(message) {
    mapEl.hidden = true;
    mapFallbackEl.hidden = false;
    mapStatusEl.textContent = message;
  }

  function render(data) {
    title.textContent = data.title || data.slug || 'Proposition de visite';
    const req = data.request || {};
    requestEl.textContent = [req.city, req.duration_budget, req.mobility, req.audience].filter(Boolean).join(' · ');

    const s = data.review_summary || {};
    const routed = s.walking_metrics_status === 'ROUTED_FROZEN';
    summaryEl.append(
      metric(`${s.visit_budget_minutes ?? '?'} min`, 'budget total'),
      metric(`${s.stop_count ?? (data.route || []).length}`, 'étapes'),
      metric(`${s.walking_distance_km ?? '?'} km`, routed ? 'marche routée' : 'marche indicative', !routed),
      metric(`${s.walking_time_minutes ?? '?'} min`, routed ? 'temps de marche routé' : 'temps de marche indicatif', !routed),
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

      const c = stop.coordinates;
      if (c && Number.isFinite(Number(c.lat)) && Number.isFinite(Number(c.lon))) {
        const coordinates = document.createElement('p');
        coordinates.className = 'coordinates';
        coordinates.textContent = `Coordonnées : ${Number(c.lat).toFixed(5)}, ${Number(c.lon).toFixed(5)}`;
        li.appendChild(coordinates);
        points.push([Number(c.lat), Number(c.lon), index + 1, stop.name]);
      }
      stopsEl.appendChild(li);
    });

    questionEl.textContent = (data.human_gate && data.human_gate.question) || 'Valider, ajuster ou rejeter cet itinéraire avant production.';

    if (!points.length) {
      showMapFallback('Aucune coordonnée cartographiable dans cette proposition.');
      return;
    }
    if (!window.L) {
      showMapFallback('Bibliothèque cartographique indisponible ; la liste ordonnée reste utilisable pour la décision.');
      return;
    }

    try {
      const map = L.map('map', {scrollWheelZoom: false});
      const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      });
      tiles.on('tileerror', () => {
        mapStatusEl.textContent = 'Fond de carte partiellement indisponible ; les marqueurs et la liste restent la référence.';
      });
      tiles.addTo(map);
      const latLngs = points.map(p => [p[0], p[1]]);
      L.polyline(latLngs, {weight: 4, opacity: .75, dashArray: '7 7'}).addTo(map);
      points.forEach(p => {
        const marker = L.marker([p[0], p[1]]).addTo(map);
        const popup = document.createElement('strong');
        popup.textContent = `${p[2]}. ${p[3]}`;
        marker.bindPopup(popup);
      });
      map.fitBounds(latLngs, {padding: [30, 30]});
      mapStatusEl.textContent = 'Carte interactive chargée. Les métriques restent celles indiquées dans la proposition.';
    } catch (err) {
      showMapFallback(`Carte interactive indisponible (${err.message}). La décision reste possible depuis la liste.`);
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
      showMapFallback('Les données de proposition ne sont pas disponibles : validation impossible.');
    });
})();
