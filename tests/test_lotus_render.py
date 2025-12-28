import unittest
from unittest.mock import patch

import lotus_render


class LotusRenderTests(unittest.TestCase):
    def test_render_main_empty_uses_nothing_template(self):
        with patch("lotus_render.render_search", return_value="search-block"), patch(
            "lotus_render.render_template",
            side_effect=lambda template_name, **kwargs: f"{template_name}:{kwargs.get('content', '')}",
        ):
            result = lotus_render.render_main([], [], [], 0, None, page=0)
            self.assertIn("nothing.html", result)
            self.assertIn("search-block", result)

    def test_render_main_first_page_combines_sections(self):
        with patch("lotus_render.render_search", return_value="search-block"), patch(
            "lotus_render.render_template",
            side_effect=lambda template_name, **kwargs: f"{template_name}:{kwargs.get('content', '')}",
        ):
            result = lotus_render.render_main(["page-0"], ["en"], ["lynxchan"], 1, "now", page=0)
            self.assertIn("stats.html", result)
            self.assertIn("page.html", result)
            self.assertIn("page-0", result)

    def test_render_404_and_nothing_templates(self):
        with patch(
            "lotus_render.render_template",
            side_effect=lambda template_name, **kwargs: f"{template_name}:{kwargs.get('content', '')}",
        ):
            not_found = lotus_render.render_404()
            nothing = lotus_render.render_nothing()
        self.assertIn("404.html", not_found)
        self.assertIn("nothing.html", nothing)


if __name__ == "__main__":
    unittest.main()
