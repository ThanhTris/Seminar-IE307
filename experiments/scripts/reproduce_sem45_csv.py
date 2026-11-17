#!/usr/bin/env python3
"""Reproduce a pinned draft SEM-45 CSV locally; not a main-run audit or a send."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]

def reproduce(ref):
    ref=subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip()
    def blob(p):return subprocess.check_output(['git','show',f'{ref}:{p}'],cwd=ROOT)
    dest=ROOT/'.local/sem44/producer';dest.mkdir(parents=True,exist_ok=True)
    for name,source in [('analyze.py','experiments/scripts/analyze.py'),('export_logs.py','experiments/scripts/export_logs.py'),('INPUTS.json','docs/evidence/SEM-45/INPUTS.json')]:
        (dest/name).write_bytes(blob(source))
    template=ROOT/'experiments/RUN_MANIFEST_TEMPLATE.json'
    if template.read_bytes()!=blob('experiments/RUN_MANIFEST_TEMPLATE.json'):
        raise ValueError('PINNED_TEMPLATE_MISMATCH')
    # Isolated script process: imports exact pinned producer/validator, not a modified parser.
    sys.path.insert(0,str(dest))
    spec=importlib.util.spec_from_file_location('sem45_pinned',dest/'analyze.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=ROOT;module.contract.TEMPLATE=template
    runs,_=module.load_source_index(dest/'INPUTS.json','pilot')
    analyses=[module.analyze_run(r) for r in runs]
    analyses.sort(key=lambda a:(a['row']['run_id'],a['row']['device_alias']))
    actual=module.csv_text(analyses).encode('utf-8');expected=blob('experiments/results.csv')
    if actual!=expected:raise ValueError('CSV_REPRODUCTION_MISMATCH')
    groups=module.summarize(analyses)
    return {'group_totals':{key:sum(g[key] for g in groups) for key in ('n_input','n_eligible','n_excluded','n_complete')},
            'group_completion_rates_all_null':all(g['completion_rate'] is None for g in groups),
            'ref':ref,'rows':len(analyses),'exact_bytes_equal':True,
            'csv_sha256':hashlib.sha256(expected).hexdigest(),
            'parser_sha256':hashlib.sha256((dest/'analyze.py').read_bytes()).hexdigest(),
            'scope':'UNMERGED_PINNED_PILOT_ONLY_NOT_MAIN','external_calls':False,'template_matches_pinned_ref':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ref',required=True)
    result=reproduce(p.parse_args().ref)
    (ROOT/'docs/evidence/SEM-44/CSV_REPRODUCTION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
