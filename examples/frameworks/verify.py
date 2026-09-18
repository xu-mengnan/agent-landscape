"""离线检查：语法、预览、配置门槛和本地链接；不执行真实 SDK 或模型。"""
import ast, json, os, re, subprocess, sys, tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG = json.loads((HERE / "catalog.json").read_text(encoding="utf-8"))

def run_preview(path):
    env = {k:v for k,v in os.environ.items() if not k.endswith(("_KEY","_TOKEN","_MODEL","_ID","_URL"))}
    return subprocess.run([sys.executable, str(path)], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=10)

def main():
    errors = []
    demos = sorted(HERE.glob("[0-9][0-9]_*.py"))
    if len(demos) != 13:
        errors.append(f"expected 13 demos, got {len(demos)}")
    if {p.name for p in demos} != {row["file"] for row in CATALOG}:
        errors.append("catalog does not match demo files")

    checks = 0
    for path in demos:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
            checks += 1
        except SyntaxError as exc:
            errors.append(f"{path.name}: syntax error: {exc}")
            continue
        doc = ast.get_docstring(tree) or ""
        if "看点" not in doc:
            errors.append(f"{path.name}: missing feature note")
        checks += 1
        if "# /// script" not in text:
            errors.append(f"{path.name}: missing PEP 723 metadata")
        else:
            block = text.split("# /// script\n",1)[1].split("# ///",1)[0]
            meta = tomllib.loads("\n".join(line.removeprefix("# ") for line in block.splitlines()))
            if meta.get("requires-python") != ">=3.11" or not meta.get("dependencies"):
                errors.append(f"{path.name}: incomplete script metadata")
        checks += 1
        preview = run_preview(path)
        if preview.returncode != 0 or "仅预览说明，不是运行结果" not in preview.stdout:
            errors.append(f"{path.name}: preview mode failed: {preview.stderr.strip()}")
        checks += 1

    for md in HERE.glob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
            if target.startswith(("http://","https://","#")):
                continue
            resolved = (md.parent / target.split("#",1)[0]).resolve()
            if resolved == ROOT / "results/python-demos-validation.json":
                continue
            if not resolved.exists():
                errors.append(f"{md.name}: broken link -> {target}")
            checks += 1

    print(json.dumps({
        "demo_count": len(demos),
        "offline_checks": checks,
        "errors": errors,
        "model_calls": 0,
        "framework_execution": 0
    }, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()
