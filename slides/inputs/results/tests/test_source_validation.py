"""Checkout portability regressions, not experimental runs."""

import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_results import check_source_bytes


class SourceValidationTests(unittest.TestCase):
    blob = b'{"outcome":"TIMEOUT"}\n{"version":23}\n'

    def check(self, raw, blob=None, expected=None):
        blob = self.blob if blob is None else blob
        check_source_bytes(raw, blob, expected or hashlib.sha256(blob).hexdigest(), "capture.json")

    def test_lf_checkout_is_accepted(self):
        self.check(self.blob)

    def test_crlf_checkout_preserves_pinned_hash(self):
        self.check(self.blob.replace(b"\n", b"\r\n"))

    def test_mixed_checkout_line_endings_are_accepted(self):
        self.check(self.blob.replace(b"\n", b"\r\n", 1))

    def test_real_edit_in_crlf_checkout_is_rejected(self):
        raw = self.blob.replace(b"TIMEOUT", b"SUCCESS").replace(b"\n", b"\r\n")
        with self.assertRaisesRegex(ValueError, "INPUT_CHANGED"):
            self.check(raw)

    def test_content_whitespace_and_eof_changes_are_rejected(self):
        for raw in [self.blob.replace(b"}\n", b"} \n"), self.blob + b"\n", self.blob.rstrip(b"\n")]:
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "INPUT_CHANGED"):
                self.check(raw)

    def test_bom_and_bare_carriage_return_are_not_checkout_normalization(self):
        for raw in [b"\xef\xbb\xbf" + self.blob, self.blob.replace(b"\n", b"\r")]:
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "INPUT_CHANGED"):
                self.check(raw)

    def test_changed_git_blob_cannot_match_worktree_without_pinned_hash(self):
        changed = self.blob.replace(b"23", b"24")
        with self.assertRaisesRegex(ValueError, "PINNED_SOURCE_HASH_MISMATCH"):
            self.check(changed, changed, hashlib.sha256(self.blob).hexdigest())


if __name__ == "__main__":
    unittest.main()
