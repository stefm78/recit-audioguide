# P7 — Ulysse performance continuity / Henri Edge

Authority: #164  
Parent artistic authority: #110  
Downstream production: #112

Status: **P7_READY_FOR_STREAM3_RENDER**

## Finding

Production human finding:

- Ulysse / Henri identity: **PASS**
- narrative performance: **FAIL**
- observation: **too mechanical and cold**

This is a performance-continuity defect, not a casting defect.

## Frozen constraints

- keep `fr-FR-HenriNeural`;
- no recasting;
- no frozen-text change;
- no Production Program mutation for P7;
- no provider/model research in Round 1;
- no decorative sound;
- dry performance comparison;
- all non-Ulysse material stays on current Production identities/settings.

## Four representative states

### 1. S05 132–143 — storyteller / pride → regret

Real dramatic question:

Can Ulysse tell his own failure to people in the room rather than recite it?

B direction:
- slightly more forward than baseline;
- pride perceptible early;
- real address to the Phéaciens;
- temperature falls after the interruption;
- final recognition of consequence is simple, not solemn.

Avoid:
- uniform recitation;
- permanent gravity;
- smiling bravado;
- theatrical regret.

### 2. S06 90–99 — shock / loss

Real dramatic question:

Does “Ithaque s’éloignait” land as a lived loss rather than narrated information?

B direction:
- body before commentary;
- short, concrete phrases;
- true temperature drop;
- no complaint and no melodrama.

Avoid:
- neutral logbook;
- lament;
- slow-motion tragedy;
- shouting.

### 3. S12 136–154 — father / recognition under disbelief

Real dramatic question:

Can Ulysse want recognition without demanding it?

B direction:
- warmth held back;
- listen to Télémaque;
- fragility without a broken voice;
- “Je comprends / Tu as raison” must feel responsive, not pre-recorded.

Avoid:
- triumphant father;
- heroic declaration;
- teacher tone;
- pathos.

### 4. S14 79–89 — controlled authority

Real dramatic question:

Can Ulysse be dangerous without becoming louder or colder?

B direction:
- moral precision;
- questions bite because they are exact;
- anger without shouting;
- no revenge pleasure.

Avoid:
- trailer voice;
- slogans;
- icy monotony;
- jubilant vengeance.

## Round 1 A/B

A = exact current Ulysse baseline:
- Henri;
- rate -4%;
- pitch -10 Hz;
- volume +2%.

B = state-shaped Henri/Edge profile defined in:
`series/odyssee/review/P7_ULYSSE_PERFORMANCE_CONTINUITY_V1.json`.

Only Ulysse gets temporary P7 prosody/pause overrides.

No P7 override is automatically a Production decision.

## Human decision

For each state, separate:

### Observation

What is actually heard.

### Artistic verdict

PASS / FAIL for:
- Henri identity preserved;
- natural French;
- B materially less mechanical/cold than A;
- dramatic temperature appropriate;
- rhythm/phrasing alive;
- restraint/no caricature.

Global:
- one recognisable Ulysse across all four states;
- states distinct without sounding like four different characters.

## PASS

Exact verdict:

`P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS`

All four B states must pass and global identity continuity must pass.

## Bounded Edge retry

If only one or two states fail while identity stays PASS:

- exactly one additional Edge round;
- failed states only;
- same Henri voice;
- same frozen text;
- no new provider.

No repeated tuning loop.

## Escalation

Only after the bounded Edge retry remains materially mechanical/cold:

`P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER`

Even then:
- identity target remains Henri/Ulysse;
- this is not recasting;
- Stream 2 may solve performance, not identity.

## H2

H2 is suspended until:

- `P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS`;
- and `A+B+C+D MACHINE_QUALIFIED`.

No other H2 scope is reopened.
