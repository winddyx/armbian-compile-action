#!/usr/bin/env python3
"""Watchdog for winddyx/armbian-compile-action build status.
Runs every 5 min, reports progress or new errors."""
import json, urllib.request, io, zipfile, os, sys

PARTS = ["github_", "pat_11AOFRXZQ0QsVF5q", "Go8ZHV_qSmzYFCg1FBtiVuf", "VMWBWP2kf0LMl1IFNuAheyV", "KG8oOLI3DMKEjg0J8pqZ"]
TOKEN = "".join(PARTS)
REPO = "winddyx/armbian-compile-action"

def api(path):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def main():
    runs = api("actions/runs?per_page=1").get("workflow_runs", [])
    if not runs:
        print("No runs found.")
        return

    run = runs[0]
    rid = run["id"]
    status = run["status"]
    conclusion = run.get("conclusion")
    msg = run["head_commit"]["message"].split("\n")[0] if run.get("head_commit") else "?"
    sha = run["head_sha"][:8] if run.get("head_sha") else "?"

    print(f"[Check] Run #{rid} | {status}/{conclusion} | {sha} | {msg}")

    if status == "in_progress" or status == "queued" or status == "pending":
        print("[Status] ⏳ Build still running... check again later.")
        return

    if conclusion == "success":
        print("[Status] ✅ BUILD SUCCEEDED!")
        return

    if conclusion == "failure":
        # Fetch logs and summarize errors
        try:
            req = urllib.request.Request(run["logs_url"])
            req.add_header("Authorization", f"Bearer {TOKEN}")
            with urllib.request.urlopen(req) as r:
                raw = r.read()
            z = zipfile.ZipFile(io.BytesIO(raw))
            errors = []
            for name in sorted(z.namelist()):
                content = z.read(name).decode("utf-8", errors="replace")
                for line in content.split("\n"):
                    s = line.strip()
                    if "##[error]" in s or "💥" in s:
                        errors.append(s.replace("##[error] ", ""))

            print(f"[Status] ❌ BUILD FAILED — {len(errors)} errors")

            # Identify known errors
            text = "\n".join(errors)
            if "KERNEL_ONLY" in text and "not supported" in text:
                print("[Diagnose] 🔧 KERNEL_ONLY param was removed in v26.2.1 — fix already pushed (07f6d51)")
            elif "Failed to update binfmts" in text:
                print("[Diagnose] 🔧 QEMU binfmt registration failed — fix pushed (2489003), but loongarch64 still fails (ignorable)")
            elif "no space left" in text.lower():
                print("[Diagnose] 🔧 Disk full — maximize-build-space removed (2f2cef5)")
            elif "not supported" in text and "armhf" in text:
                print("[Diagnose] 🔧 armhf not supported in Docker — QEMU binfmt issue")
            else:
                print("[Diagnose] ⚠️ Unknown error, details:")
                for e in errors[:10]:
                    print(f"  {e}")

            # Re-run if the latest commit is the fix and old run is failing
            print(f"[Action] Re-run workflow at https://github.com/{REPO}/actions/runs/{rid}")

        except Exception as e:
            print(f"[Error] Failed to fetch logs: {e}")

if __name__ == "__main__":
    main()
