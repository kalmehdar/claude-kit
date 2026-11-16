"""Self-check for skill-gate.py: python hooks/test_skill_gate.py"""
import json, subprocess, sys, tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "skill-gate.py"


def run(tool, inp, loaded=None):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as t:
        if loaded:
            t.write(json.dumps({"message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": loaded}}]}}) + "\n")
    ev = {"tool_name": tool, "tool_input": inp, "transcript_path": t.name, "cwd": "."}
    out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(ev), capture_output=True, text=True).stdout
    return "deny" in out


assert run("Write", {"file_path": "out/report.pdf"}), "a .pdf write is gated"
assert not run("Write", {"file_path": "out/report.pdf"}, loaded="pdf-ops"), "allowed once pdf-ops is loaded"
assert run("Bash", {"command": "python -c 'import fitz'"}), "PyMuPDF in bash is gated"
assert not run("Write", {"file_path": "src/app.ts"}), "unrelated files pass"
print("skill-gate: 4 checks passed")
