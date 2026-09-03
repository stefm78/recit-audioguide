import json
import tempfile
import unittest
from pathlib import Path

from tools import p7_round2_render as p7r2


class P7Round2RenderTests(unittest.TestCase):
    def test_contract_is_final_edge_round(self):
        data=json.loads(p7r2.CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"],"P7_ROUND2_READY_FOR_STREAM3_RENDER")
        self.assertTrue(data["decision"]["no_round3_edge"])
        self.assertEqual(data["decision"]["pass"],"P7_ULYSSE_PERFORMANCE_CONTINUITY_PASS")
        self.assertEqual(data["decision"]["fail"],"P7_ESCALATE_STREAM2_PERFORMANCE_PROVIDER")
        self.assertFalse(data["constraints"]["recasting"])
        self.assertFalse(data["constraints"]["frozen_text_change"])

    def test_candidate_changes_ulysse_per_line_and_forces_french_locale_only(self):
        window={
            "id":"father",
            "ulysse_segments":[1,3],
            "C":{
                "segment_overrides":{
                    "1":{"rate":"-8%","pitch":"-8Hz","volume":"+0%","pause_after_ms":390},
                    "3":{"rate":"-4%","pitch":"-7Hz","volume":"+1%","pause_after_ms":230},
                }
            }
        }
        source={
            "schema_version":6,"id":"source","title":"Source","language":"fr-FR",
            "profile":"speech","sources":[],
            "segments":[
                {"speaker":"ULYSSE","text":"Télémaque.","preset":"odyssee-ulysse"},
                {"speaker":"TÉLÉMAQUE","text":"Qui es-tu ?","preset":"odyssee-telemaque"},
                {"speaker":"ULYSSE","text":"Regarde-moi.","preset":"odyssee-ulysse"},
            ],
        }
        voices={"presets":[
            {"id":"odyssee-ulysse","voice":"fr-FR-HenriNeural","rate":"-4%","pitch":"-10Hz","volume":"+2%","provider":"edge"},
            {"id":"odyssee-telemaque","voice":"fr-FR-RemyMultilingualNeural","rate":"+5%","pitch":"+8Hz","volume":"+2%","provider":"edge"},
        ]}
        validated={"start":1,"end":3,"program":source,"voice_pack":voices}
        program,outvoices=p7r2.build_candidate(window,validated)

        self.assertEqual(outvoices,voices)
        self.assertEqual(program["segments"][0]["rate"],"-8%")
        self.assertEqual(program["segments"][0]["pitch"],"-8Hz")
        self.assertEqual(program["segments"][0]["volume"],"+0%")
        self.assertEqual(program["segments"][0]["pause_after_ms"],390)
        self.assertEqual(program["segments"][2]["rate"],"-4%")
        self.assertEqual(program["segments"][1]["preset"],"odyssee-telemaque")
        self.assertNotIn("rate",program["segments"][1])
        self.assertNotIn("pitch",program["segments"][1])
        self.assertNotIn("volume",program["segments"][1])
        self.assertEqual(program["segments"][1]["language_locale"],"fr-FR")
        self.assertTrue(all(s["language_locale"]=="fr-FR" for s in program["segments"]))
        self.assertEqual(program["acoustic_space"],"dry")

    def test_materialize_has_four_candidates_and_relative_paths(self):
        out=p7r2.ROOT/"generated"/"p7-r2-test"
        try:
            plan=p7r2.materialize(out)
            self.assertEqual(plan["status"],"READY_TO_RENDER_P7_ROUND2")
            self.assertEqual(plan["entry_count"],4)
            self.assertEqual([e["state"] for e in plan["entries"]],list(p7r2.EXPECTED_WINDOWS))
            for entry in plan["entries"]:
                self.assertEqual(entry["variant"],"C")
                self.assertFalse(Path(entry["program_path"]).is_absolute())
                self.assertTrue(entry["program_path"].startswith("generated/"))
        finally:
            if out.exists():
                import shutil
                shutil.rmtree(out)

    def test_collect_requires_four_machine_pass_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); render=root/"renders"; release=root/"release"; entries=[]
            for state in p7r2.EXPECTED_WINDOWS:
                pid=f"odyssee-p7-r2-{state}-c"; d=render/pid; d.mkdir(parents=True)
                (d/"audio.mp3").write_bytes(("audio-"+state).encode())
                (d/"manifest.json").write_text(json.dumps({"id":pid}),encoding="utf-8")
                (d/"qa-report.json").write_text(json.dumps({"status":"PASS"}),encoding="utf-8")
                (d/"transcript.json").write_text(json.dumps({"segments":[{"provider":"edge","language_locale":"fr-FR"}]}),encoding="utf-8")
                entries.append({
                    "state":state,"variant":"C","program_id":pid,
                    "source_program":f"series/{state}.json","source_program_git_blob_sha1":"a"*40,
                    "production_voice_pack":"voices.json","production_voice_pack_sha256":"b"*64,
                    "round1_reference_asset":f"p7-{state}-b.mp3",
                    "output_asset":f"p7-r2-{state}-c.mp3",
                    "qa_asset":f"p7-r2-{state}-c.qa-report.json",
                })
            plan={
                "status":"READY_TO_RENDER_P7_ROUND2","entry_count":4,"engine_ref":p7r2.ENGINE_REF,
                "authority_contract":"series/r2.json","authority_contract_sha256":"c"*64,
                "round1_release_tag":"odyssee-p7-round1-203a196-v1","entries":entries
            }
            pp=root/"plan.json"; pp.write_text(json.dumps(plan),encoding="utf-8")
            index=p7r2.collect(pp,render,release,"d"*40)
            self.assertEqual(index["status"],"machine-ready-p7-round2-review-assets")
            self.assertEqual(index["asset_count"],8)
            self.assertEqual(len(index["assets"]),4)
            self.assertFalse(index["production_programs_mutated"])
            self.assertFalse(index["recasting"])
            self.assertEqual(index["language_locale_override"],"fr-FR")


if __name__=="__main__":
    unittest.main()
