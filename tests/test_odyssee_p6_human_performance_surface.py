from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

PAGE = Path("web/reviews/odyssee-p6-human-performance.html")
PAGE_V2 = Path("web/reviews/odyssee-p6-s15-capture-v2.html")
CONTRACT = Path("series/odyssee/production/P6_S15_PRODUCTION_CAPTURE_V1.json")

EXPECTED = {
    112: "Quoi ?",
    114: "On ne peut pas.",
    116: "Tu le sais.",
    118: "On ne peut pas déplacer ce lit.",
    120: "Non.",
    133: "Et si l’arbre a été coupé—",
    135: "Alors tu aurais dû le savoir.",
    140: "Quoi ?",
    142: "Alors pourquoi—",
    151: "L’olivier.",
    153: "Tu savais.",
    158: "Pénélope.",
}

class V2Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slots = []
        self.record_buttons = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("data-seg"):
            self.slots.append(int(a["data-seg"]))
        if tag == "button" and a.get("data-record"):
            self.record_buttons.append(int(a["data-record"]))

class TestOdysseeP6HumanPerformanceSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.v2 = PAGE_V2.read_text(encoding="utf-8")
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.v2_parser = V2Parser(); cls.v2_parser.feed(cls.v2)

    def test_contract_is_exact_12_line_production_capture(self):
        self.assertEqual(self.contract["status"], "P6_S15_PRODUCTION_HUMAN_CAPTURE_PENDING")
        self.assertEqual(self.contract["scope"]["exact_segments"], list(EXPECTED))
        self.assertEqual(self.contract["scope"]["exact_guard_count"], 12)
        self.assertEqual({item["segment"]: item["text"] for item in self.contract["targets"]}, EXPECTED)
        self.assertFalse(self.contract["scope"]["text_change_authorized"])
        self.assertFalse(self.contract["scope"]["global_recast"])

    def test_exact_s15_targets_and_context_are_embedded(self):
        for segment, text in EXPECTED.items():
            self.assertIn(f'"segment":{segment}', self.html)
            self.assertIn(text, self.html)
        for text in (
            "Et fais sortir le lit. Mettez-le dans le couloir. Nous aurons plus de place.",
            "Le lit. Faites-le déplacer.",
            "Sa voix se casse pour la première fois.",
            "Il n’a pas été déplacé.",
            "J’avais besoin d’une chose qui ne puisse pas voyager avec ton histoire.",
            "Ils s’arrêtent encore trop loin pour deux personnes qui se sont attendues vingt ans",
            "Oui.",
        ):
            self.assertIn(text, self.html)

    def test_browser_recording_is_local_first_and_separate_from_probe_storage(self):
        self.assertIn("navigator.mediaDevices.getUserMedia", self.html)
        self.assertIn("MediaRecorder", self.html)
        self.assertIn('indexedDB.open("odyssee-p6-s15-production-recordings-v1"', self.html)
        self.assertIn("stockage local uniquement", self.html.lower())
        self.assertIn("aucun upload automatique", self.html.lower())
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_selection_is_explicit_and_clean_capture_is_required_12_of_12(self):
        self.assertIn("selected:false,cleanConfirmed:false", self.html)
        self.assertIn("Retenir cette prise", self.html)
        self.assertIn("Confirmer écoute propre", self.html)
        self.assertIn('ready+"/12 prêtes"', self.html)
        self.assertIn("les 12 segments doivent avoir une prise retenue et confirmée propre", self.html)
        self.assertIn("selected_before_conversion:true", self.html)
        self.assertIn("clean_capture_confirmed:true", self.html)

    def test_export_contains_only_frozen_selection_plus_integrity_files(self):
        self.assertIn('crypto.subtle.digest("SHA-256"', self.html)
        self.assertIn("recording-manifest.json", self.html)
        self.assertIn("SHA256SUMS.txt", self.html)
        self.assertIn("odyssee-p6-s15-production-selected-takes.zip", self.html)
        self.assertIn("EXACTLY_ONE_SELECTED_TAKE_PER_SEGMENT_BEFORE_ANY_BELTOUT_CONVERSION", self.html)
        self.assertIn("EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE", self.html)
        self.assertIn("constant_level_alignment_only", self.html)

    def test_probe_audio_is_context_only_never_production_source(self):
        self.assertIn("odyssee-h1b-corrective-review-v1/p6-b.mp3", self.html)
        self.assertIn("474c2e41a5d702b2a84524aa3be9a0559ed7378af18d507ac082b666029d64ae", self.html)
        self.assertIn("DRAMATURGIC_REFERENCE_ONLY_NEVER_PRODUCTION_SOURCE", self.html)
        self.assertIn("le probe humain bruité", self.html.lower())
        self.assertIn("production_source:false", self.html)

    def test_public_repo_never_receives_raw_human_voice(self):
        self.assertIn("NEVER_COMMIT_TO_PUBLIC_REPOSITORY", self.html)
        self.assertIn("ne doit jamais être commitée dans le repository public", self.html)

    def test_authoritative_provider_package_is_bound(self):
        self.assertEqual(self.contract["authority"]["provider_package"], "series/odyssee/production/provider-packages/P6_ULYSSES_HUMAN_BELTOUT_PRODUCTION_V1.json")

    def test_v2_has_exactly_12_static_capture_slots_and_buttons(self):
        self.assertEqual(self.v2_parser.slots, list(EXPECTED))
        self.assertEqual(self.v2_parser.record_buttons, list(EXPECTED))
        self.assertNotIn("renderCards", self.v2)
        self.assertNotIn('id="cards"', self.v2)

    def test_v2_is_same_origin_recovery_surface_with_visible_runtime_diagnostics(self):
        self.assertIn("odyssee-p6-s15-production-recordings-v1", self.v2)
        self.assertIn("https://stefm78.github.io", self.v2)
        for token in ("JavaScript :", "Origine :", "Micro/MediaRecorder :", "IndexedDB :", "SHA-256 :"):
            self.assertIn(token, self.v2)
        self.assertIn("navigator.mediaDevices.getUserMedia", self.v2)
        self.assertIn("MediaRecorder", self.v2)
        self.assertIn("crypto.subtle.digest", self.v2)

    def test_v2_enforces_private_intake_duration_bounds_before_export(self):
        self.assertIn("MIN=.20,MAX=20", self.v2)
        self.assertIn("0,20 s et 20,0 s", self.v2)
        self.assertIn("x.duration<MIN||x.duration>MAX", self.v2)

    def test_v2_export_matches_canonical_intake_contract(self):
        for token in (
            "odyssee-p6-s15-production-human-capture-v1",
            "FROZEN_SELECTED_TAKES_READY_FOR_SINGLE_BELTOUT_CONVERSION",
            "EXACTLY_ONE_BELTOUT_CONVERSION_PER_SELECTED_TAKE",
            "constant_level_alignment_only",
            "NEVER_COMMIT_TO_PUBLIC_REPOSITORY",
            "recording-manifest.json",
            "SHA256SUMS.txt",
            "odyssee-p6-s15-production-selected-takes.zip",
        ):
            self.assertIn(token, self.v2)
        self.assertNotIn("fetch(", self.v2)
        self.assertNotIn("XMLHttpRequest", self.v2)

if __name__ == "__main__":
    unittest.main()
