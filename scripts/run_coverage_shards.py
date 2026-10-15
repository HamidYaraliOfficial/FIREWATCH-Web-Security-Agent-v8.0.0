#!/usr/bin/env python3
"""Run the entire pytest suite in deterministic module shards with combined coverage.

This keeps the complete suite under instrumentation while avoiding unusually long
single-process runs in constrained build environments. Module collection is parsed
from pytest itself and assigned greedily by collected-case count. A non-zero shard
fails the gate; coverage is reported only after all shards succeed.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BACKEND=ROOT/"backend"
LINE_RE=re.compile(r"tests/(test_[^:]+\.py)::")

def run(cmd:list[str], *, cwd:Path, env:dict[str,str]|None=None)->subprocess.CompletedProcess[str]:
    return subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=None,stderr=None)

def collect(py:str, env:dict[str,str])->dict[str,int]:
    proc=subprocess.run([py,"-m","pytest","--collect-only","-q","-o","addopts=","tests"],cwd=BACKEND,env=env,text=True,capture_output=True)
    if proc.returncode:
        sys.stdout.write(proc.stdout); sys.stderr.write(proc.stderr)
        raise RuntimeError("pytest collection failed")
    counts:dict[str,int]={}
    for line in (proc.stdout+"\n"+proc.stderr).splitlines():
        match=LINE_RE.match(line.strip())
        if match:
            name="tests/"+match.group(1); counts[name]=counts.get(name,0)+1
    if not counts:
        raise RuntimeError("could not parse pytest's collected test ids")
    return counts

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shards",type=int,default=5)
    parser.add_argument("--min-coverage",type=float,default=80.0)
    parser.add_argument("--coverage-json",default="",help="Optional path for a JSON coverage summary")
    args=parser.parse_args()
    if args.shards<1 or args.shards>20: parser.error("--shards must be between 1 and 20")
    py=sys.executable
    env=os.environ.copy(); env["PYTHONPATH"]="."
    try: counts=collect(py,env)
    except RuntimeError as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    bins=[[] for _ in range(min(args.shards,len(counts)))]
    weights=[0 for _ in bins]
    for name,count in sorted(counts.items(),key=lambda item:item[1],reverse=True):
        idx=min(range(len(bins)),key=lambda i:weights[i])
        bins[idx].append(name); weights[idx]+=count
    # Start from clean data; subsequent pytest-cov invocations append to one combined dataset.
    subprocess.run([py,"-m","coverage","erase"],cwd=BACKEND,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    total_passed=0; failures=[]
    with tempfile.TemporaryDirectory(prefix="firewatch-v8-coverage-") as td:
        for idx,files in enumerate(bins,1):
            junit=Path(td)/f"junit-{idx}.xml"
            print(f"\n=== Coverage shard {idx}/{len(bins)}: {weights[idx-1]} collected cases across {len(files)} modules ===",flush=True)
            cmd=[py,"-m","pytest",*files,"-q","--cov=app","--cov-append","--cov-report=", "--junitxml",str(junit)]
            result=run(cmd,cwd=BACKEND,env=env)
            if result.returncode:
                failures.append(idx)
            if junit.exists():
                import xml.etree.ElementTree as ET
                try:
                    doc=ET.parse(junit).getroot()
                    suites=[doc] if doc.tag=="testsuite" else list(doc.iter("testsuite"))
                    for suite in suites:
                        total_passed += int(suite.attrib.get("tests","0"))-int(suite.attrib.get("skipped","0"))
                        if int(suite.attrib.get("failures","0")) or int(suite.attrib.get("errors","0")):
                            failures.append(idx)
                except Exception:
                    print(f"Could not parse JUnit summary for shard {idx}",file=sys.stderr)
        if failures:
            print(f"FAIL: one or more coverage shards failed: {sorted(set(failures))}",file=sys.stderr)
            subprocess.run([py,"-m","coverage","erase"],cwd=BACKEND,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return 1
        temp_json=Path(td)/"coverage.json"
        report=subprocess.run([py,"-m","coverage","json","-o",str(temp_json)],cwd=BACKEND,env=env,text=True,capture_output=True)
        if report.returncode:
            print(report.stdout); print(report.stderr,file=sys.stderr); return report.returncode
        coverage=json.loads(temp_json.read_text(encoding="utf-8"))
        percent=float(coverage.get("totals",{}).get("percent_covered",0.0))
        print("\n=== Combined coverage summary ===",flush=True)
        display=run([py,"-m","coverage","report","--fail-under",str(args.min_coverage)],cwd=BACKEND,env=env)
        if display.returncode:
            subprocess.run([py,"-m","coverage","erase"],cwd=BACKEND,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return display.returncode
        if args.coverage_json:
            Path(args.coverage_json).write_text(json.dumps({"test_cases_executed":sum(counts.values()),"test_module_count":len(counts),"shards":len(bins),"coverage_percent":percent,"minimum_percent":args.min_coverage,"failures":0},indent=2)+"\n",encoding="utf-8")
        print(f"RESULT: {sum(counts.values())} collected cases across {len(counts)} modules; {len(bins)} coverage shards; statement coverage {percent:.2f}%; failures: 0")
    subprocess.run([py,"-m","coverage","erase"],cwd=BACKEND,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return 0

if __name__=="__main__": raise SystemExit(main())
