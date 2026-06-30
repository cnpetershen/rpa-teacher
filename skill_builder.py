import json
import time

class SkillBuilder:

    def build(self, steps, name, reviewed_by="human"):

        return {
            "name": name,
            "version": "2.0",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),

            # human-in-the-loop metadata
            "human_in_the_loop": {
                "enabled": True,
                "reviewed_by": reviewed_by,
                "review_required": True
            },

            "steps": steps
        }

    def save(self, skill, path="skill.json"):

        # enforce human review before save
        if not skill.get("human_in_the_loop", {}).get("enabled"):
            raise Exception("Skill must go through human review layer")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(skill, f, indent=2, ensure_ascii=False)

        print("[Hermes v2] Skill saved with HUMAN REVIEW FLAG")
