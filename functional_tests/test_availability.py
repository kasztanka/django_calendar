from selenium import webdriver

from functional_tests.base import FunctionalTest


class AvailabilityTest(FunctionalTest):
    
    def add_calendar(self, name="Example"):
        self.browser.get(self.live_server_url + '/calendar/new')
        self.fill_input("id_name", name)
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        
    def add_event(self, calendar_pk=1, title="New event"):
        self.browser.get(self.live_server_url + '/event/new/{}'.format(calendar_pk))
        self.fill_input("id_title", title)
        submit = self.browser.find_element_by_id("save_event")
        submit.click()    
    
    def test_user_cannot_see_not_his_calendars_or_events(self):
        self.register()
        self.add_calendar()
        self.add_event()
        logout = self.browser.find_element_by_id("logout")
        logout.click()
        
        self.register(username="Cannot_man")
        
        self.browser.get(self.live_server_url + '/calendar/{}'.format(1))
        page_text = self.browser.find_element_by_tag_name('body'
            ).get_attribute('innerHTML')
        self.assertFalse("Example" in page_text)
        self.assertTrue("You don't have access to this calendar." in page_text)
        
        self.browser.get(self.live_server_url + '/event/{}'.format(1))
        page_text = self.browser.find_element_by_tag_name('body'
            ).get_attribute('innerHTML')
        self.assertFalse("New event" in page_text)
        self.assertTrue("You don't have access to this event." in page_text)
        
        

if __name__ == '__main__':
    unittest.main() 