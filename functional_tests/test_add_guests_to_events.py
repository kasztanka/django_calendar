import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from functional_tests.base import FunctionalTest


class GuestsTest(FunctionalTest):
    
    def test_add_guests_to_events(self):
        for i in range(1, 4):
            self.register(username=("Guest" + str(i)))
            self.logout()
        self.register()
        cal_pk = self.add_calendar()
        event_pk = self.add_event(calendar_pk=cal_pk)
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        button = self.browser.find_element_by_id("add_guest")
        button.click()
        
        select = self.browser.find_element_by_id('id_user')
        for option in select.find_elements_by_tag_name('option'):
            if "Guest2" in option.text:
                option.click()
                break
        save = self.browser.find_element_by_id("save_guest")
        save.click()
        time.sleep(1)
        
        page_text = self.get_page_text()
        self.assertTrue("<li>Guest2: Unknown</li>" in page_text)
        self.logout()
        
        self.fill_input('id_username', 'Guest2')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("add_guests")
        
        select = self.browser.find_element_by_tag_name('id_guest_state')
        for option in select.find_elements_by_tag_name('option'):
            if option.text == "Going":
                option.click()
                break
        save = self.browser.find_element_by_id("save_state")
        save.click()
        time.sleep(1)
        
        page_text = self.get_page_text()
        self.assertTrue("<li>Guest2: Going</li>" in page_text)
        self.logout()
        
        self.fill_input('id_username', 'Guest1')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
        
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_id("save_state")
        

if __name__ == '__main__':
    unittest.main() 