import os
import tempfile
import unittest
from unittest.mock import patch

import lotus_utils
from app import should_run_scheduler


class FlagFromCodeTests(unittest.TestCase):
    def test_special_language_code(self):
        self.assertEqual(lotus_utils.flag_from_code("en"), "🇬🇧")

    def test_hyphenated_language_code(self):
        self.assertEqual(lotus_utils.flag_from_code("pt-BR"), "🇧🇷")

    def test_unknown_language_code(self):
        self.assertEqual(lotus_utils.flag_from_code(""), "🏳️")


class GetImageboardsTests(unittest.TestCase):
    @patch("lotus_utils.requests.get")
    @patch("lotus_utils.favicon_exists")
    def test_normalizes_fields_and_adds_favicon(self, mock_favicon_exists, mock_get):
        mock_favicon_exists.side_effect = lambda host: host == "example.com"

        class _Response:
            def raise_for_status(self):
                return None

            def json(self):
                return [
                    {
                        "url": "https://example.com",
                        "language": "en",
                        "software": ["vichan"],
                        "boards": ["a", "b"],
                        "description": "desc",
                    },
                    {
                        "url": "https://nofavicon.test",
                        "language": ["es"],
                        "software": [],
                        "boards": None,
                        "description": "",
                    },
                ]

        mock_get.return_value = _Response()

        boards = lotus_utils.get_imageboards("http://dummy.test")

        self.assertEqual(boards[0]["favicon"], "example.com")
        self.assertEqual(boards[0]["language"], ["en"])
        self.assertEqual(boards[0]["boards"], ["a", "b"])

        self.assertEqual(boards[1]["favicon"], "none")
        self.assertEqual(boards[1]["language"], ["es"])
        self.assertEqual(boards[1]["boards"], [])

    def test_sorting_and_categorization(self):
        items = [
            {"name": "Delta", "boards": [], "description": ""},
            {"name": "Bravo", "boards": ["a"], "description": ""},
            {"name": "Alpha", "boards": ["a"], "description": "desc"},
            {"name": "Charlie", "boards": [], "description": "desc"},
        ]
        ordered = lotus_utils.sort_imageboards(items)
        self.assertEqual([item["name"] for item in ordered], ["Alpha", "Charlie", "Bravo", "Delta"])

    def test_favicon_exists_checks_static_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fav_dir = os.path.join(tmpdir, "static", "favicons")
            os.makedirs(fav_dir)
            existing = os.path.join(fav_dir, "exists.com.ico")
            with open(existing, "wb") as fp:
                fp.write(b"")
            with patch("lotus_utils.os.path.abspath", return_value=tmpdir):
                self.assertTrue(lotus_utils.favicon_exists("exists.com"))
                self.assertFalse(lotus_utils.favicon_exists("missing.com"))


class SearchImageboardsTests(unittest.TestCase):
    def setUp(self):
        self.data = [
            {
                "name": "Alpha",
                "language": ["en"],
                "software": ["vichan"],
                "boards": ["a"],
                "description": "great board",
            },
            {
                "name": "Beta",
                "language": ["es"],
                "software": ["lynxchan"],
                "boards": [],
                "description": "",
            },
            {
                "name": "Gamma",
                "language": ["en"],
                "software": ["lynxchan"],
                "boards": ["x"],
                "description": "",
            },
        ]

    def test_filters_by_language_and_keyword(self):
        results = lotus_utils.search_imageboards(
            self.data, language="en", software=None, keyword="great"
        )
        self.assertEqual([item["name"] for item in results], ["Alpha"])

    def test_filters_has_boards_and_description(self):
        results = lotus_utils.search_imageboards(
            self.data,
            language=None,
            software=None,
            keyword=None,
            has_boards=True,
            has_description=True,
        )
        self.assertEqual([item["name"] for item in results], ["Alpha"])

    def test_sort_modes(self):
        alphabetical = lotus_utils.search_imageboards(
            self.data, language=None, software=None, keyword=None, sort_by="alphabetical"
        )
        self.assertEqual([item["name"] for item in alphabetical], ["Alpha", "Beta", "Gamma"])

        by_board_count = lotus_utils.search_imageboards(
            self.data, language=None, software=None, keyword=None, sort_by="board_count"
        )
        self.assertEqual([item["name"] for item in by_board_count], ["Alpha", "Gamma", "Beta"])


class AvailableFieldsTests(unittest.TestCase):
    def test_collects_unique_languages_and_softwares(self):
        imageboards = [
            {"language": ["en", "es"], "software": "vichan"},
            {"language": ["en", "fr"], "software": "lynxchan"},
            {"language": "fr", "software": ["lynxchan"]},
        ]
        self.assertEqual(lotus_utils.available_languages(imageboards), ["en", "es", "fr"])
        self.assertEqual(lotus_utils.available_softwares(imageboards), ["vichan", "lynxchan"])


class SchedulerFlagTests(unittest.TestCase):
    def test_scheduler_flag_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(should_run_scheduler(default=True))
            self.assertFalse(should_run_scheduler(default=False))

    def test_scheduler_flag_respects_environment(self):
        with patch.dict(os.environ, {"ENABLE_SCHEDULER": "0"}):
            self.assertFalse(should_run_scheduler(default=True))
        with patch.dict(os.environ, {"ENABLE_SCHEDULER": "yes"}):
            self.assertTrue(should_run_scheduler(default=False))

    def test_scheduler_flag_handles_mixed_case_values(self):
        with patch.dict(os.environ, {"ENABLE_SCHEDULER": "False"}):
            self.assertFalse(should_run_scheduler(default=True))
        with patch.dict(os.environ, {"ENABLE_SCHEDULER": "No"}):
            self.assertFalse(should_run_scheduler(default=True))
        with patch.dict(os.environ, {"ENABLE_SCHEDULER": "TRUE"}):
            self.assertTrue(should_run_scheduler(default=False))


if __name__ == "__main__":
    unittest.main()
