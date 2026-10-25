"""Offline paired-output evaluation. Python 3.9+, standard library, no providers."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import secrets
import sys

HERE = Path(__file__).resolve().parent
ARMS = ("baseline", "idea_man")
DIMENSIONS = ("originality", "usefulness", "method_fit")
PROVENANCE = {"model", "model_version", "settings", "host", "tool_budget",
              "context_sha256", "base_context_sha256", "prompt_sha256", "session_id", "captured_at",
              "intervention", "intervention_revision"}
COMPARE = ("model", "model_version", "settings", "host", "tool_budget", "context_sha256", "base_context_sha256")

def need(value, message):
    if not value:
        raise ValueError(message)

def text(value):
    return isinstance(value, str) and bool(value.strip())

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()

def bad_constant(value):
    raise ValueError("Nonfinite JSON number: " + value)

def finite_float(value):
    number = float(value)
    need(math.isfinite(number), "Nonfinite JSON number: " + value)
    return number

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), parse_constant=bad_constant, parse_float=finite_float,
                      object_pairs_hook=unique_object)

def write_new(path, value):
    path = Path(path)
    payload = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents silently replacing a capture or judgment.
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)

def cases():
    data = read(HERE / "cases.json")
    return {case["id"]: case for case in data["cases"]}

def context_hash(case):
    return digest(case["turns"])

def validate_capture(data, case, allow_fixture=False):
    fields = {"schema_version", "case_id", "arm", "capture_kind", "final_response",
              "artifacts", "provenance"}
    need(isinstance(data, dict) and set(data) == fields, "Invalid capture fields")
    need(type(data["schema_version"]) is int and data["schema_version"] == 1, "Invalid capture schema")
    need(data["case_id"] == case["id"] and data["arm"] in ARMS, "Invalid case or arm")
    need(data["capture_kind"] in {"observed", "test_fixture"}, "Invalid capture kind")
    need(allow_fixture or data["capture_kind"] == "observed", "Test fixtures require --allow-test-fixtures")
    need(isinstance(data["final_response"], str), "Response must be text")
    p = data["provenance"]
    need(isinstance(p, dict) and set(p) == PROVENANCE, "Invalid provenance fields")
    for key in PROVENANCE - {"settings", "tool_budget"}:
        need(text(p[key]), "Missing provenance: " + key)
    need(p["context_sha256"] == context_hash(case), "Conversation context does not match case")
    need(p["intervention"] == ("ordinary_assistant" if data["arm"] == "baseline" else "idea_man"),
         "Arm/intervention mismatch")
    for key in ("prompt_sha256", "context_sha256", "base_context_sha256"):
        need(len(p[key]) == 64 and all(c in "0123456789abcdef" for c in p[key]), "Invalid provenance hash: " + key)
    need(data["arm"] != "baseline" or p["intervention_revision"] == "none", "Baseline revision must be none")
    need(data["arm"] != "idea_man" or p["intervention_revision"] != "none", "Idea-Man source revision required")
    need(isinstance(p["settings"], dict), "Settings must be an object; use explicit unknown values")
    budget = p["tool_budget"]
    need(isinstance(budget, dict) and set(budget) == {"tools", "max_calls"}, "Invalid tool budget")
    need(isinstance(budget["tools"], list) and all(text(x) for x in budget["tools"])
         and len(set(budget["tools"])) == len(budget["tools"]), "Invalid tools")
    need(type(budget["max_calls"]) is int and budget["max_calls"] >= 0, "Invalid call budget")
    need(isinstance(data["artifacts"], list), "Artifacts must be an array")
    names = set()
    for artifact in data["artifacts"]:
        need(isinstance(artifact, dict) and set(artifact) == {"name", "path", "sha256"}, "Invalid artifact")
        need(all(text(artifact[k]) for k in artifact), "Empty artifact field")
        need(artifact["name"] not in names, "Duplicate artifact name")
        names.add(artifact["name"])
        need(Path(artifact["path"]).is_absolute(), "Artifact paths must be absolute")
        need(len(artifact["sha256"]) == 64 and all(c in "0123456789abcdef" for c in artifact["sha256"]),
             "Invalid artifact hash")
    return data

def capture_path(run, case_id, arm):
    return run / "captures" / (case_id + "." + arm + ".json")

def pair(run, case):
    return {arm: validate_capture(read(capture_path(run, case["id"], arm)), case, True) for arm in ARMS}

def artifact_data(artifact):
    path = Path(artifact["path"])
    need(path.is_file(), "Artifact missing: " + artifact["name"])
    need(path.stat().st_size <= 1024 * 1024, "Artifact exceeds 1 MiB review limit")
    body = path.read_bytes()
    need(hashlib.sha256(body).hexdigest() == artifact["sha256"], "Artifact changed: " + artifact["name"])
    return {"name": artifact["name"], "sha256": artifact["sha256"],
            "content": body.decode("utf-8-sig")}

def mechanical(case, capture):
    failures = []
    for artifact in capture["artifacts"]:
        try:
            artifact_data(artifact)
        except (ValueError, OSError, UnicodeError) as exc:
            failures.append(str(exc))
    check = case["check"]
    output = capture["final_response"]
    exact_output = output.strip() if check.get("trim_outer_whitespace") else output
    if check["kind"] == "exact" and exact_output != check["value"]:
        failures.append("Exact output mismatch")
    elif check["kind"] == "json":
        try:
            value = json.loads(output, parse_constant=bad_constant, parse_float=finite_float, object_pairs_hook=unique_object)
            if "keys" in check:
                need(isinstance(value, dict) and set(value) == set(check["keys"]), "JSON object keys mismatch")
                for key, length in check.get("array_lengths", {}).items():
                    need(isinstance(value[key], list) and len(value[key]) == length
                         and all(isinstance(item, str) for item in value[key]), "JSON array contract: " + key)
            if "length" in check:
                need(isinstance(value, list) and len(value) == check["length"], "JSON array length mismatch")
                for item in value:
                    need(isinstance(item, dict) and set(item) == set(check["item_keys"])
                         and all(isinstance(v, str) for v in item.values()), "JSON item contract mismatch")
        except (ValueError, TypeError) as exc:
            failures.append(str(exc))
    elif check["kind"] == "artifact":
        if not any(a["name"] == check["name"] for a in capture["artifacts"]):
            failures.append("Required artifact absent: " + check["name"])
    return failures

def unknown(value):
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or value.strip().lower() in {"unknown", "unspecified"}
    if isinstance(value, dict):
        return not value or any(unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(unknown(v) for v in value)
    return False

def comparability(captures):
    a, b = captures["baseline"]["provenance"], captures["idea_man"]["provenance"]
    mismatches = [key for key in COMPARE if a[key] != b[key]]
    for key in ("model", "model_version", "host"):
        if a[key].strip().lower() in {"unknown", "unspecified"} or b[key].strip().lower() in {"unknown", "unspecified"}:
            mismatches.append("unknown_" + key)
    if not a["settings"] or not b["settings"] or any(unknown(p["settings"]) for p in (a,b)):
        mismatches.append("unknown_settings")
    if a["session_id"] == b["session_id"]:
        mismatches.append("shared_session")
    if a["prompt_sha256"] == b["prompt_sha256"]:
        mismatches.append("identical_full_prompt")
    if unknown(b["intervention_revision"]):
        mismatches.append("unknown_intervention_revision")
    return mismatches

def packet_for(case, captures, mapping, packet_id):
    outputs = {}
    for label, arm in mapping.items():
        cap = captures[arm]
        assets = []
        for artifact in cap["artifacts"]:
            try:
                assets.append(artifact_data(artifact))
            except (ValueError, OSError, UnicodeError) as exc:
                assets.append({"name": artifact["name"], "inspection_error": str(exc)})
        outputs[label] = {"response": cap["final_response"], "artifacts": assets}
    return {"schema_version": 1, "packet_id": packet_id, "case_id": case["id"],
            "synthetic_case": True, "conversation": case["turns"], "rubric": case["rubric"],
            "pair_sha256": digest(captures), "outputs": outputs,
            "review_instruction": "Grade actual outputs, cite evidence, list constraint failures. Do not infer quality from format checks."}

def make_packets(run):
    catalog = cases()
    destination = run / "packets"
    need(not destination.exists(), "Packets already exist; use a new run rather than overwrite")
    pending, keys = [], {}
    for case_id, case in catalog.items():
        if not all(capture_path(run, case_id, arm).is_file() for arm in ARMS):
            continue
        captures = pair(run, case)
        first = secrets.choice(ARMS)
        for order in (1, 2):
            arm_a = first if order == 1 else next(arm for arm in ARMS if arm != first)
            mapping = {"A": arm_a, "B": next(arm for arm in ARMS if arm != arm_a)}
            packet_id = case_id + ".order" + str(order)
            packet = packet_for(case, captures, mapping, packet_id)
            keys[packet_id] = {"mapping": mapping, "packet_sha256": digest(packet)}
            pending.append(packet)
    need(pending, "No complete capture pairs")
    # Compute all packets before creating output; source remains untouched.
    destination.mkdir(parents=True)
    for packet in pending:
        write_new(destination / (packet["packet_id"] + ".json"), packet)
    write_new(run / "private" / "order-key.json", keys)
    return {"packets": len(pending), "reviewer_directory": str(destination),
            "warning": "Do not give reviewers the private order key or capture metadata"}

def validated_packet(run, packet_id):
    need(packet_id in {case_id + ".order" + str(order) for case_id in cases() for order in (1, 2)},
         "Unknown packet ID")
    keys = read(run / "private" / "order-key.json")
    need(packet_id in keys, "Unknown packet")
    key = keys[packet_id]
    need(isinstance(key, dict) and set(key) == {"mapping", "packet_sha256"}, "Invalid packet key")
    need(isinstance(key["mapping"], dict) and set(key["mapping"]) == {"A", "B"}
         and set(key["mapping"].values()) == set(ARMS), "Invalid blinded arm mapping")
    case_id, order = packet_id.rsplit(".order", 1)
    companion = keys.get(case_id + ".order" + ("2" if order == "1" else "1"))
    need(isinstance(companion, dict) and companion.get("mapping") ==
         {"A": key["mapping"]["B"], "B": key["mapping"]["A"]},
         "Companion packet must reverse the blinded order")
    case = cases()[case_id]
    packet = read(run / "packets" / (packet_id + ".json"))
    expected = packet_for(case, pair(run, case), key["mapping"], packet_id)
    need(digest(packet) == key["packet_sha256"] == digest(expected), "Packet or capture changed since blinding")
    return packet, key

def validate_judgment(data, run):
    fields = {"schema_version", "packet_id", "packet_sha256", "reviewer_id", "blinded",
              "independent_of_capture", "scores", "hard_failures", "preference", "rationale"}
    need(isinstance(data, dict) and set(data) == fields, "Invalid judgment fields")
    need(type(data["schema_version"]) is int and data["schema_version"] == 1, "Invalid judgment schema")
    need(text(data["packet_id"]) and text(data["reviewer_id"]), "Missing packet/reviewer")
    need(data["blinded"] is True and data["independent_of_capture"] is True, "Judgment must be independent and blinded")
    packet, key = validated_packet(run, data["packet_id"])
    case_prefix = data["packet_id"].rsplit(".order", 1)[0] + ".order"
    for path in (run / "judgments").glob("*.json"):
        previous = read(path)
        need(isinstance(previous, dict), "Stored judgment must be an object")
        need(not (previous.get("reviewer_id") == data["reviewer_id"]
                  and previous.get("packet_id", "").startswith(case_prefix)
                  and previous.get("packet_id") != data["packet_id"]),
             "Use a different reviewer for the swapped order; repeat exposure is not independent")
    need(data["packet_sha256"] == digest(packet), "Judgment is bound to another packet")
    need(isinstance(data["scores"], dict) and set(data["scores"]) == {"A", "B"}, "Both outputs need scores")
    for label in ("A", "B"):
        scores = data["scores"][label]
        need(isinstance(scores, dict) and set(scores) == set(DIMENSIONS), "Missing grading dimensions")
        for value in scores.values():
            need(isinstance(value, dict) and set(value) == {"score", "evidence"}, "Invalid dimension grade")
            need(value["score"] is None or type(value["score"]) is int and 1 <= value["score"] <= 5, "Score must be 1-5 or null for N/A")
            need(text(value["evidence"]), "Each score/N/A needs output-specific evidence")
    need(isinstance(data["hard_failures"], dict) and set(data["hard_failures"]) == {"A", "B"}, "Both outputs need failure lists")
    need(all(isinstance(v, list) and all(text(x) for x in v) for v in data["hard_failures"].values()), "Invalid hard failures")
    need(data["preference"] in {"A", "B", "tie", "neither"} and text(data["rationale"]), "Preference needs rationale")
    return key

def report(run):
    rows = []
    for case_id, case in cases().items():
        row = {"case_id": case_id, "synthetic_case": True, "status": "not_evaluated",
               "eligible_for_comparison": False, "missing_arms": [], "provenance_mismatches": [],
               "hard_failures": {arm: [] for arm in ARMS}, "judgments": [], "preference": None}
        row["missing_arms"] = [arm for arm in ARMS if not capture_path(run, case_id, arm).is_file()]
        if row["missing_arms"]:
            # A missing comparator must not hide a known failure in the available arm.
            for arm in ARMS:
                if arm not in row["missing_arms"]:
                    try:
                        capture = validate_capture(read(capture_path(run, case_id, arm)), case, True)
                        row["hard_failures"][arm] = mechanical(case, capture)
                    except (ValueError, KeyError, TypeError, OSError) as exc:
                        row["hard_failures"][arm].append("Invalid capture: " + str(exc))
            rows.append(row)
            continue
        try:
            captures = pair(run, case)
            row["provenance_mismatches"] = comparability(captures)
            row["test_fixture"] = any(c["capture_kind"] != "observed" for c in captures.values())
            for arm in ARMS:
                row["hard_failures"][arm] = mechanical(case, captures[arm])
            row["eligible_for_comparison"] = not row["provenance_mismatches"] and not row["test_fixture"]
            for path in sorted((run / "judgments").glob("*.json")):
                judgment = read(path)
                need(isinstance(judgment, dict), "Stored judgment must be an object")
                if not str(judgment.get("packet_id", "")).startswith(case_id + ".order"):
                    continue
                key = validate_judgment(judgment, run)
                preference = judgment["preference"]
                translated = key["mapping"].get(preference, preference)
                row["judgments"].append({"reviewer_id": judgment["reviewer_id"],
                    "packet_id": judgment["packet_id"], "preference": translated,
                    "rationale": judgment["rationale"],
                    "scores": {key["mapping"][label]: value for label, value in judgment["scores"].items()}})
                for label in ("A", "B"):
                    row["hard_failures"][key["mapping"][label]].extend(judgment["hard_failures"][label])
            reviewers = {j["reviewer_id"] for j in row["judgments"]}
            orders = {j["packet_id"].rsplit(".order", 1)[-1] for j in row["judgments"]}
            if row["test_fixture"]:
                row["status"] = "test_fixture"
            elif row["provenance_mismatches"]:
                row["status"] = "provenance_mismatch"
            elif len(reviewers) >= 2 and orders == {"1", "2"}:
                row["status"] = "reviewed"
                votes = {j["preference"] for j in row["judgments"]}
                row["preference"] = next(iter(votes)) if len(votes) == 1 else "mixed"
            elif row["judgments"]:
                row["status"] = "incomplete_review"
        except (ValueError, KeyError, TypeError, OSError) as exc:
            row["status"] = "invalid_evidence"
            row["eligible_for_comparison"] = False
            row["error"] = str(exc)
        rows.append(row)
    return {"schema_version": 1, "cases": rows,
            "counts": {status: sum(r["status"] == status for r in rows) for status in sorted({r["status"] for r in rows})},
            "quality_score": None,
            "limitations": "Synthetic tasks; captures/provenance and human judgments are supplied evidence, not independently authenticated. No native activation or customer demand claim. Hard failures are never averaged away."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("cases")
    template = sub.add_parser("capture-template")
    template.add_argument("--case", required=True, choices=tuple(cases()))
    template.add_argument("--arm", required=True, choices=ARMS)
    template = sub.add_parser("judgment-template")
    template.add_argument("--run", required=True, type=Path)
    template.add_argument("--packet-id", required=True)
    for command in ("import-capture", "import-judgment", "make-packets", "report"):
        cmd = sub.add_parser(command)
        cmd.add_argument("--run", required=True, type=Path)
        if command.startswith("import-"):
            cmd.add_argument("--input", required=True, type=Path)
        if command == "import-capture":
            cmd.add_argument("--allow-test-fixtures", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "cases":
            result = [{"id": c["id"], "context_sha256": context_hash(c), "synthetic": True} for c in cases().values()]
        elif args.command == "capture-template":
            case = cases()[args.case]
            result = {"schema_version": 1, "case_id": args.case, "arm": args.arm,
                      "capture_kind": "observed", "final_response": "", "artifacts": [],
                      "provenance": {key: "" for key in PROVENANCE}}
            result["provenance"].update({"context_sha256": context_hash(case), "settings": {},
                "tool_budget": {"tools": [], "max_calls": 0},
                "intervention": "ordinary_assistant" if args.arm == "baseline" else "idea_man",
                "intervention_revision": "none" if args.arm == "baseline" else ""})
        elif args.command == "judgment-template":
            packet, _ = validated_packet(args.run, args.packet_id)
            result = {"schema_version": 1, "packet_id": args.packet_id,
                "packet_sha256": digest(packet), "reviewer_id": "", "blinded": False,
                "independent_of_capture": False,
                "scores": {label: {dimension: {"score": None, "evidence": ""}
                          for dimension in DIMENSIONS} for label in ("A", "B")},
                "hard_failures": {"A": [], "B": []}, "preference": "", "rationale": ""}
        elif args.command == "import-capture":
            data = read(args.input)
            catalog = cases()
            need(isinstance(data, dict) and data.get("case_id") in catalog, "Unknown case")
            validate_capture(data, catalog[data["case_id"]], args.allow_test_fixtures)
            write_new(capture_path(args.run, data["case_id"], data["arm"]), data)
            result = {"imported": data["case_id"], "arm": data["arm"], "capture_kind": data["capture_kind"]}
        elif args.command == "import-judgment":
            data = read(args.input)
            validate_judgment(data, args.run)
            name = digest({"packet": data["packet_id"], "reviewer": data["reviewer_id"]}) + ".json"
            write_new(args.run / "judgments" / name, data)
            result = {"imported": data["packet_id"], "reviewer": data["reviewer_id"]}
        elif args.command == "make-packets":
            result = make_packets(args.run)
        else:
            result = report(args.run)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
