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
        
        select = self.browser.find_element_by_id('id_state')
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
        
    def test_guest_can_change_event_but_only_he_sees_the_changes(self):
        self.register(username="Guest")
        self.logout()
        self.register(username="Owner")
        cal_pk = self.add_calendar()
        event_pk = self.add_event(calendar_pk=cal_pk)
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        button = self.browser.find_element_by_id("add_guest")
        button.click()
        
        select = self.browser.find_element_by_id('id_user')
        for option in select.find_elements_by_tag_name('option'):
            if "Guest" in option.text:
                option.click()
                break
        save = self.browser.find_element_by_id("save_guest")
        save.click()
        time.sleep(1)
        self.logout()
        
        self.fill_input('id_username', 'Guest')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        edit = self.browser.find_element_by_id("edit_event")
        edit.click()
        page_text = self.get_page_text()
        self.assertIn("If you change default settings, you won't be able to "
                + "see changes made by owner of this event.", page_text)
        
        self.fill_input("id_title", "Changed title")
        submit = self.browser.find_element_by_id("save_event")
        submit.click()
        time.sleep(2)
        
        title = self.browser.find_element_by_tag_name("h2")
        self.assertEqual(title.get_attribute('innerHTML'), "Changed title")
        self.logout()
        
        self.fill_input('id_username', 'Owner')
        self.fill_input('id_password', 'JingleBellsBatmanSmells')
        submit = self.browser.find_element_by_tag_name('button')
        submit.click()
        
        self.browser.get(self.live_server_url + '/event/{}'.format(event_pk))
        title = self.browser.find_element_by_tag_name("h2")
        self.assertNotEqual(title.get_attribute('innerHTML'), "Changed title")      
        
    
if __name__ == '__main__':
    unittest.main() 