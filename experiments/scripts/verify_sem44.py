#!/usr/bin/env python3
"""Read-only independent evidence/CSV inspection; never certifies an unobserved main run."""
import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[2]
RUN_ROOTS = tuple(PurePosixPath("experiments", folder) for folder in ("runs", "pilots", "development"))
spec = importlib.util.spec_from_file_location('exporter', ROOT/'experiments/scripts/export_logs.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify(draft_ref=None, source_ref="HEAD"):
    source = subprocess.check_output(
        ['git', 'rev-parse', source_ref], cwd=ROOT, text=True
    ).strip()
    tracked = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', '-z', source, '--',
         *(root.as_posix() for root in RUN_ROOTS)],
        cwd=ROOT,
    ).decode('utf-8').split('\0')
    tracked_paths = (PurePosixPath(name) for name in tracked if name)
    expected = {
        path for path in tracked_paths
        if path.name == 'manifest.json' and path.parent.parent in RUN_ROOTS
    }
    present = {
        PurePosixPath(path.relative_to(ROOT).as_posix())
        for root in RUN_ROOTS for path in (ROOT / root).glob('*/manifest.json')
        if path.is_file()
    }
    missing_manifests = sorted(path.as_posix() for path in expected - present)
    unexpected_manifests = sorted(path.as_posix() for path in present - expected)

    files = {}
    def read(p):
        p = PurePosixPath(p)
        data = (ROOT / p).read_bytes()
        files[p.as_posix()] = digest(data)
        return data
    index = json.loads(read('docs/evidence/SEM-43/EVIDENCE_INDEX.json'))
    reference_issues = []
    for attempt in index['sem41_pilot']['attempts_index']:
        for item in attempt['sources']:
            if (not (ROOT / item['path']).is_file() or
                    digest(read(item['path'])) != item['sha256']):
                reference_issues.append(item['path'])
    records = []
    for root in RUN_ROOTS:
        for rel in sorted(path for path in expected & present if path.parent.parent == root):
            manifest = json.loads(read(rel))
            eventpath = rel.parent/'events.jsonl'
            record = {'directory': rel.parent.as_posix(), 'run_id': manifest['run_id'],
                      'phase': manifest['run_phase'], 'data_kind': manifest['data_kind'],
                      'case_id': manifest['case_id'], 'mode': manifest['mode'],
                      'validity': manifest['validity'], 'outcome': manifest['outcome'],
                      'build': manifest['build'], 'issues': [], 'event_format': manifest['event_schema_version']}
            records.append(record)
            if manifest['event_schema_version'] != '2.0.0':
                record['scope'] = 'LEGACY_NOT_CANONICAL'
                continue
            try:
                exporter.validate_manifest(manifest, manifest['run_id'], manifest['device_alias'], fixture=False)
            except (exporter.ExportError, ValueError, TypeError, KeyError):
                record['issues'].append('MANIFEST_SCHEMA_INVALID')
            events = []
            for number, line in enumerate(read(eventpath).decode().splitlines(), 1):
                try:
                    event = exporter.validate_event(exporter.parse_json(line))
                    if any(event[k] != manifest[k] for k in ('run_id', 'device_alias', 'mode')):
                        record['issues'].append(f'EVENT_CONTEXT_LINE_{number}')
                    events.append(event)
                except (exporter.ExportError, ValueError, TypeError, KeyError):
                    record['issues'].append(f'EVENT_SCHEMA_LINE_{number}')
            ids = [e['event_id'] for e in events]
            if len(ids) != len(set(ids)):
                record['issues'].append('DUPLICATE_EVENT_IDS')
            record['counts_all'] = dict(sorted(Counter(e['event_type'] for e in events).items()))
            record['starts_by_source_all'] = dict(Counter(e['source'] for e in events if e['event_type']=='work_started'))
            android=[e for e in events if e['origin']=='ANDROID']
            record['android_boot_known'] = bool(android) and all(e['boot_session_id'] is not None for e in android)
            record['clock_controlled'] = manifest['clock']['controlled']
            record['latency_audit'] = 'NOT_COMPUTED'  # null boot/offset never filled from collector assumptions
            for e in events:
                if e['event_type']=='push_send_skipped' and (e['reason']!='FAULT_INJECTION_SKIP' or e['message_id'] is not None or e['send_attempt_id'] is not None):
                    record['issues'].append('INVALID_SKIP')
                if e['event_type']=='snapshot_applied' and e['data_version']!=e['cached_version']:
                    record['issues'].append('APPLIED_CACHE_MISMATCH')
            # Schema/provenance checks do not re-qualify an INVALID producer run.
            record['scope'] = 'NON_MAIN_STRUCTURAL_REVIEW' if manifest['run_phase']!='main' else 'MAIN_REQUIRES_FULL_AUDIT'
    draft = None
    if draft_ref:
        ref = subprocess.check_output(['git', 'rev-parse', draft_ref], cwd=ROOT, text=True).strip()
        def blob(p):
            return subprocess.check_output(['git', 'show', f'{ref}:{p}'], cwd=ROOT)
        raw = blob('experiments/results.csv')
        inputs = json.loads(blob('docs/evidence/SEM-45/INPUTS.json'))
        rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
        issues = []
        by_id = {r['run_id']: r for r in records}
        keys = [r['run_id'] for r in rows]
        if len(set(keys))!=len(keys): issues.append('DUPLICATE_RUN_ROWS')
        for row in rows:
            r = by_id.get(row['run_id'])
            if not r:
                issues.append({'run': row['run_id'], 'code': 'NO_LOCAL_MANIFEST'})
                continue
            mbytes = read(PurePosixPath(r['directory'])/'manifest.json')
            ebytes = read(PurePosixPath(r['directory'])/'events.jsonl')
            m = json.loads(mbytes)
            for field in ('run_phase','case_id','mode','device_alias','outcome','validity','data_kind'):
                if row.get(field) != str(m[field]): issues.append({'run':row['run_id'],'code':'CSV_METADATA_'+field})
            for field in ('app_commit','server_commit','apk_sha256'):
                if row.get(field) != str(m['build'][field]): issues.append({'run':row['run_id'],'code':'CSV_BUILD_'+field})
            for field, data in [('manifest_sha256',mbytes),('events_sha256',ebytes)]:
                if row.get(field) != digest(data): issues.append({'run':row['run_id'],'code':'CSV_HASH_'+field})
            if row.get('eligible')!='false' and m['validity']!='VALID': issues.append({'run':row['run_id'],'code':'INVALID_ELIGIBLE'})
            for key, value in row.items():
                if key.endswith('_event_count_all'):
                    event_type = key[:-len('_event_count_all')]
                    if value != str(r['counts_all'].get(event_type,0)): issues.append({'run':row['run_id'],'code':'CSV_COUNT_'+key})
            if m['outcome'] in ('TIMEOUT','UNKNOWN','NOT_RUN') and row.get('update_to_applied_ms') not in ('','null',None):
                issues.append({'run':row['run_id'],'code':'TIMEOUT_HAS_LATENCY'})
        missing = [r['run_id'] for r in records if r['directory'].startswith('experiments/pilots/') and r['run_id'] not in keys]
        draft = {'ref': ref, 'csv_sha256': digest(raw), 'input_index_sha256':digest(blob('docs/evidence/SEM-45/INPUTS.json')),
                 'declared_source_commit':inputs['source_commit'],'rows':len(rows),
                 'validity_counts':dict(Counter(r['validity'] for r in rows)), 'outcome_counts':dict(Counter(r['outcome'] for r in rows)),
                 'missing_current_pilot_ids':missing,'issues':issues,'status':'UNMERGED_PINNED_SCOPE_NOT_MAIN',
                 'row_run_ids':keys}
    snapshot_mismatches = sorted(missing_manifests + unexpected_manifests)
    for name, sha in files.items():
        original = subprocess.check_output(['git','show',f'{source}:{name}'],cwd=ROOT)
        if digest(original)!=sha: snapshot_mismatches.append(name)
    main_count=sum(r['phase']=='main' for r in records)
    return {'snapshot_mismatches':snapshot_mismatches,'missing_manifests':missing_manifests,
            'unexpected_manifests':unexpected_manifests,'scope':'SEM44_READ_ONLY_LIMITED_AUDIT','source_commit':source,
            'main_status':'NOT_RUN' if main_count==0 else 'REQUIRES_MAIN_AUDIT','main_runs':main_count,'results_csv_on_main_checkout':(ROOT/'experiments/results.csv').exists(),
            'reference_hash_mismatches':reference_issues,'records':records,'draft_csv':draft,'input_sha256':files}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft-ref',help='Optional already-fetched SEM-45 commit; never fetches or executes producer parser')
    parser.add_argument('--source-ref',default='HEAD',help='Input snapshot commit to verify against Git bytes')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/evidence/SEM-44/VERIFICATION.json')
    args=parser.parse_args(argv)
    result=verify(args.draft_ref,args.source_ref)
    # Only the audit-owned output is written; inputs remain byte-for-byte unchanged.
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'docs/evidence/SEM-44').resolve()):
        parser.error('output must stay in docs/evidence/SEM-44')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'snapshot_mismatches':len(result['snapshot_mismatches']),
                      'missing_manifests':result['missing_manifests'],'unexpected_manifests':result['unexpected_manifests'],
                      'main_status':result['main_status'],'records':len(result['records']),
                      'reference_hash_mismatches':len(result['reference_hash_mismatches']),
                      'structural_issues':sum(len(r['issues']) for r in result['records']),
                      'draft_csv_issues':len(result['draft_csv']['issues']) if result['draft_csv'] else None}))

    problems = (
        result['snapshot_mismatches'] or result['reference_hash_mismatches']
        or any(r['issues'] for r in result['records'])
        or (result['draft_csv'] and result['draft_csv']['issues'])
    )
    return 2 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
