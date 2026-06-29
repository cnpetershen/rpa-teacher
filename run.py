import json

from recorder import RPARecorder
from interpreter import Interpreter
from intent_recognizer import IntentRecognizer
from correction_engine import CorrectionEngine
from skill_builder import SkillBuilder
from review_ui import ReviewUI

SKILL_FILE = "skill.json"

rec = RPARecorder()
rec.start()

input("Press Enter to stop...")
events = rec.stop()

steps = Interpreter().convert(events)

print("[Hermes] Analyzing user intent...")
enriched_steps, intent_info = IntentRecognizer().analyze(steps)
print(f"[Hermes] Intent recognized: {intent_info.get('overall_intent', 'unknown')}")

print("[Hermes] Checking for deviations...")
corrections = CorrectionEngine().correct(enriched_steps, intent_info)
if corrections:
    print(f"[Hermes] Found {len(corrections)} issue(s):")
    for c in corrections:
        print(f"       [{c['severity']}] {c['message']}")
else:
    print("[Hermes] No issues found - clean demonstration!")

with open(SKILL_FILE, "w", encoding="utf-8") as f:
    json.dump({
        "steps": enriched_steps,
        "intent": intent_info,
        "corrections": corrections,
    }, f, indent=2, ensure_ascii=False)

print("[Hermes] Opening review UI...")
ReviewUI()

with open(SKILL_FILE, "r", encoding="utf-8") as f:
    skill = json.load(f)

builder = SkillBuilder()
skill["human_in_the_loop"] = {"enabled": True, "reviewed_by": "human", "review_required": True}
builder.save(skill)

print("[Hermes] v2 skill ready")