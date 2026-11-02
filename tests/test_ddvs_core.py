import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import ddvs_core as d


class TestDDVS(unittest.TestCase):
    def setUp(self):
        self.store, self.log = {}, []
        self.vid, _ = d.register_document(self.store, 1, "Marksheet", "A", "2026-01-01", "a.pdf", b"orig")

    def v(self, vid, data=None):
        return d.verify_document(self.store, self.log, None, vid, "ID", data)

    def test_t01_verified_by_id(self):      self.assertEqual(self.v(self.vid), "Verified")
    def test_t02_verified_by_file(self):    self.assertEqual(self.v(self.vid, b"orig"), "Verified")
    def test_t03_tampered(self):            self.assertEqual(self.v(self.vid, b"edit"), "Tampered")
    def test_t04_not_found(self):           self.assertEqual(self.v("DDVS-000000000000"), "Not Found")
    def test_t05_malformed(self):           self.assertEqual(self.v("abc"), "Malformed ID")
    def test_t06_revoked(self):
        d.revoke_document(self.store, self.vid); self.assertEqual(self.v(self.vid, b"orig"), "Invalid")
    def test_t07_revoked_even_if_hash_differs(self):
        d.revoke_document(self.store, self.vid); self.assertEqual(self.v(self.vid, b"edit"), "Invalid")
    def test_t08_file_only(self):
        self.assertEqual(d.verify_by_file(self.store, self.log, None, b"orig"), "Verified")
        self.assertEqual(d.verify_by_file(self.store, self.log, None, b"zzz"), "Not Found")
    def test_t09_reject_missing_field(self):
        self.assertIsNone(d.register_document(self.store, 1, "", "A", "2026", "a.pdf", b"x")[0])
    def test_t10_reject_type_and_size(self):
        self.assertIsNone(d.register_document(self.store, 1, "T", "A", "2026", "a.exe", b"x")[0])
        self.assertIsNone(d.register_document(self.store, 1, "T", "A", "2026", "a.pdf", b"x" * (d.MAX_SIZE + 1))[0])
    def test_t11_unique_ids(self):
        ids = {d.register_document(self.store, 1, "T", "A", "2026", "a.pdf", b"x")[0] for _ in range(50)}
        self.assertEqual(len(ids), 50)
    def test_t12_every_attempt_logged(self):
        n = len(self.log); self.v(self.vid); self.v("DDVS-000000000000"); self.assertEqual(len(self.log), n + 2)


if __name__ == "__main__":
    unittest.main()
