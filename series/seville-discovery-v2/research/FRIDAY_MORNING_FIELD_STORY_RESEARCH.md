# J1 — Friday morning field-story research

Status: `BOUNDED_BATCH_COMPLETE`
Research date: 2026-09-17
Worker branch baseline: `seville-v2-j1-field-research @ 67da444c7828dca7e9d8bf41b4f7dd8a23be7f94`
Route authority: V1 `seville-discovery-ep06` + `seville-discovery-ep07` (read-only)
V2 authority: `FIELD_GUIDE_V2_CONTRACT.md`

## Scope and method

Bounded batch: **NH Sevilla Plaza de Armas → Reyes Católicos → Puente de Isabel II → Altozano / Mercado de Triana → San Jorge / Castilla → Puente de Isabel II → Paseo de Cristóbal Colón / exterior Maestranza → NH Plaza de Armas**.

The research target is field material, not final narration. Candidates are selected for what a visitor can notice while already walking this route. No route, booking, timing, UX, V1 or audio-production change is proposed here.

Selection criteria used by `/solve`:

1. specific and memorable rather than encyclopedic;
2. observable on the actual route, or usable as a walking-time story without forcing a search;
3. supported by strong sources;
4. robust against ordinary closure, scaffolding, vendor and visibility variation;
5. additive to the V1 idea rather than a paraphrase of it;
6. compatible with `LOOK_BEFORE_EXPLAIN`, short field scenes, optional depth and deliberate silence.

## Current field constraints discovered by `/research`

- The Mercado de Triana association currently lists commercial stalls from **09:00 to 14:30, Monday–Saturday**. The V1 timing reaches the Triana market area around 08:50, so the first Triana cue must work from Altozano / the market exterior and must not assume every stall is already active. This is a robustness constraint, not a route or schedule change. Sources: `S03`, `S04`.
- The dedicated current tourism page for **Castillo de San Jorge** states `Sitio arqueológico cerrado`; its hall is used as a tourist-information point with separate hours. Therefore no candidate may require descending into or visiting the archaeological site. The factual layer beneath the market remains usable from ground level. Sources: `S04`, `S05`, `S06`.
- The municipal government announced on **2026-09-17** that the Rodrigo de Triana statue in Pagés del Corro was removed temporarily for bronze reproduction. It is also outside the exact assigned walking line. It is explicitly rejected as a field landmark. Source: `S18`.

## Candidate records

### J1-FRI-001 — Plaza de Armas: a city edge rewritten

- **Route section / location:** start at NH Plaza de Armas; old Córdoba / Plaza de Armas station context.
- **What the visitor can observe:** if the former station building is naturally in sight, compare its large neo-Mudéjar brick mass with the open approach toward the river; otherwise use the story while moving without asking the visitor to hunt for the façade.
- **Narrative hook:** this western edge has successively been defined by barriers and mobility infrastructure; the railway terminal later disappeared as an active rail barrier and the riverfront was reopened in the Expo 92 transformation.
- **Concise factual basis:** the Plaza de Armas station was built in 1899–1901 in a neo-Mudéjar language; the station closed before Expo 92 and the tracks along Torneo were removed as the riverfront was reorganised.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S14`, `S15`.
- **Robustness:** `MEDIUM_HIGH`. Building/history are stable; exact line of sight from the hotel-to-river path is not guaranteed. Cue must remain conditional.
- **Suggested duration:** `45-90s`.
- **/solve disposition:** `PRIMARY_CONDITIONAL`.

### J1-FRI-002 — The Generation of ’27 arrives here, then risks the river

- **Route section / location:** Plaza de Armas → river approach; works best as walking-time material.
- **What the visitor can observe:** the old station / departure zone behind them and the river ahead; no small object is required.
- **Narrative hook:** in December 1927, several of the young poets later grouped as the Generation of ’27 arrived at this station; during the Seville gathering, a later Triana night ended with some of them crossing the flooded Guadalquivir in an improvised boat, a crossing remembered by Dámaso Alonso.
- **Concise factual basis:** Seville’s official Generation of ’27 itinerary places the poets’ arrival on 15 December 1927 at the Córdoba station, now Plaza de Armas, and recounts the subsequent river episode from contemporary recollection.
- **Legend / tradition status:** `NONE — DOCUMENTED_RECOLLECTION`.
- **Sources:** `S16`.
- **Robustness:** `HIGH` as transfer story; no fragile object dependency.
- **Suggested duration:** `90-180s`.
- **/solve disposition:** `WALKING_RESERVE / DEPTH_ONLY`. Strong story, but too dense to stack with the station + engineered-river + bridge primary sequence.

### J1-FRI-003 — The water in front of you is also an engineered port dársena

- **Route section / location:** Reyes Católicos → Puente de Isabel II, preferably before or early in the crossing.
- **What the visitor can observe:** the contained urban waterway, fixed banks, bridges and urban frontage; boats are optional, not required.
- **Narrative hook:** the visitor thinks “river”; the modern city centre is also looking at an engineered **dársena** shaped by twentieth-century port and flood-control works.
- **Concise factual basis:** Port of Seville history describes the Brackenbury works and later transformations that reorganised the old river course and port; current port regulation defines the urban waterway as part of the `Dársena del Puerto de Sevilla`.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S09`, `S10`.
- **Robustness:** `HIGH`. Do not claim a particular water level, calmness or boat activity on the day.
- **Suggested duration:** `45-90s`.
- **/solve disposition:** `PRIMARY`.

### J1-FRI-004 — Triana bridge: the iron you notice is no longer doing the job you assume

- **Route section / location:** Puente de Isabel II.
- **What the visitor can observe:** the characteristic iron arches / circular forms, stone supports and current deck.
- **Narrative hook:** the strongest-looking part of the bridge is a historical memory: after the 1970s restoration, the old iron arches ceased to carry the deck and remained as heritage form.
- **Concise factual basis:** the permanent Isabel II bridge opened in 1852 on the line of the earlier bridge of boats; during the 1976–77 restoration its deck was replaced and the original iron arches stopped performing their former structural function.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S01`.
- **Robustness:** `HIGH`; large permanent elements, no access dependency.
- **Suggested duration:** `45-90s`.
- **/solve disposition:** `PRIMARY`.

### J1-FRI-005 — La cucaña: a bridge tradition that belongs to the water even when it is absent

- **Route section / location:** Puente de Isabel II / Guadalquivir view.
- **What the visitor can observe:** the water and bridge; the event itself is not expected to be present.
- **Narrative hook:** the 1852 opening of the bridge is tied in local memory to the first `cucaña` of the Velá de Santa Ana — a slippery-pole contest over the water that remains a Triana tradition.
- **Concise factual basis:** Seville tourism’s bridge history links the first cucaña to the bridge inauguration festivities and notes its survival in the Velá.
- **Legend / tradition status:** `LOCAL_TRADITION — NOT_A_LIVE_VISUAL_CUE`.
- **Sources:** `S01`.
- **Robustness:** `HIGH` factually, `LOW` for direct visibility; never tell the visitor to look for the installation outside the festival.
- **Suggested duration:** `20-45s`.
- **/solve disposition:** `DEPTH_ONLY`.

### J1-FRI-006 — Capillita del Carmen: tiny landmark, concentrated Triana material

- **Route section / location:** Triana end of the bridge / Altozano.
- **What the visitor can observe:** small brick chapel, ceramic decoration and octagonal bell-tower form at the bridgehead.
- **Narrative hook:** after the large nineteenth-century metal bridge, the eye can land on a tiny 1928 building whose brick and ceramic surface compresses a very different Triana material identity.
- **Concise factual basis:** Aníbal González designed the Capilla del Carmen in 1928; it uses exposed brick and Triana ceramics, with work associated with ceramist Emilio García García. The popular nickname `el Mechero` refers to its form.
- **Legend / tradition status:** `POPULAR_NICKNAME`, not legend.
- **Sources:** `S02`.
- **Robustness:** `HIGH`; exterior-only cue.
- **Suggested duration:** `20-45s`.
- **/solve disposition:** `PRIMARY`.
- **Excluded embellishment:** do not make the promotional “ceramic lighthouse for boats” comparison a core factual claim; it is unnecessary to the stronger architectural hook.

### J1-FRI-007 — Mercado de Triana: everyday market over a coercive layer

- **Route section / location:** Altozano / Mercado de Triana.
- **What the visitor can observe:** market exterior, entrances and — once active — food stalls / aisles; no underground access is required.
- **Narrative hook:** a living food market occupies the site of the Castillo de San Jorge, long associated with the Tribunal of the Inquisition. The field contrast is ordinary daily commerce above an uncomfortable institutional layer.
- **Concise factual basis:** the market dates from the early nineteenth century and stands over remains of the Castillo de San Jorge; archaeological remains were documented during redevelopment. The dedicated current site page states that the archaeological site is closed.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S03`, `S04`, `S05`, `S06`.
- **Robustness:** `HIGH` if written as a ground-level scene. Commercial stalls officially start at 09:00, so the candidate must work outside first and treat interior sensory detail as opportunistic rather than guaranteed.
- **Suggested duration:** `90-180s`.
- **/solve disposition:** `PRIMARY`.

### J1-FRI-008 — Ceramics without turning the walk into a museum hunt

- **Route section / location:** San Jorge / Castilla walking return through Triana.
- **What the visitor can observe:** tiles, ceramic surfaces, signs or façade details encountered naturally; no single shopfront is mandatory.
- **Narrative hook:** instead of merely saying “Triana = ceramics,” use material encountered in the street to connect the neighbourhood to a production history with medieval / Islamic roots and later Mudéjar continuities.
- **Concise factual basis:** Seville’s ceramic institutions document long ceramic production in Triana and the preserved industrial context of the former Santa Ana ceramic factory / kilns nearby.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S07`, `S08`.
- **Robustness:** `MEDIUM`. Individual storefronts, signs and displays can change. The scene must accept any clearly visible ceramic surface and must not detour to the Centro Cerámica.
- **Suggested duration:** `45-90s`.
- **/solve disposition:** `PRIMARY_WALKING_FLEXIBLE`; downgrade to depth if the showrunner cannot anchor a route-native visual cue without adding a detour.

### J1-FRI-009 — Magellan’s expedition also depended on an ordinary crossing

- **Route section / location:** return toward / across Puente de Isabel II; walking-time alternative.
- **What the visitor can observe:** the act of crossing between Triana and the city; no specific surviving object from 1519 is required.
- **Narrative hook:** the first circumnavigation story begins not only with ships but with supply logistics: Seville’s official Magellan itinerary notes goods, provisions and tools crossing the old bridge of boats toward the expedition’s ships.
- **Concise factual basis:** municipal V Centenario itinerary identifies the bridge-of-boats crossing at the site of today’s Triana bridge as part of expedition provisioning movements.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S17`.
- **Robustness:** `HIGH` as context, but visually indirect.
- **Suggested duration:** `45-90s`.
- **/solve disposition:** `DEPTH_ONLY / WALKING_RESERVE`. The bridge already has a stronger primary structural reveal.

### J1-FRI-010 — Arenal: the vanished working shore beneath the promenade

- **Route section / location:** Paseo de Cristóbal Colón / Arenal after returning to the east bank.
- **What the visitor can observe:** broad riverfront / promenade and relationship between city and water; the historic sandy working shore itself is gone.
- **Narrative hook:** `Arenal` is not an abstract district name: it recalls the sandy riverbank where maritime trades clustered. The modern promenade asks for a before/after mental reconstruction.
- **Concise factual basis:** official Seville tourism traces the district name and its maritime trades to the sandy Guadalquivir edge; twentieth-century port transformations progressively moved major port activity south and remade the central waterfront.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S09`, `S11`.
- **Robustness:** `HIGH`; relies on large-scale spatial contrast, not a fragile object.
- **Suggested duration:** `45-90s`.
- **/solve disposition:** `PRIMARY`.

### J1-FRI-011 — Maestranza exterior: the arena is less geometrically pure than memory suggests

- **Route section / location:** exterior Maestranza only, Friday morning.
- **What the visitor can observe:** the arena block at the Arenal and its irregular exterior / relationship to the river; do not ask the visitor to count sides.
- **Narrative hook:** the famous “round” arena accumulated over a very long construction history; the official Maestranza describes an irregular polygon of thirty unequal sides rather than a perfect circle.
- **Concise factual basis:** the present complex developed over roughly 120 years, from the eighteenth into the nineteenth century, constrained by its site and construction sequence; official history describes the irregular thirty-sided enclosure.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S12`, `S13`.
- **Robustness:** `MEDIUM_HIGH`. Exterior form is stable, but the best angle may vary. Do not duplicate interior material reserved for the booked Sunday visit.
- **Suggested duration:** `20-45s`.
- **/solve disposition:** `PRIMARY_BRIEF`.

### J1-FRI-012 — Rodrigo de Triana statue as field landmark

- **Route section / location:** Pagés del Corro, outside the exact assigned line.
- **What the visitor can observe:** currently nothing reliable; the statue was removed on 2026-09-17 for reproduction work.
- **Narrative hook:** potentially a named-human-story cue, but it would require route drift and currently lacks the object.
- **Concise factual basis:** municipal announcement documents the temporary removal.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S18`.
- **Robustness:** `FAIL` for this batch.
- **Suggested duration:** `DEPTH_ONLY`.
- **/solve disposition:** `REJECTED — ROUTE_DRIFT + CURRENTLY_REMOVED`.

### J1-FRI-013 — Descend into Castillo de San Jorge archaeology

- **Route section / location:** Mercado de Triana.
- **What the visitor can observe:** access cannot currently be assumed.
- **Narrative hook:** strong in principle, but it fails current field access.
- **Concise factual basis:** dedicated current tourism page says the archaeological site is closed.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S05`.
- **Robustness:** `FAIL` as an action cue.
- **Suggested duration:** `DEPTH_ONLY`.
- **/solve disposition:** `REJECTED_AS_FIELD_ACTION`; retain only the underfoot historical layer in `J1-FRI-007`.

### J1-FRI-014 — “Ceramic lighthouse” story for Capillita del Carmen

- **Route section / location:** Altozano.
- **What the visitor can observe:** the chapel is visible, but the lighthouse metaphor is interpretive / promotional.
- **Narrative hook:** vivid but weaker than the directly sourced architecture + material story.
- **Concise factual basis:** not needed for the selected candidate.
- **Legend / tradition status:** `PROMOTIONAL_ANECDOTE`.
- **Sources:** `S02` for the architectural facts; anecdotal comparison intentionally excluded.
- **Robustness:** `MEDIUM` semantically.
- **Suggested duration:** `DEPTH_ONLY`.
- **/solve disposition:** `REJECTED_AS_CORE_FACT`.

### J1-FRI-015 — Centro Cerámica as a physical stop

- **Route section / location:** nearby Triana, but would require treating the centre as a destination rather than incidental route material.
- **What the visitor can observe:** not guaranteed on the exact route without detour.
- **Narrative hook:** excellent evidence source for the craft history, unnecessary as a Friday stop.
- **Concise factual basis:** the centre preserves former ceramic-production context and kilns.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S07`, `S08`.
- **Robustness:** `LOW` as route-native stop; `HIGH` as background evidence.
- **Suggested duration:** `DEPTH_ONLY`.
- **/solve disposition:** `REJECTED_AS_STOP — KEEP_AS_CONTEXT`.

### J1-FRI-016 — Detailed Maestranza interior story

- **Route section / location:** Maestranza.
- **What the visitor can observe:** Friday route sees exterior only; Sunday has the booked interior visit.
- **Narrative hook:** could explain ring, barriers and viewing hierarchy, but doing so Friday would cannibalise Sunday.
- **Concise factual basis:** official Maestranza sources are strong, but timing/sequence makes this the wrong batch.
- **Legend / tradition status:** `NONE`.
- **Sources:** `S12`, `S13`.
- **Robustness:** `HIGH` evidence, `LOW` sequencing value Friday.
- **Suggested duration:** `DEPTH_ONLY`.
- **/solve disposition:** `REJECTED_FOR_FRIDAY — RESERVE_FOR_SUNDAY`.

### J1-FRI-017 — Add Torre del Oro / Atarazanas as another Arenal stop

- **Route section / location:** beyond what is needed for the exact morning loop.
- **What the visitor can observe:** potentially visible depending on position, but making either a stop would expand the assigned route logic.
- **Narrative hook:** strong port-history material, but `J1-FRI-010` already makes the Arenal leg intelligible without adding another destination.
- **Concise factual basis:** not needed to decide the Friday batch.
- **Legend / tradition status:** `NONE`.
- **Sources:** not promoted into the manifest because the candidate loses on route fit before factual discrimination is needed.
- **Robustness:** `LOW` for scope discipline.
- **Suggested duration:** `DEPTH_ONLY`.
- **/solve disposition:** `REJECTED — ROUTE_EXPANSION_WITHOUT_INCREMENTAL_VALUE`.

## /solve — selected field flow

### BEST_SOLUTION

Use a deliberately sparse **eight-hook primary palette**, with three optional walking/depth reserves:

**Primary / route-native**

1. `J1-FRI-001` — Plaza de Armas rewritten edge (`PRIMARY_CONDITIONAL`).
2. `J1-FRI-003` — engineered urban dársena.
3. `J1-FRI-004` — bridge structure / non-structural historic iron reveal.
4. `J1-FRI-006` — Capillita del Carmen as concentrated brick-and-ceramic landmark.
5. `J1-FRI-007` — living market over Castillo / Inquisition layer, ground-level only.
6. `J1-FRI-008` — flexible ceramic-material reading while walking, no detour.
7. `J1-FRI-010` — Arenal before/after working shore.
8. `J1-FRI-011` — brief exterior Maestranza irregularity; reserve interior for Sunday.

**Optional walking/depth reserves**

- `J1-FRI-002` — Generation of ’27 arrival + flooded-river anecdote.
- `J1-FRI-005` — cucaña / Velá tradition.
- `J1-FRI-009` — Magellan provisioning over the old bridge of boats.

### Challenge of the leading solution

- **Bridge overload risk:** the bridge alone supports engineering, boat-bridge history, cucaña and Magellan. Putting all four in primary flow would turn the strongest observation point into a lecture. Keep the engineered-dársena setup + structural bridge reveal; move cucaña and Magellan to optional depth.
- **Market access contradiction:** generic visitor material can make the archaeological interpretation centre sound visitable, while the dedicated current page says the archaeological site is closed. The stronger field design is a surface scene that does not need access at all.
- **Ceramic fragility:** a named shopfront or display may disappear, close or be scaffolded. The selected candidate observes ceramic material opportunistically and survives if no particular façade is available.
- **Maestranza duplication:** Friday should create anticipation, not pre-consume Sunday’s booked interior visit. Keep only the exterior irregularity / long-building-history reveal.
- **Station sightline:** if the old station is not naturally visible from the start path, do not create a search task. Convert `J1-FRI-001` to short walking context or silence.

### Density and silence notes for J2

- Let the river appear before explaining `J1-FRI-003`.
- After `J1-FRI-004`, the bridge should get a real observation / silence window; optional depth can fill walking time only if useful.
- In the market, sensory attention outranks a fact pile. `J1-FRI-007` can be shorter if stalls are active; the visitor should look before hearing the institutional layer.
- The return bridge is a good candidate for silence rather than a second mandatory bridge lecture.
- `J1-FRI-010` should begin only when the broad Arenal riverfront is perceptible.
- `J1-FRI-011` is an anticipation tag, not a Sunday-preview lecture.

## RESEARCH_HANDOFF

- **To J2:** the strongest Friday morning material is now route-native, sourced and field-robust. J2 should treat the candidate IDs and dispositions as research input, not final prose.
- **Do not reopen without new evidence:** underground Castillo access, Rodrigo de Triana statue, physical Centro Cerámica detour, detailed Friday Maestranza interior.
- **Revalidate if production is materially later:** market hours, Castillo access status and any scaffolding / works affecting a specific visual cue.
- **Unresolved but bounded:** exact sightline to the old Plaza de Armas station from the hotel departure; exact ceramic surfaces encountered on San Jorge / Castilla; individual vendor opening state around 09:00.

## Stop condition

`STOP_CONDITION = MET_FOR_FRIDAY_MORNING_BATCH`.

After freshness, closure and route-fit checks, additional research no longer changed the best primary field-story set. New searches mainly produced weaker duplicates, route-expanding attractions or optional-depth material. The batch therefore stops here instead of attempting to exhaust Seville.
