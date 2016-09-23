import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from functional_tests.base import FunctionalTest


class AvailabilityTest(FunctionalTest):
    
    def add_calendar(self, name="Example", can_read=None):
        self.browser.get(self.live_server_url + '/calendar/new')
        self.fill_input("id_name", name)
        if can_read != None:
            inputs = self.browser.find_elements_by_name("can_read")
            for username in can_read:
                for input in inputs:
                    parent = input.find_element_by_xpath('..')
                    if username in parent.text:
                        input.click()
        submit = self.browser.find_element_by_id("save_calendar")
        submit.click()
        return self.browser.current_url[-1]
        
    def add_event(self, calendar_pk=1, title="New event"):
        self.browser.get(self.live_server_url + '/event/new/{}'.format(calendar_pk))
        self.fill_input("id_title", title)
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        return self.browser.current_url[-1]
    
    def logout(self):
        logout = self.browser.find_element_by_id("logout")
        logout.click()
    
    def test_user_cannot_see_not_his_calendars_or_events(self):
        self.register(username="Owner")
        cal_pk = self.add_calendar()
        event_pk = self.add_event(calendar_pk=cal_pk)
        time.sleep(2)
        self.logout()
        
        self.register(username="Cannot_man")
        
        self.browser.get(self.live_server_url + '/calendar/{}'.format(cal_pk))
        page_text = self.get_page_text()
        self.assertFalse("Example" in page_text)
        self.assertTrue("You don't have access to this calendar." in page_text)
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        page_text = self.get_page_text()
        self.assertFalse("New event" in page_text)
        self.assertTrue("You don't have access to this event." in page_text)
        
    def test_can_see_but_not_edit_if_can_read(self):
        self.register(username="Can_man")
        self.logout()
        self.register()
        cal_pk = self.add_calendar(can_read=["Can_man"])
        event_pk = self.add_event(calendar_pk=cal_pk)
        cal_pk2 = self.add_calendar()
        event_pk2 = self.add_event(calendar_pk=cal_pk2)
        self.logout()
        
        self.fill_input('id_username', 'Can_man')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
        
        self.browser.get(self.live_server_url + '/calendar/{}'.format(cal_pk))
        page_text = self.get_page_text()
        self.assertTrue("Example" in page_text)
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("edit_calendar")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("add_event")
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        page_text = self.get_page_text()
        self.assertTrue("New event" in page_text)
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("edit_event")
            
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk2))
        page_text = self.get_page_text()
        self.assertFalse("New event" in page_text)
        

if __name__ == '__main__':
    unittest.main() 