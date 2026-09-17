# J1 — Seville V2 field-story source manifest

Status: `ACTIVE_FOR_J1_RESEARCH`
Research date: 2026-09-17
Current bounded batch: Friday morning — NH Plaza de Armas → Guadalquivir → Triana → Arenal → NH

## Source policy

- Prefer institutional / municipal / operator-primary sources for historical facts and current access information.
- Separate historical evidence from freshness-sensitive operating facts.
- When two pages conflict about current access, prefer the more specific current page for the facility concerned and record the contradiction.
- A source may support research without implying that its venue should be added to the route.
- Revalidate dynamic hours, closures and field visibility before materially later production if a scene depends on them.

## Internal route and product sources

| ID | Source | Role |
|---|---|---|
| I01 | `series/seville-discovery/series.json` | Read-only authority for exact V1 Friday route, timings and sequence. |
| I02 | `series/seville-discovery/assets/visit-experience.json` | Read-only V1 field cues; used to avoid merely paraphrasing existing material. |
| I03 | `series/seville-discovery-v2/FIELD_GUIDE_V2_CONTRACT.md` | V2 research boundary and field-scene principles. |
| I04 | `series/seville-discovery-v2/BASELINE_V1_FALLBACK.md` | V1 immutability / fallback invariant. |

## External evidence sources

### S01 — Puente de Triana / Puente de Isabel II

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/puente-de-triana/
- **Evidence used:** former bridge of boats on the crossing; permanent Isabel II bridge opened in 1852; iron/stone construction history; 1976–77 restoration and changed structural role of the historic iron arches; cucaña tradition linked to the 1852 festivities / Velá.
- **Quality:** institutional tourism source; strong for concise local architectural/history facts.
- **Freshness sensitivity:** low for historical facts; festival scheduling itself is not used as a live cue.

### S02 — Capilla del Carmen / Capillita del Carmen

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/capilla-del-carmen/
- **Evidence used:** 1928 construction, Aníbal González, exposed brick and Triana ceramics, collaboration with ceramist Emilio García García, octagonal bell-tower form and popular `Mechero` nickname.
- **Quality:** institutional tourism source.
- **Freshness sensitivity:** low for architecture; ordinary exterior visibility should still be checked if works/scaffolding appear.

### S03 — Mercado de Triana opening hours

- **Publisher:** Asociación de Comerciantes del Mercado de Triana
- **URL:** https://mercadodetrianasevilla.com/horarios/
- **Evidence used:** current commercial-stall hours Monday–Saturday 09:00–14:30; hospitality has broader hours.
- **Quality:** primary market-operator source for current operating hours.
- **Freshness sensitivity:** high; revalidate if production/runtime is materially later.

### S04 — Mercado de Triana

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/mercado-de-triana/
- **Evidence used:** market origins in the nineteenth century; location over remains of Castillo de San Jorge; archaeology exposed during redevelopment; relationship between market and former fortress / Inquisition site.
- **Quality:** institutional tourism source.
- **Freshness sensitivity:** medium for access claims; see contradiction `C01`.

### S05 — Castillo de San Jorge

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/castillo-de-san-jorge/
- **Evidence used:** dedicated current page states `Sitio arqueológico cerrado`; tourist-information use / hours are separate from archaeological access.
- **Quality:** institutional, facility-specific current source; preferred over more generic market wording for current access status.
- **Freshness sensitivity:** high; revalidate before any future scene that would depend on access.

### S06 — Castillo de San Jorge — Patrimonium Hispalense

- **Publisher:** Ayuntamiento de Sevilla / Patrimonium Hispalense
- **URL:** https://www.sevilla.org/patrimonium-hispalense/patrimonium-hispalense/arquitectura/castillo-de-san-jorge
- **Evidence used:** historical and archaeological relationship between the castle remains and the later market; municipal heritage framing.
- **Quality:** municipal heritage source.
- **Freshness sensitivity:** low for historical / archaeological facts.

### S07 — Centro Cerámica Triana

- **Publisher:** ICAS — Instituto de la Cultura y las Artes de Sevilla
- **URL:** https://icas.sevilla.org/espacios/centro-ceramica
- **Evidence used:** former ceramic-factory context, kilns / production heritage and continuity of the Triana ceramics site.
- **Quality:** primary municipal cultural-institution source.
- **Freshness sensitivity:** low for historical evidence; the centre is used as evidence, not added as a Friday stop.

### S08 — Ceramics in Seville / Triana

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/en/ceramics/
- **Evidence used:** long ceramic-production tradition in Triana; Islamic / Mudéjar historical layers and tile-making context.
- **Quality:** institutional tourism synthesis.
- **Freshness sensitivity:** low for historical facts.

### S09 — Port of Seville history / Junta de Obras

- **Publisher:** Autoridad Portuaria de Sevilla
- **URL:** https://www.puertodesevilla.com/el-puerto/historia/junta-de-obras
- **Evidence used:** twentieth-century port works, including the Brackenbury transformation, reorganisation of river / port infrastructure and progressive movement of major port functions southward.
- **Quality:** primary port authority.
- **Freshness sensitivity:** low for historical transformation.

### S10 — Current Port of Seville maritime-traffic ordinance

- **Publisher:** Autoridad Portuaria de Sevilla
- **URL:** https://transparencia.puertodesevilla.com/images/1_Institucional/1_4_Relevancia%20Juridica/20260520_Ordenanza%20reguladora%20trafico%20maritimo_v1.pdf
- **Evidence used:** current formal use and extent of `Dársena del Puerto de Sevilla`; supports precise modern terminology for the engineered urban waterway.
- **Quality:** primary 2026 port-regulatory document.
- **Freshness sensitivity:** medium; terminology/current boundary is current as researched 2026-09-17.

### S11 — Barrio de El Arenal

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/barrio-de-el-arenal/
- **Evidence used:** `Arenal` as the sandy Guadalquivir-side area tied historically to port and maritime activity.
- **Quality:** institutional tourism source.
- **Freshness sensitivity:** low for historical explanation.

### S12 — Real Plaza de Toros de la Maestranza — La Plaza

- **Publisher:** Real Maestranza de Caballería de Sevilla
- **URL:** https://www.realmaestranza.com/real-plaza-de-toros/la-plaza/
- **Evidence used:** site by the Arenal / river, irregular enclosure, approximately thirty unequal sides and long construction history.
- **Quality:** primary institution / site operator for architectural description.
- **Freshness sensitivity:** low for architecture.

### S13 — Construction history of the Real Maestranza

- **Publisher:** Real Maestranza de Caballería de Sevilla
- **URL:** https://www.realmaestranza.com/real-plaza-de-toros/historia-de-la-construccion-de-la-real-maestranza-de-caballeria-de-sevilla/
- **Evidence used:** extended eighteenth–nineteenth-century construction sequence and reasons the arena evolved irregularly.
- **Quality:** primary institution / site operator.
- **Freshness sensitivity:** low.

### S14 — Plaza de Armas historical station documentation

- **Publisher:** Ayuntamiento de Sevilla — historical cartography / municipal archive publication
- **URL:** https://www.sevilla.org/no8do-digital/expo-no8do/cartografia-historica/sahp_07995.pdf
- **Evidence used:** construction of the Córdoba / Plaza de Armas station in 1899–1901, neo-Mudéjar architectural context and railway relationship to the western city edge.
- **Quality:** municipal historical documentation.
- **Freshness sensitivity:** low.

### S15 — Paseo del Rey Juan Carlos I / riverfront transformation

- **Publisher:** Ayuntamiento de Sevilla
- **URL:** https://www.sevilla.org/servicios/medio-ambiente-parques-jardines/parques/paseos-arbolados/paseo-del-rey-juan-carlos-i
- **Evidence used:** removal of rail tracks / reorganisation around the former Plaza de Armas railway corridor in the Expo 92-era riverfront transformation.
- **Quality:** municipal public-space history.
- **Freshness sensitivity:** low.

### S16 — Seville and the Generation of ’27

- **Publisher:** Visita Sevilla / Turismo de Sevilla
- **URL:** https://visitasevilla.es/fr/seville-generation-de-27/
- **Evidence used:** 15 December 1927 arrival at the Córdoba station / present Plaza de Armas and the later recollection of a makeshift boat crossing after a Triana gathering during high water / flood conditions.
- **Quality:** institutional cultural-tourism itinerary using documented literary recollection.
- **Freshness sensitivity:** low.

### S17 — Seville municipal V Centenario / first circumnavigation itinerary

- **Publisher:** Ayuntamiento de Sevilla
- **URL:** https://www.sevilla.org/actualidad/noticias/2019/nuevo-itinerario-turistico-y-cultural-con-15-espacios-vinculados-con-el-v-centenario-de-la-primera-vuelta-al-mundo
- **Evidence used:** logistical use of the old bridge-of-boats crossing for goods, provisions and tools associated with Magellan’s expedition; relation of Triana / Castillo site to the 1519 city.
- **Quality:** municipal historical-itinerary source.
- **Freshness sensitivity:** low.

### S18 — Rodrigo de Triana statue removed on 2026-09-17

- **Publisher:** Ayuntamiento de Sevilla
- **URL:** https://www.sevilla.org/actualidad/noticias/2026/el-ayuntamiento-retira-la-estatua-de-rodrigo-de-triana-de-la-calle-pages-del-corro-para-realizar-una-copia-en-bronce-de-la-misma
- **Evidence used:** current-day removal of the statue from Pagés del Corro for bronze-copy work.
- **Quality:** primary municipal current notice.
- **Freshness sensitivity:** very high; used principally to reject the statue as a current field landmark.

## Contradiction and uncertainty register

### C01 — Mercado page versus Castillo-specific current access

- `S04` presents the market / archaeological interpretation as part of the visitor context.
- `S05`, the dedicated current Castillo page, states that the archaeological site is closed.
- **Resolution:** for current field access, `S05` governs. `J1-FRI-007` remains entirely ground-level; `J1-FRI-013` is rejected as an action cue.

### C02 — “Market open” does not mean all commercial stalls are active before 09:00

- The market area / hospitality can have broader availability.
- `S03` specifically lists commercial stalls from 09:00 Monday–Saturday.
- **Resolution:** scenes around the V1 ~08:50 arrival must work from Altozano / exterior first and cannot require a fully active market interior.

### C03 — Capillita del Carmen promotional metaphor

- A vivid “ceramic lighthouse” comparison appears in tourism-style promotional material, but the selected field hook is fully supported without relying on that metaphor.
- **Resolution:** retain the directly sourced 1928 / Aníbal González / brick / Triana-ceramic / `Mechero` facts; exclude the metaphor from the core factual basis.

## Freshness recheck list for downstream workers

Before final showrunner/runtime material if materially later than 2026-09-17, recheck only facts that can actually change the field action:

1. `S03` — commercial-stall hours at Mercado de Triana;
2. `S05` — Castillo de San Jorge archaeological access status;
3. any current works / scaffolding that materially blocks a specifically named observation target;
4. whether a selected cue has accidentally become dependent on a temporary storefront, sign or display.

Historical bridge, Arenal, station, Maestranza and port-transformation facts do not require routine freshness refresh unless new contradictory evidence appears.
