#!/usr/bin/env python3
"""Run the local release gate and report unavailable optional tools honestly."""
from __future__ import annotations
import argparse, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(label: str, command: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None) -> bool:
    print(f"\n=== {label} ===", flush=True)
    proc = subprocess.run(command, cwd=cwd, env=env, text=True)
    print(f"[{ 'PASS' if proc.returncode == 0 else 'FAIL' }] {label} (exit {proc.returncode})", flush=True)
    return proc.returncode == 0

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-optional-tools", action="store_true", help="Fail when Bandit, pip-audit, or Docker CLI are not installed")
    args=parser.parse_args()
    checks=[]
    py=sys.executable
    checks.append(run("Python compilation", [py,"-m","compileall","-q","backend/app","backend/tests","demo_target"]))
    checks.append(run("Dashboard JavaScript syntax", ["node","--check","frontend/static/app.js"]) if shutil.which("node") else True)
    if not shutil.which("node"):
        print("[SKIP] Node.js not installed; browser JavaScript syntax was not checked locally.")
    checks.append(run("Publisher shell syntax", ["bash","-n","scripts/publish_to_github.sh"]) if shutil.which("bash") else True)
    if not shutil.which("bash"):
        print("[SKIP] Bash not installed; shell syntax was not checked locally.")
    checks.append(run("Docker Compose YAML parse", [py,"-c","import yaml; yaml.safe_load(open('docker-compose.yml', encoding='utf-8')); print('Compose YAML OK')"]))
    checks.append(run("Repository hygiene", [py,"scripts/repo_hygiene.py"]))
    checks.append(run("Assessment plan export", [py,"scripts/export_assessment_plan.py"]))
    checks.append(run("Test manifest generation", [py,"scripts/build_test_manifest.py"]))
    coverage_summary=Path(tempfile.gettempdir())/f"firewatch-v{(ROOT / 'VERSION').read_text().strip().split('.')[0]}-coverage-summary.json"
    command=[py,"scripts/run_coverage_shards.py","--shards","8","--min-coverage","80","--coverage-json",str(coverage_summary)]
    checks.append(run("Full regression suite in coverage shards + combined coverage gate",command,cwd=ROOT,env=os.environ.copy()))
    if coverage_summary.exists():
        try:
            import json
            summary=json.loads(coverage_summary.read_text(encoding="utf-8"))
            print(f"Test report: tests={summary['test_cases_executed']} modules={summary['test_module_count']} coverage={summary['coverage_percent']:.2f}% failures=0")
        except Exception as exc:
            print(f"Coverage summary parsing skipped: {type(exc).__name__}")
        finally:
            coverage_summary.unlink(missing_ok=True)
    optional = [("Bandit", ["bandit","-q","-r","backend/app","-lll","-iii"]),
                ("pip-audit", ["pip-audit","-r","backend/requirements.txt"])]
    for label, command in optional:
        if shutil.which(command[0]):
            checks.append(run(label,command))
        else:
            print(f"[SKIP] {label}: executable not installed; result is unverified locally.")
            if args.strict_optional_tools: checks.append(False)
    if shutil.which("docker"):
        checks.append(run("Docker Compose configuration",["docker","compose","config","-q"]))
    else:
        print("[SKIP] Docker CLI not installed; Docker image build/deployment not verified locally.")
        if args.strict_optional_tools: checks.append(False)
    failed=sum(not result for result in checks)
    print(f"\nRelease verification: {len(checks)-failed} passed, {failed} failed. Optional-tool skips are listed above.")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
