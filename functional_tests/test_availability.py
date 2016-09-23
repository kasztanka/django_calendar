import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from functional_tests.base import FunctionalTest


class AvailabilityTest(FunctionalTest):
        
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
        self.register(username="Owner2")
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
        
    def test_can_edit_events_not_calendars_when_can_modify(self):
        self.register(username="Edit_man")
        self.logout()
        self.register(username="Owner3")
        cal_pk = self.add_calendar(can_modify=["Edit_man"])
        event_pk = self.add_event(calendar_pk=cal_pk)
        cal_pk2 = self.add_calendar()
        event_pk2 = self.add_event(calendar_pk=cal_pk2)
        self.logout()
        
        self.fill_input('id_username', 'Edit_man')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
        
        self.browser.get(self.live_server_url + '/calendar/{}'.format(cal_pk))
        page_text = self.get_page_text()
        self.assertTrue("Example" in page_text)
        # still only owner of calendar can add events or edit it the calendar
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("add_event")
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("edit_calendar")  
            
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        page_text = self.get_page_text()
        self.assertTrue("New event" in page_text)
        edit = self.browser.find_element_by_id("edit_event")
        edit.click()
        
        self.fill_input("id_title", "New title!")
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        time.sleep(2)
        
        page_text = self.get_page_text()
        self.assertTrue("<h2>New title!</h2>" in page_text)
            

if __name__ == '__main__':
    unittest.main() 