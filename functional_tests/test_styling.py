from .base import FunctionalTest


class StylingTest(FunctionalTest):

    def test_styling(self):
        self.browser.get(self.live_server_url)

        page_title = self.browser.find_element_by_id("id_page_title")
        self.assertEqual(
            page_title.value_of_css_property('text-align'),
            'center'
        )
