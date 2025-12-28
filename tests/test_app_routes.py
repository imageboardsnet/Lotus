import unittest
from unittest.mock import patch

import app as app_module
from app import create_app


class AppRouteTests(unittest.TestCase):
    def setUp(self):
        # Stub out network/scheduler work and template rendering.
        self.patcher_update = patch("app.update_ib")
        self.patcher_scheduler = patch("app.ensure_scheduler")
        self.patcher_render_main = patch("app.lotus_render.render_main", return_value="rendered-main")
        self.patcher_render_boards = patch("app.lotus_render.render_boards", return_value="rendered-boards")
        self.patcher_render_search = patch("app.lotus_render.render_search", return_value="rendered-search")
        self.patcher_render_template = patch(
            "app.render_template",
            side_effect=lambda template_name, **kwargs: f"{template_name}:{kwargs.get('content', '')}",
        )

        self.patcher_update.start()
        self.patcher_scheduler.start()
        self.patcher_render_main.start()
        self.mock_render_boards = self.patcher_render_boards.start()
        self.patcher_render_search.start()
        self.patcher_render_template.start()

        for patcher in (
            self.patcher_update,
            self.patcher_scheduler,
            self.patcher_render_main,
            self.patcher_render_boards,
            self.patcher_render_search,
            self.patcher_render_template,
        ):
            self.addCleanup(patcher.stop)

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def _set_state(self, imageboards=None, ibpages=None):
        prev_imageboards = app_module.imageboards
        prev_ibpages = app_module.ibpages
        app_module.imageboards = imageboards or []
        app_module.ibpages = ibpages or []
        self.addCleanup(lambda: self._restore_state(prev_imageboards, prev_ibpages))

    def _restore_state(self, imageboards, ibpages):
        app_module.imageboards = imageboards
        app_module.ibpages = ibpages

    def test_home_returns_content(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"rendered-main", response.data)

    def test_page_redirects_when_out_of_range(self):
        response = self.client.get("/page/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    def test_page_renders_when_available(self):
        self._set_state(
            imageboards=[{"id": 1, "name": "Alpha"}],
            ibpages=["page-one", "page-two"],
        )
        response = self.client.get("/page/2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"rendered-main", response.data)

    def test_search_redirects_without_filters(self):
        response = self.client.post("/search", data={})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    def test_search_renders_results_with_filters(self):
        # Provide a keyword to avoid the redirect and exercise rendering path.
        response = self.client.post("/search", data={"keyword": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"rendered-search", response.data)
        self.assertTrue(self.mock_render_boards.called)

    def test_viewer_uses_requested_board(self):
        boards = [
            {"id": 1, "name": "Alpha"},
            {"id": 2, "name": "Beta"},
        ]
        self._set_state(imageboards=boards)
        response = self.client.get("/viewer?id=2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"viewer.html", response.data)

    def test_lucky_get_renders_closed_box(self):
        self._set_state(imageboards=[{"id": 1}, {"id": 2}])
        response = self.client.get("/lucky")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"lucky.html", response.data)

    @patch("random.sample", return_value=[{"id": 1}, {"id": 2}, {"id": 3}])
    def test_lucky_post_returns_sample(self, mock_sample):
        self._set_state(imageboards=[{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}])
        response = self.client.post("/lucky")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_sample.called)
        self.assertIn(b"lucky.html", response.data)

    def test_sitemap_route(self):
        with patch("app.sitemapper.generate", return_value="sitemap-xml") as mock_generate:
            response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"sitemap-xml", response.data)
        self.assertTrue(mock_generate.called)

    def test_static_files_routes(self):
        with patch("app.send_from_directory", return_value="robots-response") as mock_send:
            response = self.client.get("/robots.txt")
            mock_send.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"robots-response", response.data)

        with patch("app.send_from_directory", return_value="favicon-response") as mock_favicon:
            response = self.client.get("/favicon.ico")
            mock_favicon.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"favicon-response", response.data)


if __name__ == "__main__":
    unittest.main()
