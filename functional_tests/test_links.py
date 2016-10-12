import time

from selenium import webdriver

from functional_tests.base import FunctionalTest

class LinksTest(FunctionalTest):

    def visit_timeline(self, period='month'):
        self.browser.get(self.live_server_url + '/{}/2016-05-09'.format(period))

    def test_link_to_profile(self):
        self.register()

        self.browser.get(self.live_server_url)
        profile_link = self.browser.find_element_by_link_text("Hey, mary123!")
        profile_link.click()
        self.assertRegex(self.browser.current_url, '/profile/mary123')

        self.visit_timeline()
        profile_link = self.browser.find_element_by_link_text("Hey, mary123!")
        profile_link.click()
        self.assertRegex(self.browser.current_url, '/profile/mary123')

    def test_links_to_calendars_and_events(self):
        self.register()
        cal_pk = self.add_calendar()
        event_pk = self.add_event(calendar_pk=cal_pk)

        # link to event on timeline
        # wrong date for timeline changes to today date
        self.browser.get(self.live_server_url + '/month/2016-15-09')
        event_link = self.browser.find_element_by_link_text("New event")
        event_link.click()
        self.assertRegex(self.browser.current_url, '/event/{}'.format(event_pk))

        # link to calendar on timeline
        self.browser.get(self.live_server_url + '/month/2016-15-09')
        cal_link = self.browser.find_element_by_link_text("Example")
        cal_link.click()
        self.assertRegex(self.browser.current_url,
            '/calendar/{}'.format(cal_pk))

        # link to event on its calendar
        event_link = self.browser.find_element_by_link_text("New event")
        event_link.click()
        self.assertRegex(self.browser.current_url, '/event/{}'.format(event_pk))

        # link to calendar on its event
        event_link = self.browser.find_element_by_link_text("Example")
        event_link.click()
        self.assertRegex(self.browser.current_url,
            '/calendar/{}'.format(cal_pk))

    def test_links_to_dates_on_timeline(self):
        self.register()

        self.visit_timeline()
        some_day_link = self.browser.find_element_by_link_text("20 May")
        some_day_link.click()
        self.assertRegex(self.browser.current_url, '/month/2016-05-20')

        self.visit_timeline(period='week')
        some_day_link = self.browser.find_element_by_link_text("Thursday 05/12")
        some_day_link.click()
        self.assertRegex(self.browser.current_url, '/week/2016-05-12')

        self.visit_timeline(period='day')
        today_link = self.browser.find_element_by_link_text("Monday 05/09")
        today_link.click()
        self.assertRegex(self.browser.current_url, '/day/2016-05-09')

    def test_links_to_earlier_and_later_dates(self):
        self.register()

        self.visit_timeline()
        link_to_earlier = self.browser.find_element_by_id("earlier")
        link_to_earlier.click()
        self.assertRegex(self.browser.current_url, '/month/2016-04-01')
        link_to_later = self.browser.find_element_by_id("later")
        link_to_later.click()
        self.assertRegex(self.browser.current_url, '/month/2016-05-01')

        self.visit_timeline(period='week')
        link_to_earlier = self.browser.find_element_by_id("earlier")
        link_to_earlier.click()
        self.assertRegex(self.browser.current_url, '/week/2016-05-02')
        link_to_later = self.browser.find_element_by_id("later")
        link_to_later.click()
        self.assertRegex(self.browser.current_url, '/week/2016-05-09')

        self.visit_timeline(period='day')
        link_to_earlier = self.browser.find_element_by_id("earlier")
        link_to_earlier.click()
        self.assertRegex(self.browser.current_url, '/day/2016-05-08')
        link_to_later = self.browser.find_element_by_id("later")
        link_to_later.click()
        self.assertRegex(self.browser.current_url, '/day/2016-05-09')

if __name__ == '__main__':
    unittest.main()
