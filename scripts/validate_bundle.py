"""Validate local documentation/data integrity; NOT a security audit or web link crawl."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

def project_files():
    return [p for p in ROOT.rglob('*') if p.is_file()
            and not any(part in {'.git','__pycache__','.venv'} for part in p.relative_to(ROOT).parts)]

def main():
    errors=[]
    sources=json.loads((ROOT/'sources/registry.json').read_text(encoding='utf-8'))
    ids={s['id'] for s in sources}
    if len(ids) != len(sources):
        errors.append('Duplicate source IDs')
    files=project_files()
    checked_links=0
    refs=set()
    for p in files:
        if p.suffix!='.md':
            continue
        text=p.read_text(encoding='utf-8')
        for sid in re.findall(r'\[(S\d{2})\]',text):
            refs.add(sid)
            if sid not in ids:
                errors.append(f'{p.relative_to(ROOT)}: undefined source {sid}')
        for target in re.findall(r'\[[^\]\n]*\]\(([^)]+)\)',text):
            target=target.split(' "',1)[0]
            if target.startswith(('https://','http://','mailto:','#')):
                continue
            local=unquote(target.split('#',1)[0])
            if not local:
                continue
            checked_links+=1
            resolved=(p.parent/local).resolve()
            if not resolved.is_relative_to(ROOT.resolve()):
                errors.append(f'{p.relative_to(ROOT)}: link outside bundle {target}')
            elif not resolved.exists():
                errors.append(f'{p.relative_to(ROOT)}: broken link {target}')
    cases=[json.loads(x) for x in (ROOT/'benchmarks/cases/evaluation.jsonl').read_text(encoding='utf-8').splitlines() if x]
    if len(cases)!=35 or len({r['id'] for r in cases})!=35:
        errors.append('Expected 35 unique evaluation cases')
    if any(r['status']!='DESIGNED_NOT_EXECUTED' for r in cases):
        errors.append('Unexecuted evaluation case incorrectly relabeled')
    results=json.loads((ROOT/'results/offline-results.json').read_text(encoding='utf-8'))
    if results['model_calls']!=0 or results['real_model_trials_completed']!=0:
        errors.append('Evidence boundary mismatch')
    if results['failures'] or results['errors']:
        errors.append('Offline tests did not pass')
    # Preserve reproducibility of non-generated content while allowing reruns to update results.
    manifest_path=ROOT/'sources/content-manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for name, expected in manifest['sha256'].items():
            path=ROOT/name
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
                errors.append(f'Content changed versus release manifest: {name}')
    report=dict(validated_at_utc=datetime.now(timezone.utc).isoformat(),
                local_links_checked=checked_links,source_ids_defined=len(ids),
                source_ids_referenced=len(refs),evaluation_cases=len(cases),
                errors=errors,status='passed' if not errors else 'failed',
                limitations='Local paths and declared evidence only; does not verify live external URLs, model quality, SDK behavior or production security.')
    (ROOT/'results/validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':
    raise SystemExit(main())
