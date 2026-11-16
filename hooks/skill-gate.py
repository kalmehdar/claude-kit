#!/usr/bin/env python3
"""PreToolUse hook: block a matching tool call until this session has loaded the gate's skill.

Gates live in skill-gates.json beside this file. Fails open: any error allows the call and logs
one line to skill-gate.log. SKILL_GATE_OFF=1 turns it off."""
import json, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "skill-gate.log"
PATH_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def draws_chart(text):
    if re.search(r"new Chart\(|\bd3\.(select|scale)|Plotly\.newPlot|echarts\.init", text):
        return True
    if "<svg" not in text:
        return False
    return len(re.findall(r"<(rect|polyline|circle|line)\b", text)) >= 6


def loaded(transcript, skill):
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if '"Skill"' not in line and "<command-name>" not in line:
                    continue
                if f'<command-name>/{skill}</command-name>' in line:
                    return True
                rec = json.loads(line)
                for b in (rec.get("message") or {}).get("content") or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill":
                        name = (b.get("input") or {}).get("skill", "")
                        if name == skill or name.endswith(":" + skill):
                            return True
    except (OSError, ValueError):
        return False
    return False


def repo_dir(cwd, command):
    """The folder a Bash command acts in: the last `cd X` in it, else the session's cwd."""
    cds = re.findall(r"(?:^|[;&|(]|&&)\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", command)
    return str(Path(cwd or ".") / os.path.expanduser(cds[-1].strip("\"'"))) if cds else (cwd or ".")


def diff_touches(gate, where):
    """Does `git diff --name-only <diff_range>` in `where` list a file matching diff_re? Unreadable counts as yes."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", where, "diff", "--name-only", gate["diff_range"]],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return True
    if r.returncode != 0:
        return True
    return any(re.search(gate["diff_re"], f) for f in r.stdout.splitlines())


def matches(gate, tool, inp, cwd=""):
    if tool == "Bash" and gate.get("bash_re") and (gate.get("cwd_re") or gate.get("diff_re")):
        cmd = inp.get("command", "")
        if not re.search(gate["bash_re"], cmd, re.I):
            return False
        where = repo_dir(cwd, cmd)
        if gate.get("cwd_re") and not re.search(gate["cwd_re"], where.replace("\\", "/"), re.I):
            return False
        return not gate.get("diff_re") or diff_touches(gate, where)
    if tool in PATH_TOOLS and gate.get("path_re"):
        p = (inp.get("file_path") or inp.get("notebook_path") or "").replace("\\", "/")
        return bool(re.search(gate["path_re"], p, re.I))
    if tool == "Bash" and gate.get("bash_re"):
        return bool(re.search(gate["bash_re"], inp.get("command", ""), re.I))
    if tool == "Artifact" and gate.get("chart") and inp.get("action", "publish") == "publish" and inp.get("file_path") and not inp.get("asset"):
        try:
            return draws_chart(Path(inp["file_path"]).read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            return False
    return False


def main():
    if os.environ.get("SKILL_GATE_OFF") == "1":
        return
    # Headless SDK runs often cannot load skills; skip them.
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT", "").startswith("sdk"):
        return
    ev = json.load(sys.stdin)
    tool, inp = ev.get("tool_name", ""), ev.get("tool_input") or {}
    gates = json.loads((HERE / "skill-gates.json").read_text(encoding="utf-8"))["gates"]
    for g in gates:
        if matches(g, tool, inp, ev.get("cwd", "")) and not loaded(ev.get("transcript_path", ""), g["skill"]):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Skill gate: load the `{g['skill']}` skill with the Skill tool first, then retry this call. Rule: {g['why']}."}}))
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} deny {g['skill']} {tool}\n")
            return


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # fail open: a broken gate must never stop work
        try:
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} error {type(e).__name__}: {e}\n")
        except OSError:
            pass
    sys.exit(0)
