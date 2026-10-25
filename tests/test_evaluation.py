"""Test-only synthetic captures. No provider, human study, or observed output evidence."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "eval/paired_eval.py"
SPEC = importlib.util.spec_from_file_location("paired_eval", SCRIPT)
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)

class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.run = self.folder / "run"
        self.counter = 0

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str,args)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0 if ok else 2, result.stderr)
        return json.loads(result.stdout if ok else result.stderr)

    def capture(self, case_id="exact_edit", arm="baseline"):
        case = EVAL.cases()[case_id]
        return {"schema_version":1, "case_id":case_id, "arm":arm, "capture_kind":"test_fixture",
                "final_response":case["check"].get("value", "TEST FIXTURE ONLY"),
                "artifacts":[], "provenance":{
                    "model":"TEST-MODEL", "model_version":"TEST-VERSION",
                    "settings":{"temperature":0, "max_output_tokens":1000},
                    "host":"TEST-HOST", "tool_budget":{"tools":[], "max_calls":0},
                    "context_sha256":EVAL.context_hash(case), "base_context_sha256":"a"*64,
                    "prompt_sha256":("b" if arm=="baseline" else "d")*64, "session_id":"TEST-"+arm, "captured_at":"TEST-TIMESTAMP",
                    "intervention":"ordinary_assistant" if arm=="baseline" else "idea_man",
                    "intervention_revision":"none" if arm=="baseline" else "TEST-SOURCE"}}

    def input_file(self, data):
        self.counter += 1
        path = self.folder / ("input"+str(self.counter)+".json")
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def import_capture(self, capture, ok=True, allow=True):
        args = ["import-capture","--run",self.run,"--input",self.input_file(capture)]
        if allow:
            args.append("--allow-test-fixtures")
        return self.cli(*args, ok=ok)

    def prepare(self, case_id="exact_edit"):
        for arm in EVAL.ARMS:
            self.import_capture(self.capture(case_id,arm))
        return self.cli("make-packets","--run",self.run)

    def judgment(self, order=1, reviewer="reviewer-1", case_id="exact_edit"):
        packet = EVAL.read(self.run/"packets"/(case_id+".order"+str(order)+".json"))
        return {"schema_version":1,"packet_id":packet["packet_id"],"packet_sha256":EVAL.digest(packet),
                "reviewer_id":reviewer,"blinded":True,"independent_of_capture":True,
                "scores":{label:{d:{"score":None if d=="originality" else 3,
                                   "evidence":"TEST ONLY: output preserves the requested text."}
                                 for d in EVAL.DIMENSIONS} for label in ("A","B")},
                "hard_failures":{"A":[],"B":[]},"preference":"tie",
                "rationale":"TEST FIXTURE ONLY: identical example strings; not a real human judgment."}

    def import_judgment(self, judgment, ok=True):
        return self.cli("import-judgment","--run",self.run,"--input",self.input_file(judgment),ok=ok)

    def test_templates_are_incomplete_and_not_importable(self):
        template=self.cli("capture-template","--case","exact_edit","--arm","baseline")
        self.import_capture(template,ok=False)
        self.prepare()
        template=self.cli("judgment-template","--run",self.run,"--packet-id","exact_edit.order1")
        self.import_judgment(template,ok=False)

    def test_missing_pair_keeps_available_arm_failure(self):
        cap=self.capture();cap["final_response"]="wrong"
        self.import_capture(cap)
        row=self.cli("report","--run",self.run)["cases"][0]
        self.assertEqual(row["status"],"not_evaluated")
        self.assertEqual(row["missing_arms"],["idea_man"])
        self.assertEqual(row["hard_failures"]["baseline"],["Exact output mismatch"])

    def test_order_swap_and_human_failures_survive_report(self):
        cap=self.capture();cap["final_response"]="wrong"
        self.import_capture(cap);self.import_capture(self.capture(arm="idea_man"))
        self.cli("make-packets","--run",self.run)
        p1=EVAL.read(self.run/"packets/exact_edit.order1.json")
        p2=EVAL.read(self.run/"packets/exact_edit.order2.json")
        self.assertEqual(p1["outputs"]["A"],p2["outputs"]["B"])
        self.assertEqual(p1["outputs"]["B"],p2["outputs"]["A"])
        j=self.judgment();j["hard_failures"]["A"]=["TEST ONLY: explicit constraint violated"]
        self.import_judgment(j)
        row=self.cli("report","--run",self.run)["cases"][0]
        self.assertTrue(any("TEST ONLY" in reason for failures in row["hard_failures"].values() for reason in failures))
        self.assertEqual(row["status"],"test_fixture")

    def test_unknown_nested_settings_are_not_comparable(self):
        caps={arm:self.capture(arm=arm) for arm in EVAL.ARMS}
        for cap in caps.values():
            cap["provenance"]["settings"]={"reasoning":{"effort":"UNKNOWN"}}
        self.assertIn("unknown_settings",EVAL.comparability(caps))

    def test_tampered_key_cannot_map_both_outputs_to_one_arm(self):
        self.prepare()
        path=self.run/"private/order-key.json"
        keys=EVAL.read(path)
        keys["exact_edit.order1"]["mapping"]={"A":"baseline","B":"baseline"}
        path.write_text(json.dumps(keys),encoding="utf-8")
        self.import_judgment(self.judgment(),ok=False)

    def test_companion_order_cannot_repeat_same_mapping(self):
        self.prepare()
        path=self.run/"private/order-key.json";keys=EVAL.read(path)
        keys["exact_edit.order2"]["mapping"]=keys["exact_edit.order1"]["mapping"]
        path.write_text(json.dumps(keys),encoding="utf-8")
        self.import_judgment(self.judgment(),ok=False)

    def test_duplicate_json_and_overflow_leave_no_capture(self):
        cap=self.capture()
        body=json.dumps(cap)
        for corrupt in [body.replace('"arm": "baseline"','"arm": "idea_man", "arm": "baseline"'),
                        body.replace('"temperature": 0','"temperature": 1e999')]:
            path=self.folder/"corrupt.json";path.write_text(corrupt,encoding="utf-8")
            self.cli("import-capture","--run",self.run,"--input",path,"--allow-test-fixtures",ok=False)
            self.assertFalse(EVAL.capture_path(self.run,"exact_edit","baseline").exists())
        path=self.folder/"nonfinite.json"
        with self.assertRaises(ValueError):
            EVAL.write_new(path,{"invalid":float("inf")})
        self.assertFalse(path.exists())

    def test_malformed_stored_judgment_is_reported_not_crashed(self):
        self.prepare()
        directory=self.run/"judgments";directory.mkdir()
        (directory/"corrupt.json").write_text("[]",encoding="utf-8")
        row=self.cli("report","--run",self.run)["cases"][0]
        self.assertEqual(row["status"],"invalid_evidence")
        self.assertIn("must be an object",row["error"])

    def test_blank_settings_not_comparable_but_empty_stop_list_valid(self):
        caps={arm:self.capture(arm=arm) for arm in EVAL.ARMS}
        for cap in caps.values():
            cap["provenance"]["settings"]={"temperature":" "}
        self.assertIn("unknown_settings",EVAL.comparability(caps))
        for cap in caps.values():
            cap["provenance"]["settings"]={"temperature":0,"stop":[]}
        self.assertEqual(EVAL.comparability(caps),[])

    def test_identical_treatment_prompt_is_not_comparable(self):
        caps={arm:self.capture(arm=arm) for arm in EVAL.ARMS}
        caps["idea_man"]["provenance"]["prompt_sha256"]=caps["baseline"]["provenance"]["prompt_sha256"]
        self.assertIn("identical_full_prompt",EVAL.comparability(caps))

    def test_sentence_only_check_ignores_transport_whitespace(self):
        cap=self.capture();cap["final_response"]+="\n"
        self.assertEqual(EVAL.mechanical(EVAL.cases()["exact_edit"],cap),[])
        cap["final_response"]+="Extra commentary."
        self.assertEqual(EVAL.mechanical(EVAL.cases()["exact_edit"],cap),["Exact output mismatch"])

    def test_empty_is_not_evaluated(self):
        report = self.cli("report","--run",self.run)
        self.assertEqual(len(report["cases"]),14)
        self.assertEqual(report["counts"],{"not_evaluated":14})
        self.assertIsNone(report["quality_score"])
        self.assertFalse(any(c["eligible_for_comparison"] for c in report["cases"]))

    def test_end_to_end_test_fixture_never_becomes_observed_result(self):
        self.prepare()
        packets = [EVAL.read(p) for p in sorted((self.run/"packets").glob("*.json"))]
        self.assertEqual(len(packets),2)
        self.assertNotIn("provenance",packets[0]["outputs"]["A"])
        self.import_judgment(self.judgment())
        self.import_judgment(self.judgment(2,"reviewer-2"))
        report = self.cli("report","--run",self.run)
        row = next(c for c in report["cases"] if c["case_id"]=="exact_edit")
        self.assertEqual(row["status"],"test_fixture")
        self.assertFalse(row["eligible_for_comparison"])
        self.assertIsNone(row["preference"])
        self.assertEqual(len(row["judgments"]),2)
        self.assertEqual(report["counts"],{"not_evaluated":13,"test_fixture":1})

    def test_import_rejects_unknown_context_fixture_and_overwrite(self):
        cap = self.capture()
        self.import_capture(cap,ok=False,allow=False)
        wrong = copy.deepcopy(cap);wrong["provenance"]["context_sha256"]="c"*64
        self.import_capture(wrong,ok=False)
        self.import_capture(cap)
        before = EVAL.capture_path(self.run,"exact_edit","baseline").read_bytes()
        self.import_capture(cap,ok=False)
        self.assertEqual(before,EVAL.capture_path(self.run,"exact_edit","baseline").read_bytes())

    def test_model_budget_and_context_mismatch_are_visible(self):
        self.import_capture(self.capture())
        other = self.capture(arm="idea_man")
        other["provenance"]["model"]="DIFFERENT"
        other["provenance"]["tool_budget"]["max_calls"]=4
        other["provenance"]["base_context_sha256"]="c"*64
        self.import_capture(other)
        row = self.cli("report","--run",self.run)["cases"][0]
        self.assertEqual(set(row["provenance_mismatches"]),{"model","tool_budget","base_context_sha256"})
        self.assertFalse(row["eligible_for_comparison"])

    def test_bad_output_is_hard_failure_without_quality_score(self):
        cap = self.capture();cap["final_response"]="Here is the correction: wrong"
        self.import_capture(cap);self.import_capture(self.capture(arm="idea_man"))
        row = self.cli("report","--run",self.run)["cases"][0]
        self.assertEqual(row["hard_failures"]["baseline"],["Exact output mismatch"])
        self.assertEqual(row["hard_failures"]["idea_man"],[])
        self.assertIsNone(row["preference"])

    def test_swapped_order_requires_distinct_reviewer_and_evidence(self):
        self.prepare()
        bad = self.judgment();bad["scores"]["A"]["usefulness"]["evidence"]=""
        self.import_judgment(bad,ok=False)
        self.import_judgment(self.judgment())
        self.import_judgment(self.judgment(2),ok=False)
        self.import_judgment(self.judgment(),ok=False)
        self.import_judgment(self.judgment(2,"reviewer-2"))

    def test_tampered_capture_invalidates_bound_judgment(self):
        self.prepare();self.import_judgment(self.judgment())
        path = EVAL.capture_path(self.run,"exact_edit","baseline")
        cap=EVAL.read(path);cap["final_response"]="changed";path.write_text(json.dumps(cap))
        row=self.cli("report","--run",self.run)["cases"][0]
        self.assertEqual(row["status"],"invalid_evidence")
        self.assertIn("changed",row["error"])

    def test_artifact_existence_hash_and_packet_content(self):
        case=EVAL.cases()["structured_handoff"]
        cap=self.capture("structured_handoff")
        self.assertTrue(EVAL.mechanical(case,cap))
        artifact=self.folder/"pilot-plan.md";artifact.write_text("TEST FIXTURE ONLY",encoding="utf-8")
        cap["artifacts"]=[{"name":"pilot-plan.md","path":str(artifact),
                           "sha256":hashlib.sha256(artifact.read_bytes()).hexdigest()}]
        self.assertEqual(EVAL.mechanical(case,cap),[])
        artifact.write_text("changed",encoding="utf-8")
        self.assertIn("Artifact changed",EVAL.mechanical(case,cap)[0])
        artifact.unlink()
        self.assertIn("Artifact missing",EVAL.mechanical(case,cap)[0])

    def test_json_checks_do_not_claim_semantic_quality(self):
        case=EVAL.cases()["mechanism_variation"]
        cap=self.capture("mechanism_variation")
        cap["final_response"]=json.dumps([{"idea":"same","mechanism":"same"}]*3)
        self.assertEqual(EVAL.mechanical(case,cap),[])
        cap["final_response"]="```json\n"+cap["final_response"]+"\n```"
        self.assertTrue(EVAL.mechanical(case,cap))
        cap["final_response"]="NaN"
        self.assertTrue(EVAL.mechanical(case,cap))

if __name__ == "__main__":
    unittest.main()
