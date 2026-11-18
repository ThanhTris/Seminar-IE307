"""Regression coverage for the manifest inventory and portable Git paths."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    'verify_sem44', Path(__file__).resolve().parents[1] / 'verify_sem44.py'
)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class VerifierTests(unittest.TestCase):
    def test_deleted_development_manifest_reports_pinned_path_and_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            index = 'docs/evidence/SEM-43/EVIDENCE_INDEX.json'
            manifest = 'experiments/development/control/manifest.json'
            for path, data in (
                (index, {'sem41_pilot': {'attempts_index': []}}),
                (manifest, {
                    'run_id': 'synthetic-control', 'run_phase': 'development',
                    'data_kind': 'OBSERVED', 'case_id': 'CONTROL', 'mode': 'PUSH',
                    'validity': 'VALID', 'outcome': 'SUCCESS', 'build': {},
                    'event_schema_version': 'legacy-room-v1',
                }),
            ):
                file = repo / path
                file.parent.mkdir(parents=True)
                file.write_text(json.dumps(data), encoding='utf-8')

            def git(*args):
                return subprocess.check_output(
                    ['git', '-c', 'core.autocrlf=false', *args], cwd=repo, text=True
                ).strip()

            git('init', '--quiet')
            git('add', '.')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'Synthetic inventory')
            pinned = git('rev-parse', 'HEAD')
            report_path = repo / 'docs/evidence/SEM-44/VERIFICATION.json'
            args = ['--source-ref', pinned, '--output', str(report_path)]
            with patch.object(verifier, 'ROOT', repo), redirect_stdout(io.StringIO()):
                self.assertEqual(verifier.main(args), 0)
                report = json.loads(report_path.read_text(encoding='utf-8'))
                self.assertEqual(list(report['input_sha256']), [index, manifest])
                self.assertEqual(report['records'][0]['directory'], 'experiments/development/control')

                (repo / manifest).unlink()
                self.assertEqual(verifier.main(args), 2)
                report = json.loads(report_path.read_text(encoding='utf-8'))
                self.assertEqual(report['missing_manifests'], [manifest])
                self.assertEqual(report['snapshot_mismatches'], [manifest])
                self.assertEqual(report['records'], [])
