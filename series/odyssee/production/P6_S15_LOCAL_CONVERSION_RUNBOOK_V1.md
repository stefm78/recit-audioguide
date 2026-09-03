# P6 S15 — Local Windows conversion runbook

Authority: #163  
Raw human voice policy: **never upload or commit raw human captures to the public repository**.

This runbook is executed only after the browser capture surface has exported the exact frozen 12-take ZIP.

## Qualified machine inputs

### Windows BeltOut runtime

- repository: `stefm78/audio-engine`
- run: `33670957570`
- artifact: `beltout-portable-runtime-windows-x86_64`
- artifact digest: `sha256:ea9f387016a4452b9918a980214e26a2bcb513a31ad561cc91d0f8dc9072bcc1`
- Audio Engine: `f14a941d9218c2e9e632d7198557e7a3e48ff894`
- machine result: Windows CPU model load PASS

### Henri/Ulysse target anchor

- repository: `stefm78/audio-engine`
- run: `33603995656`
- artifact: `local-tts-p6-beltout-r0`
- required anchor SHA-256:
  `dc6266a224a3de4236c0eca8cbfb2364e97b16f558f514da48616451a3acad45`

The post-capture tool searches the downloaded anchor artifact recursively and accepts exactly one WAV with that SHA-256.

## Suggested private workspace

Use a directory outside the public repository checkout, for example:

`C:\voice-lab\p6-s15-production`

Nothing under `raw-selected`, `conversion-reports`, or `conversion-logs` is publishable.

## 1. Download the qualified runtime and anchor artifacts

From Git Bash or PowerShell with GitHub CLI authenticated:

```powershell
mkdir C:\voice-lab\p6-s15-production\runtime
mkdir C:\voice-lab\p6-s15-production\anchor

gh run download 33670957570 -R stefm78/audio-engine -n beltout-portable-runtime-windows-x86_64 -D C:\voice-lab\p6-s15-production\runtime
gh run download 33603995656 -R stefm78/audio-engine -n local-tts-p6-beltout-r0 -D C:\voice-lab\p6-s15-production\anchor
```

Do not substitute another runtime, checkpoint set, BeltOut revision, or anchor.

## 2. Freeze the selected 12-take capture ZIP

From the `recit-audioguide` checkout:

```powershell
python tools/p6_s15_pipeline.py intake C:\path\odyssee-p6-s15-production-selected-takes.zip --private-out C:\voice-lab\p6-s15-production\private
```

Expected status:

`FROZEN_12_OF_12_READY_FOR_SINGLE_BELTOUT_CONVERSION`

At this point the chosen take for every segment is immutable for this production round.

## 3. Run the exact one-shot conversions

```powershell
python tools/p6_s15_post_capture.py convert ^
  --frozen C:\voice-lab\p6-s15-production\private\frozen-intake.json ^
  --runtime-root C:\voice-lab\p6-s15-production\runtime ^
  --anchor-root C:\voice-lab\p6-s15-production\anchor
```

Rules enforced by the tool:

- exact 12 frozen segments only;
- source SHA-256 verified before conversion;
- exact Henri/Ulysse anchor SHA-256;
- exact BeltOut revision and seven checkpoint hashes;
- seed = `202609060000 + S15 segment`;
- `n_timesteps=10`;
- no best-of-N;
- no second BeltOut pass;
- no time-stretch;
- no pitch-shift;
- no emotion DSP;
- no network during conversion;
- WebM/Opus fallback decode is in-memory only;
- an existing valid output is verified and skipped, never reconverted;
- a partial or invalid existing output is a fail-closed stop, not permission to retry.

Expected final private status:

`P6_S15_12_OF_12_BELTOUT_MACHINE_PASS`

## 4. Build the converted-only Release payload and staged product patch

```powershell
python tools/p6_s15_post_capture.py stage ^
  --conversion-set C:\voice-lab\p6-s15-production\private\conversion-set.json ^
  --out C:\voice-lab\p6-s15-production\materialization
```

Expected status:

`P6_S15_POST_CAPTURE_STAGE_READY`

The publishable directory contains only:

- `p6-s15-ulysses-converted-v1.tar.xz`
- `p6-converted-index.json`

The archive contains the 12 **converted BeltOut outputs**, never the raw human takes.

The staged product tree contains:

- `series/odyssee/programs/S15.json`
- `series/odyssee/production/provider-packages/P6_ULYSSES_IMMUTABLE_CLIPS_V1.json`
- `series/odyssee/production/ODYSSEE_PRODUCTION_MANIFEST_V1.json`
- `.github/workflows/odyssee-production.yml`

The 12 target lines retain the public Ulysse identity `edge:fr-FR-HenriNeural` and use `immutable-voice-clips-v1` only as `performance_provider`.

## 5. Publication order after machine PASS

Do not apply the staged product patch before the converted-only Release exists.

Create exactly one immutable Release:

- tag: `odyssee-p6-s15-ulysses-converted-v1`
- asset: `p6-s15-ulysses-converted-v1.tar.xz`

Then apply the staged product files in one PR and run Production with S15 forced fresh.

Do not upload:

- the original capture ZIP;
- `raw-selected/*`;
- `frozen-intake.json`;
- `conversion-plan.json`;
- `conversion-reports/*`;
- `conversion-logs/*`;
- any file containing private local raw-audio paths.

## H2

Even after S15 becomes machine-qualified, H2 remains forbidden while P7 is open.

H2 can resume only after both:

- `P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS`;
- `A+B+C+D MACHINE_QUALIFIED`.
