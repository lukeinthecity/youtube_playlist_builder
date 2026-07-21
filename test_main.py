"""Smoke tests for the pure-Python pieces of main.py.

Run with:  python -m unittest test_main
"""
import json
import os
import tempfile
import unittest

import main


class TestDurationParsing(unittest.TestCase):

    def test_full_duration(self):
        self.assertEqual(main.iso8601_to_seconds("PT1H2M3S"), 3723)

    def test_minutes_seconds(self):
        self.assertEqual(main.iso8601_to_seconds("PT4M20S"), 260)

    def test_seconds_only(self):
        self.assertEqual(main.iso8601_to_seconds("PT45S"), 45)

    def test_empty_duration(self):
        self.assertEqual(main.iso8601_to_seconds("PT"), 0)


class TestVideoValidation(unittest.TestCase):

    def test_accepts_normal_track(self):
        self.assertTrue(main.is_valid_video("Artist - Song", 200, 900, False))

    def test_rejects_over_duration(self):
        self.assertFalse(main.is_valid_video("Artist - Song", 1000, 900, False))

    def test_rejects_blacklisted_word(self):
        self.assertFalse(main.is_valid_video("Artist - Song (Remix)", 200, 900, False))

    def test_rejects_live_by_default(self):
        self.assertFalse(main.is_valid_video("Artist - Song (Live)", 200, 900, False))

    def test_allows_live_when_enabled(self):
        self.assertTrue(main.is_valid_video("Artist - Song (Live)", 200, 900, True))

    def test_live_toggle_does_not_bypass_other_words(self):
        self.assertFalse(main.is_valid_video("Artist - Song (Live Cover)", 200, 900, True))


class TestCache(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        self.addCleanup(os.chdir, self.original_cwd)

    def test_load_missing_cache_returns_empty(self):
        self.assertEqual(main.load_cache(), {})

    def test_save_and_load_roundtrip(self):
        cache = {"Artist - Song": {"video_id": "abc123", "title": "Artist - Song", "duration": 200}}
        main.save_cache(cache)
        self.assertEqual(main.load_cache(), cache)

    def test_cache_file_is_valid_json(self):
        main.save_cache({"a": {"video_id": "x"}})
        with open(main.CACHE_FILE, "r", encoding="utf-8") as f:
            self.assertEqual(json.load(f), {"a": {"video_id": "x"}})


class TestClientSecretImport(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)
        self.addCleanup(os.chdir, self.original_cwd)

    def test_has_client_secret_false_when_missing(self):
        self.assertFalse(main.has_client_secret())

    def test_import_valid_installed_credentials(self):
        source = os.path.join(self.tmpdir.name, "downloaded.json")
        with open(source, "w", encoding="utf-8") as f:
            json.dump({"installed": {"client_id": "x", "client_secret": "y"}}, f)

        main.import_client_secret(source)

        self.assertTrue(main.has_client_secret())
        with open(main.CLIENT_SECRET_FILE, encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["installed"]["client_id"], "x")

    def test_import_accepts_web_credentials(self):
        source = os.path.join(self.tmpdir.name, "downloaded.json")
        with open(source, "w", encoding="utf-8") as f:
            json.dump({"web": {"client_id": "x", "client_secret": "y"}}, f)

        main.import_client_secret(source)

        self.assertTrue(main.has_client_secret())

    def test_import_rejects_unrelated_json(self):
        source = os.path.join(self.tmpdir.name, "not_a_secret.json")
        with open(source, "w", encoding="utf-8") as f:
            json.dump({"foo": "bar"}, f)

        with self.assertRaises(ValueError):
            main.import_client_secret(source)
        self.assertFalse(main.has_client_secret())

    def test_import_rejects_invalid_json(self):
        source = os.path.join(self.tmpdir.name, "broken.json")
        with open(source, "w", encoding="utf-8") as f:
            f.write("{not json")

        with self.assertRaises(json.JSONDecodeError):
            main.import_client_secret(source)


class TestPlaylistFile(unittest.TestCase):

    def test_reads_lines_and_skips_blanks(self):
        with tempfile.NamedTemporaryFile(
                "w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Artist - One\n\n  Artist - Two  \n\n")
            path = f.name
        self.addCleanup(os.unlink, path)
        self.assertEqual(main.read_playlist_file(path), ["Artist - One", "Artist - Two"])


if __name__ == "__main__":
    unittest.main()
